import scrapy
import random
import urllib.parse

from scrapy_playwright.page import PageMethod

class YelpRestaurants(scrapy.Spider):
    name = "yelprestaurants"
    allowed_domains = ["yelp.com"]
    USER_AGENTS = [
 
  *["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    *["Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0"]]*10,
 
  *["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"]*5,
  
  *["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"]*5,

  *["Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"]*5,
  
  *["Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"]*5
]

    OX_SERVER = 'unblock.oxylabs.io:60000'
    OX_USERNAME = 'Yelpshesh_COnI4'
    OX_PASSWORD = 'EmH+6kvWLc5tAR7'

    start_urls = [
        "https://www.yelp.com/search?find_desc=Takeout&find_loc=Manila%2C+Metro+Manila"
    ]
    custom_settings = {

        
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
  
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        
      



        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,
            
      

            "proxy": {
                "server": f"http://{OX_SERVER}",
                "username": OX_USERNAME,
                "password": OX_PASSWORD
            },
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000,
         "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000,
         "PLAYWRIGHT_PAGE_TIMEOUT": 180000,
        "PLAYWRIGHT_PAGE_GOTO_TIMEOUT": 180000,
         "CONCURRENT_REQUESTS": 10,
        "CONCURRENT_REQUESTS_PER_IP": 2
        
    }

    def start_requests(self):
        user_agent = random.choice(self.USER_AGENTS)
        
     
        for url in self.start_urls:
            yield self.create_request(url, user_agent)
        
       
        for i in range(10, 230, 10):
            next_page = f"https://www.yelp.com/search?find_desc=Takeout&find_loc=Manila%2C+Metro+Manila&attrs=RestaurantsTakeOut&start={i}"
            yield self.create_request(next_page, user_agent)

    def create_request(self, url, user_agent):
        return scrapy.Request(
            url=url,
            headers={
                "User-Agent": user_agent,
                "x-oxylabs-geo-location": "United States",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context": "default",  
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "body", timeout=90000),
                    PageMethod(
                        "evaluate",
                        """
                        async () => {
                            await new Promise((resolve) => {
                                let totalHeight = 0;
                                const distance = 500;
                                const timer = setInterval(() => {
                                    const scrollHeight = document.body.scrollHeight;
                                    window.scrollBy(0, distance);
                                    totalHeight += distance;
                                    if (totalHeight >= scrollHeight) {
                                        clearInterval(timer);
                                        resolve();
                                    }
                                }, 1000);
                            });
                        }
                        """,
                    ),
                    PageMethod("wait_for_timeout", 5000),
                ]
            }
        )


    def parse(self, response):
        businesses = response.css("li.y-css-mhg9c5")
       
        for business in businesses:
            raw_yelp_page_url = business.css("h3.y-css-hcgwj4 a::attr(href)").get()
            if raw_yelp_page_url:
                yelp_page_url = response.urljoin(raw_yelp_page_url)

                user_agent = random.choice(self.USER_AGENTS)

                yield scrapy.Request(
                    url=yelp_page_url,
                    callback=self.parse_business_detail,
                    headers={
                        "User-Agent": user_agent,
                        "x-oxylabs-geo-location": "United States"
                    },
                    meta={
                        "playwright": True,
                      
                        "playwright_context_kwargs": {
                            "user_agent": user_agent,
                            "device_scale_factor": 2.5,
                            "is_mobile": True,
                            "has_touch": True,
                            "viewport": {"width": 1366, "height": 768},
                            "ignore_https_errors": True,
                            "proxy": {
                                "server": f"http://{self.OX_SERVER}",
                                "username": self.OX_USERNAME,
                                "password": self.OX_PASSWORD,
                            },
                           
                        },
                        "playwright_page_methods": [
                            PageMethod("add_init_script", script="""
                                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                                window.chrome = { runtime: {} };
                                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                                """),


                         
                        ],
                        "yelp_page_url": yelp_page_url
                    },
                    dont_filter=True,
                )

      
    def parse_business_detail(self, response):

        yelp_page_url = response.meta["yelp_page_url"]
        
        website_url = None
        redirect_url = response.css('a[href*="/biz_redir?url="]::attr(href)').get()

        if redirect_url:
            parsed_url = urllib.parse.urlparse(redirect_url)
            query = urllib.parse.parse_qs(parsed_url.query)
            website_url = query.get("url", [None])[0]  
        if yelp_page_url.startswith("/biz/"):
            business_id = yelp_page_url.split("/biz/")[1].split("?")[0]
        else:
            business_id = None  
        business_name = response.css("h1.y-css-olzveb::text").get()

        claimed_or_not = response.css("a.y-css-1x1elr2::text").get()
        if claimed_or_not == 'Claimed':


            claimed = "yes"
        else:
            claimed = "no"
        category = response.css('[data-testid="BizHeaderCategory"] a::text').get()
        parsed = urllib.parse.urlparse(yelp_page_url)
        if "/biz/" in parsed.path:
            business_id = parsed.path.split("/biz/")[1]
        else:
            business_id = None

        phone_number = response.css("p.y-css-qn4gww::text").get()
        address = response.css("p.y-css-p0gpmm::text").get()
        star_rating= response.css("span.y-css-1ms5w5p::text").get()
        total_reviews = response.css("a.y-css-1x1e1r2::text").get()

        yield {
            "yelp_page_url": yelp_page_url,
            "business_id": business_id,
            "business_name": business_name,
            "claimed": claimed,
            "category": category,
            "website_url": website_url,
            "phone_number": phone_number,
            "address": address,
            "star_rating": star_rating,
            "total_reviews": total_reviews
        }

        
        

        



        