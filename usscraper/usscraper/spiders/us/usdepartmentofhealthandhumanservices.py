import scrapy
from scrapy_playwright.page import PageMethod


class US_DEPARTMENT_OF_HEALTH_AND_HUMANSERVICES(scrapy.Spider):
    name = "usdepartmentofhealthandhumanservices"
    start_urls = ["https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/index.html"]
    
    
    OX_USERNAME = "Deeps_HcBbh"
    OX_PASSWORD = "DeepAidive123="
    OX_SERVER = "unblock.oxylabs.io:60000"
    
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 120,  
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,  
            "timeout": 120000  
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000,

    "CONCURRENT_REQUESTS": 16,
    "CONCURRENT_REQUESTS_PER_DOMAIN": 8,
    "CONCURRENT_REQUESTS_PER_IP": 2,
   
    }
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_context": "new-context",
                    "playwright_context_kwargs": {
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
                        "viewport": {"width": 1366, "height": 768},
                        "proxy": {
                            "server": f"http://{self.OX_SERVER}",
                            "username": self.OX_USERNAME,
                            "password": self.OX_PASSWORD
                        },
                        "ignore_https_errors": True  
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=120000),
                        PageMethod("wait_for_function", "document.readyState === 'complete'", timeout=120000),
                        PageMethod("evaluate", "window.scrollBy(0, 500)"),
                        PageMethod("wait_for_timeout", 60000),
                    ],
                    "playwright_include_page": True,
                    "errback": self.errback,
                    
                    "playwright_extra_http_headers": {
                        "x-oxylabs-geo-location": "United States"
                    }
                }
            )
    
    async def parse(self, response):

        page = response.meta["playwright_page"]
        main_urls = response.css("p a::attr(href)").getall()

        pdf_file = response.css("span.usa-tooltip")

        for pdf in pdf_file:
            title = pdf.css("span.usa-tool-tip a::text").get()
            source_url = response.urljoin(pdf.css("span.usa-tooltip a::attr(href)").get())

            full_url = response.urljoin(source_url) 
               

            if not source_url:
                source_url = None

            yield {
                "title": title,
                "source_url": full_url
            }


        for url in main_urls:

            if not url:
                continue

            absolute_url = response.urljoin(url)

            if not absolute_url.startswith("http") or "pdf" in absolute_url.lower():
                continue
   
            else:

                yield scrapy.Request(
                    url=absolute_url,
                      meta={
                        "playwright": True,
                        "playwright_context": "new-context",
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "body", timeout=120000),
                             PageMethod("wait_for_function", "document.readyState === 'complete'", timeout=120000),
                            PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                            PageMethod("wait_for_timeout", 60000),
                        
                        ],
                        "errback": self.errback,
                    },
                    callback=self.parse_sub_url
                    
                )

    async def parse_sub_url(self, response):


        pdf_file = response.css("span.usa-tooltip")

        for pdf in pdf_file:

            title = pdf.css("span.usa-tool-tip a::text").get()
            source_url = response.urljoin(pdf.css("span.usa-tooltip a::attr(href)").get())

            if not source_url.lower().endswith("pdf"):
                continue

                
            if not title:
                title = None
            
            if not source_url:
                source_url = None
            

            yield {
                "title": title,
                "source_url": source_url
            }

        all_sub_urls = []
        second_sub_urls = response.css("li a::attr(href)").getall()
        sub_urls = response.css("p a::attr(href)").getall()
        all_sub_urls.extend(sub_urls)
        all_sub_urls.extend(second_sub_urls)
        

        

        for url in all_sub_urls:
            
            if not url:
                continue
            absolute_url = response.urljoin(url)
            print("\n")
            print(absolute_url)
            print("\n")
            if not absolute_url.startswith("https://www.hhs.gov"):
                continue  

            if absolute_url.lower().endswith(".pdf"):
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
                        PageMethod("wait_for_timeout", 60000),
                        ],
                        "errback": self.errback,
                    },
                    callback=self.parse_sub_url
            )
        
            
    async def extract_documents(self, response):

        body = response.css("p")

        for section in body:

            if section.css("span.usa-tool-tip"):

                title = section.css("span.usa-tool-tip a::text").get()
                if not title:
                    title = None
                source_url = response.urljoin(section.css("span.usa-tooltip a::attr(href)").get())

                if not source_url:
                    source_url = None

                yield {
                    "title": title,
                    "source_url": source_url
                }


    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"Request failed: {failure}")



        