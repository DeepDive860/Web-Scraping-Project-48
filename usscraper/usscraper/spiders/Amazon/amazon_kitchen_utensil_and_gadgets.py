import scrapy
import random
import time
from scrapy_playwright.page import PageMethod
from usscraper.spiders.base_spider import BaseSpider
from usscraper.items import AmazonProduct
from datetime import datetime


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; LE2117) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; M2011K2G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; moto g power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0",
    "Mozilla/5.0 (Linux; Android 14; CPH2451) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36 OPR/79.0.0.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/127.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/127.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:127.0) Gecko/127.0 Firefox/127.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:126.0) Gecko/126.0 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36 EdgA/127.0.0.0",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/127.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/127.0 Mobile/15E148 Safari/605.1.15",
]

class Baking_and_Pastry_Utensils(BaseSpider):
    name = "amazon_spider_kitchen_products"
    start_urls = ["https://www.amazon.com/s?k=home+and+kitchen&rh=n%3A1055398&dc&ds=v1%3AjQJIhxMLUki6iMEqe190RSA6XXv0gMJYV994HL%2FUmnI&_encoding=UTF8&content-id=amzn1.sym.5d0c6367-faf2-4a6d-abef-5547b5a67981&pd_rd_r=0a319f8b-dd77-4438-ae6b-4f3b12d07e0c&pd_rd_w=lU7Tf&pd_rd_wg=acUHS&pf_rd_p=5d0c6367-faf2-4a6d-abef-5547b5a67981&pf_rd_r=8VKTKVWCDGFAP6ZH36SZ&qid=1757307833&rnid=2941120011&ref=sr_nr_n_1"]
    
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
       "CONCURRENT_REQUESTS": 5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,

     
        "DOWNLOAD_DELAY": 2.5,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 3.0,
        "AUTOTHROTTLE_MAX_DELAY": 10.0,

        "RETRY_TIMES": 5,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408, 429],
        "COOKIES_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
        },
        "USER_AGENT": USER_AGENTS[0],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seen_asins = set()


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.sg-col-inner", timeout=120000),  
                        PageMethod("wait_for_timeout", 2000),
                    ],
                    "playwright_context_kwargs": {
                        "user_agent": random.choice(USER_AGENTS),
                    },
                },
                errback=self.errback,
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        
        try:
        
            await page.add_init_script("""
                delete Object.getPrototypeOf(navigator).webdriver;
                window.navigator.chrome = {
                    runtime: {},
                };
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            """)
            await page.route("**/*.{png,jpg,jpeg,gif,svg,webp,woff,woff2,eot,ttf,otf}", lambda route: route.abort())

          
            results = response.css("div.s-main-slot div.s-result-item[data-component-type='s-search-result'][data-asin]")
            for res in results:
                asin = (res.attrib.get("data-asin") or "").strip()
                if not asin:
                    continue

             
                sold_last_month = res.css("span.a-size-base.a-color-secondary::text").get()

                product_url = response.urljoin(f"/dp/{asin}")  
                yield scrapy.Request(
                    url=product_url,
                    callback=self.parse_item,
                    priority=10,  
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "sold_last_month": sold_last_month,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "domcontentloaded"),
                           
                        ],
                        "playwright_context_kwargs": {"user_agent": random.choice(USER_AGENTS)},
                    },
                    errback=self.errback,
                )



          
            next_page = response.css('.s-pagination-next::attr(href)').get()
            if next_page:
            
                
                yield scrapy.Request(
                    url=response.urljoin(next_page),
                    callback=self.parse,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "div.sg-col-inner", timeout=60000),
                            PageMethod("wait_for_timeout", 2000),
                        ],
                        "playwright_context_kwargs": {
                            "user_agent": random.choice(USER_AGENTS),
                        },
                    },
                    errback=self.errback,
                )
            
        except Exception as e:
            self.logger.error(f"Error parsing page: {e}")
           
            yield response.request.replace(dont_filter=True)
        finally:
            await page.close()



    async def parse_item(self, response):

        self.logger.info("Im called")
        page = response.meta["playwright_page"]
        try:

            item = AmazonProduct()

            item["product_name"] = response.css("span#productTitle.a-size-large.product-title-word-break::text").get().strip()
            price = response.css("span.a-price-whole::text").get()
            fraction = response.css("span.a-price-fraction::text").get()
            item["current_price"] = f"{price}.{fraction}"
            item["discount_percent"] = response.css("span.a-size-large.a-color-price.savingPriceOverride.aok-align-center.reinventPriceSavingsPercentageMargin.savingsPercentage::text").get()
            item["original_price"] = response.css("span.a-price.a-text-price span.a-offscreen::text").get()
            item["ratings"] =response.css("div#averageCustomerReviews span.a-size-base.a-color-base::text").get()
            item["review_count"] =  response.css("span#acrCustomerReviewText::text").get().strip()
            item["category"] = " > ".join(response.css("ul.a-unordered-list.a-horizontal.a-size-small li a.a-link-normal.a-color-tertiary::text").getall())

            item["image_url"] = response.css("div.imgTagWrapper img.a-dynamic-image::attr(src)").get()
            item["brand"] =  response.css("tr.po-brand td.a-span9 span::text").get().strip()
            avail = (
            response.css('#availability .a-color-success::text, #availability .a-color-state::text').get()
        or response.css('#availabilityInsideBuyBox_feature_div .a-color-success::text, #availabilityInsideBuyBox_feature_div .a-color-state::text').get()
    )
            item["stock_availability"] = avail.strip() if avail else None
            item["manufacturer"] =  response.xpath("normalize-space(//table[@id='productDetails_detailBullets_sections1']""//th[normalize-space()='Manufacturer']/following-sibling::td[1])").get()

            item["sold_by"] = response.css("div.offer-display-feature-text.a-spacing-none.odf-truncation-popover.aok-inline-block a.a-size-small.a-link-normal.offer-display-feature-text-message::text").get()
            item["product_url"] = response.url
            item["currency"] = "USD"
            item["scraped_date"] =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item["sold_last_month"] = response.meta.get("sold_last_month")

            yield item
        except Exception as e:
            self.logger.info(f"Error parsing the page {e}")
        finally:
            await page.close()
    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        
     
        self.logger.error(f"Request failed: {failure.value}")
        
      
        if failure.request.meta.get('retry_times', 0) < self.custom_settings.get('RETRY_TIMES', 2):
            retry_request = failure.request.copy()
            retry_request.meta['retry_times'] = retry_request.meta.get('retry_times', 0) + 1
            yield retry_request