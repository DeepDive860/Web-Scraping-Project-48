import scrapy
from  scrapy_playwright.page import PageMethod

class SimpleSpider(scrapy.Spider):
    name = "simple_treaties"
    start_urls = [
        "https://www.state.gov/2025-tias/?results=30&gotopage=&total_pages=1"
    ]
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120000,
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 120000,
        "CONCURRENT_REQUESTS": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2
    }
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    def start_requests(self):
     
        
        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                headers=self.headers,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("wait_for_selector", "li.collection-result")
                    ]
                },
                callback=self.parse
            )
        
    def parse(self, response):
       
       
       agreeements = response.css("li.collection-result")

       for agreement in agreeements:
           
          
            source_url = agreement.css("a.collection-result__link::attr(href)").get()

            if not agreement and source_url:
               continue

            yield scrapy.Request(
               url=source_url,
               headers=self.headers,
               callback=self.parse_document,
               meta={
                   "playwright": True,
                   "playwright_page_methods": [
                       PageMethod("wait_for_load_state", "networkidle"),
                       
                   ]
               }
           )
            
    def parse_document(self, response):


        agreement_name = response.css("h1.featured-content__headline.stars-above::text").get().strip()

        source_pdf = response.css("a.button.button--outline.button--outline-red.button--corners.button--download::attr(href)").get().strip()


        yield {
            "source_url": response.url,
            "agreement_name": agreement_name,
            "source_pdf": source_pdf
        }







           