import scrapy
from scrapy_playwright.page import PageMethod
import random
from usscraper.items import EbayProducts
from datetime import datetime as dt, timezone
import re

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]
class Ebay(scrapy.Spider):

    name = "ebay_spider"
    start_urls = ["https://www.ebay.com/b/Bathroom-Fixtures-Accessories-Supplies/26677/bn_824323"]
    custom_settings = {
         "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,  
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-zygote",
                "--disable-software-rasterizer",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-back-forward-cache",
                "--disable-ipc-flooding-protection",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--enable-features=NetworkService",
                "--hide-scrollbars",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-client-side-phishing-detection",
                "--disable-component-extensions-with-background-pages",
                "--disable-default-apps",
                "--disable-extensions",
                "--mute-audio",
                "--no-experiments",
                "--ignore-certificate-errors",
                "--ignore-certificate-errors-spki-list",
                "--ignore-ssl-errors",
            ],
        },
         "PLAYWRIGHT_CONTEXTS": {
            "default": {
                "user_agent": random.choice(USER_AGENTS),
                "viewport": {"width": random.randint(1200, 1920), "height": random.randint(800, 1080)},
                "locale": "en-US,en;q=0.9",
                "timezone_id": "America/New_York",
                "geolocation": {"longitude": -74.006, "latitude": 40.7128},
                "permissions": ["geolocation"],
                "color_scheme": "light",
                "java_script_enabled": True,
                "extra_http_headers": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                },
            }
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180_000,  
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "CONCURRENT_REQUESTS": 1,
        "RETRY_TIMES": 5, 
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408, 429],
        "COOKIES_ENABLED": True,
        "RANDOMIZE_DOWNLOAD_DELAY": False,
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
        },
        "USER_AGENT": USER_AGENTS[0],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self._seen_product_urls = set()

    def start_requests(self):
        
        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta = {
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
            
                        PageMethod("wait_for_timeout", 2000)
                    ],
                    "playwright_context_kwargs": {
                        "user_agent": random.choice(USER_AGENTS)
                    }
                },
                errback=self.errback
            )

    async def parse(self, response):

        page = response.meta.get("playwright_page")
        try:
                
            category_urls = response.css("div.seo-card a.seo-card__wrapper::attr(href)").getall()

            print(len(category_urls))
            print(category_urls)

            for url in category_urls:

            
                if url:
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_data,
                        meta = {
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", "li.brwrvr__item-card", timeout=120000),
                                PageMethod("wait_for_timeout", 2000)
                            ],
                            "playwright_context_kwargs": {
                                "user_agent": random.choice(USER_AGENTS)
                            }
                        },
                        errback=self.errback
                    )
        finally:
            if page:
                await page.close()
        
    async def parse_data(self, response):
        self.logger.info("Im called")
        page = response.meta["playwright_page"]

        try:
            await page.add_init_script("""
                delete Object.getPrototypeOf(navigator).webdriver;
                window.navigator.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """)
            await page.route("**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,eot,ttf,otf}", lambda route: route.abort())

          
            products = response.css("li.brwrvr__item-card, li.brvrvr__item-card")
            for product in products:
                image_url = product.css("img.brwrvr__item-card__image::attr(src), img.brvrvr__item-card__image::attr(src)").get()
                rating_url = product.css("a.bsig__product-review::attr(href)").get()
                product_url = product.css("span.bsig__title a.bsig__title__wrapper::attr(href)").get()

                if product_url:
                   
                    if product_url in self._seen_product_urls:
                        continue
                    self._seen_product_urls.add(product_url)

                    yield scrapy.Request(
                        url=product_url,
                        callback=self.parse_item,
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "image_url": image_url,
                            "product_url": product_url,
                            "rating_url": rating_url,
                            "playwright_page_methods": [
                                PageMethod("wait_for_load_state", "networkidle"),
                                PageMethod("wait_for_load_state", "domcontentloaded"),
                                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                                
                                PageMethod("wait_for_timeout", 1000),
                            ],
                            "playwright_context_kwargs": {"user_agent": random.choice(USER_AGENTS)},
                        },
                        errback=self.errback,
                    )

        except Exception as e:
            self.logger.error(f"Error parsing page: {e}")
         
        finally:
            await page.close()

   

    async def parse_item(self, response):
        page = response.meta["playwright_page"]
        try:
            item = EbayProducts()
            item["product_name"] = response.css("h1.x-item-title__mainTitle span.ux-textspans.ux-textspans--BOLD::text").get()
            item["product_id"] = response.css("span.x-prp-product-details_value span.ux-textspans::text").get()
            item["current_price"] = response.css("div.x-price-primary span.ux-textspans::text").get()
            item["original_price"] = response.css("span.ux-textspans.ux-textspans--SECONDARY.ux-textspans--STRIKETHROUGH::text").get() \
                                     or response.css("span.ux-textspans.ux-textspans--STRIKETHROUGH::text").get()
            item["discount_percent"] = response.css("span.ux-textspans.ux-textspans--EMPHASIS::text").get() \
                                       or response.css("span.ux-textspans.ux-textspans--SECONDARY::text").get()
            disc_raw = response.css(
            "span.ux-textspans.ux-textspans--EMPHASIS::text, "
            "span.ux-textspans.ux-textspans--SECONDARY::text"
            ).get()
            item["discount_percent"] = None
            if disc_raw:
                m = re.search(r"(\d+)\s*%", disc_raw)
                if m:
                    item["discount_percent"] = f"{m.group(1)}%"
                
          
            item["category"] = " > ".join(response.css("div.seo-breadcrumbs-container.viexpsvc li a.seo-breadcrumb-text span::text").getall())
            item["brand"] = response.css("h2.x-store-information__store-name span.ux-textspans.ux-textspans--BOLD::text").get()
            item["condition"] = response.css("div.x-item-condition-text span.ux-textspans::text").get()
           
            item["units_sold"] = response.css("div#qtyAvailability span.ux-textspans.ux-textspans--BOLD.ux-textspans--EMPHASIS::text").get()
            sold = response.css("div#qtyAvailability span.ux-textspans.ux-textspans--BOLD.ux-textspans--EMPHASIS::text").get()
            sold_text = response.css(
                "div#qtyAvailability span.ux-textspans.ux-textspans--BOLD.ux-textspans--EMPHASIS::text"
            ).get()
            alt_sold = response.css("span.ux-textspans--SECONDARY::text").re_first(r"(\d+)\s+sold")
            item["units_sold"] = sold_text or alt_sold  
                        
            item["number_watching"] = response.css("div.ux-section-icon-with-details__data-item-text span.ux-textspans:not(.ux-textspans--BOLD)::text").get()
            watching_text = response.css(
                "div.ux-section-icon-with-details__data-item-text span.ux-textspans:not(.ux-textspans--BOLD)::text"
            ).get()
            item["number_watching"] = None
            
            if watching_text:
                wt = watching_text.strip()
                if "watch" in wt.lower():
                    n = re.search(r"(\d+)\s*watch", wt.lower())
                    item["number_watching"] = (n.group(1) if n else wt)

            item["product_url"] = response.meta.get("product_url")
            item["image_url"] = response.meta.get("image_url")
            if item.get("current_price") and ("US" in item["current_price"] or "$" in item["current_price"]):
                item["currency"] = "USD"
            item["seller"] = response.css("h2.x-store-information__store-name span.ux-textspans.ux-textspans--BOLD::text").get()
            item["scraped_date"] = dt.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S%z")
            item["stock_availability"] = response.css("div.x-quantity__availability span.ux-textspans.ux-textspans--SECONDARY::text").get()
        

            
            yield item

        except Exception as e:
            self.logger.info(f"Error parsing {e}")
        finally:
            await page.close()

    async def parse_ratings(self, response):
        page = response.meta["playwright_page"]
        item = response.meta.get("item")
        try:
          
            yield item
        finally:
            await page.close()

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Request failed: {failure.value}")
       