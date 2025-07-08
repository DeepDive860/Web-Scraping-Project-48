import scrapy
from scrapy_playwright.page import PageMethod

class USDEPARTMENTOFTREASURY(scrapy.Spider):
    name = "usdepartmentoftreasury"
    
    OX_USERNAME = "deepdive_0TdFW"
    OX_PASSWORD = "i_NhRAuyg4uRM_J"
    OX_SERVER = "unblock.oxylabs.io:60000"

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,
            "proxy": {
                "server": f"http://{OX_SERVER}",
                "username": OX_USERNAME,
                "password": OX_PASSWORD
            },
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-http2"
            ]
        },
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 60000,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120000,
        "CONCURRENT_REQUESTS_PER_IP": 1,
    }

    def start_requests(self):


        start_urls = [

    {
        "url": "https://home.treasury.gov/about/budget-financial-reporting-planning-and-performance/budget-requestannual-performance-plan-and-reports/budget-in-brief",
        "callback": self.parse_budget_in_brief
    },
    {
        "url": " https://home.treasury.gov/about/budget-financial-reporting-planning-and-performance/budget-requestannual-performance-plan-and-reports/budget-documents-congressional-justification",
        "callback": self.parse_congressional_justification
    },
    {
        "url": "https://home.treasury.gov/about/budget-financial-reporting-planning-and-performance/budget-requestannual-performance-plan-and-reports/summary-of-capital-investments",
        "callback": self.parse_capital_investment
    }
]

        for item in start_urls:
            yield scrapy.Request(
                url=item["url"],
                headers={
                    "x-oxylabs-geo-location": "United States"
                },
                meta={
                    "playwright": True,
                    "playwright_context": "new-context",
                    "playwright_context_kwargs": {
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                        "viewport": {"width": 1366, "height": 768},
                        "ignore_https_errors": True
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=10000),
                  
                    ]
                },
                callback=item["callback"]
            )

    def parse_congressional_justification(self, response):
        self.logger.info(f"Page loaded: {response.url}")

        items = response.css("li.menu-item a::attr(href)").getall()

        for url in items:
            

            if not url:
                continue
            absolute_url = response.urljoin(url)


            print(absolute_url)
            
            if absolute_url.lower().endswith("congressional-justification"):
                yield scrapy.Request(

                    url=absolute_url,
                    meta={
                    "playwright": True,
                    "playwright_context": "new-context",
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=120000),
                        PageMethod("wait_for_function", "document.readyState === 'complete'", timeout=120000),
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    ]
       
                    },
                    callback=self.parse_pdf

                )
           
    def parse_budget_in_brief(self, response):

        items = response.css("li.menu-item a::attr(href)").getall()

        for url in items:
         

            if not url:
                continue
            absolute_url = response.urljoin(url)
            if not absolute_url.lower().endswith("budget-in-brief"):
                continue
            yield scrapy.Request(
                 url=absolute_url,
                    meta={
                    "playwright": True,
                    "playwright_context": "new-context",
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=120000),
                        PageMethod("wait_for_function", "document.readyState === 'complete'", timeout=120000),
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                    ]
       
                    },
                    callback=self.parse_pdf
            )

    def parse_capital_investment(self, response):
            items = response.css("li.menu-item a::attr(href)").getall()

            for url in items:
            

                if not url:
                    continue
                absolute_url = response.urljoin(url)
                if not absolute_url.lower().endswith("capital-investments"):
                    continue
                yield scrapy.Request(
                    url=absolute_url,
                        meta={
                        "playwright": True,
                        "playwright_context": "new-context",
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "body", timeout=120000),
                            PageMethod("wait_for_function", "document.readyState === 'complete'", timeout=120000),
                            PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        ]
        
                        },
                        callback=self.parse_pdf
                )

            
    def parse_pdf(self, response):
        items = response.css("ul li")
        for section in items:
        
            title = section.css("a::text").get()
            raw_url = section.css("a::attr(href)").get()
            full_url = response.urljoin(raw_url)

            if not full_url or not full_url.lower().endswith(".pdf"):
                continue

            yield {
                "title": title,
                "source_url": full_url
            }
                





        