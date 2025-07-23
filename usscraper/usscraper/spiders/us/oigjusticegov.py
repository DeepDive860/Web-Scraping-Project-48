import scrapy
from scrapy_playwright.page import PageMethod
from usscraper.items import ReportItem

class USDepartmentOfJusticeOfficeOfTheInspectorGeneral(scrapy.Spider):

    '''
        Scraping all Report Fraud, Waste, and Abuse 
    '''

    name = "usdepartmentofjusticeofficeoftheinspectorgeneral"
    start_urls = ["https://oig.justice.gov/reports?keys=&field_publication_date_value=&field_publication_date_value_1=&sort_by=field_publication_date_value&sort_order=DESC&items_per_page=250"]

 

    custom_settings = {

        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,
            "proxy": {
            "server": "http://unblock.oxylabs.io:60000",
            "username":  "Deep11_bNhM6",
            "password": "fZ=MVmm6PvMAtjQ"
        },
       
        },
         'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 120000,
        # "CONCURRENT_REQUESTS": 2,
        # "DOWNLOAD_DELAY": 2,

        "CONCURRENT_REQUESTS_PER_IP": 5
        # "AUTOTHROTTLE_ENABLED": True,
        # "AUTOTHROTTLE_START_DELAY": 2,
        # "AUTOTHROTTLE_MAX_DELAY": 60,
        # "RETRY_HTTP_CODES":[503]
    }

    


    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                headers={
                    "x-oxylabs-geo-location": "United States"
                },
                meta={
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
                        "viewport": {"width": 1366, "height": 768},
                        "ignore_https_errors": True
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=10000),
                        PageMethod("wait_for_selector", "div.views-row", timeout=10000),
                        PageMethod("wait_for_timeout", 100000)
                    ]
                },
                callback=self.parse
            )        
        

    def parse(self, response):

        raw_url = response.css("span.field-content a::attr(href)").getall()
        print("\n")
        print(len(f"SUB URL: {raw_url}"))
        print("\n")

        for url in raw_url:
            if not url:
                continue

            source_url = response.urljoin(url)
        
            yield scrapy.Request(
                url=source_url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context_kwargs": {
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                        "viewport": {"width": 1366, "height": 768},
                        "ignore_https_errors": True
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", 'div.field.field--name-title.field--type-string.field--label-hidden.field__item', timeout=60000 ),
                        PageMethod("wait_for_selector", "a.usa-button.usa-button--outline", timeout=60000)
                    ],
                    "source_url": source_url
                },
                callback=self.parse_main_content
        )
            
        raw_page = response.css("pager__item pager__item--next a::text").get()
        next_page = response.urljoin(raw_page)
        
        if next_page:
            yield scrapy.Request(
                url=next_page,
                headers={
                    "x-oxylabs-geo-location": "United States"
                },
                meta={
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.91 Safari/537.36",
                        "viewport": {"width": 1366, "height": 768},
                        "ignore_https_errors": True
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=10000),
                        PageMethod("wait_for_selector", "div.views-row", timeout=10000),
                        PageMethod("wait_for_timeout", 100000)
                    ]
                },
                callback=self.parse
            )


    async def parse_main_content(self, response):

        page = response.meta["playwright_page"]
        
        source_url = response.meta["source_url"]
        title = response.css("div.field.field--name-title.field--type-string.field--label-hidden.field__item::text").get()
        if not title:
            if page:
                await page.close()
        raw_pdf = response.css("a.usa-button.usa-button--outline::attr(href)").get()
        source_pdf = response.urljoin(raw_pdf)

        if page:
            await page.close()
        yield self.save_data(source_url, title, source_pdf)
        

    def save_data(self, source_url, title, source_pdf):
        item = ReportItem()
        item["source_url"] = source_url
        item["title"] = title
        item["source_pdf"] = source_pdf

        return item


