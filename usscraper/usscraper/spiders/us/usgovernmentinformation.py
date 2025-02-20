import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.http import HtmlResponse


class UsGovernmentInformation(scrapy.Spider):

    name = "usinfo"
    allowed_domain = ["govinfo.gov"]
    start_urls = [
        "https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(GPO)%20AND%20publishdate%3Arange(%2C2025-02-19)%20%22%2C%22pageSize%22%3A100%7D",
        "https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(BUDGET)%20AND%20publishdate%3Arange(%2C2025-02-19)%20%22%2C%22pageSize%22%3A100%7D",
        "https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(CZIC)%20AND%20publishdate%3Arange(%2C2025-02-19)%20%22%2C%22pageSize%22%3A100%7D",
        "https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(CFR)%20AND%20publishdate%3Arange(%2C2025-02-19)%20%22%2C%22pageSize%22%3A100%7D",
        "https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(BILLS)%20AND%20publishdate%3Arange(%2C2025-02-19)%20%22%2C%22pageSize%22%3A100%7D",
        "https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(CCAL)%20AND%20publishdate%3Arange(%2C2025-02-19)%20%22%2C%22pageSize%22%3A100%7D",

    ]

    custom_settings = {
        'PLAYWRIGHT_LAUNCH_OPTIONS': {'headless': False},
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 180000,
        "PLAYWRIGHT__DEFAULT_NAVIGATION_TIMEOUT": 180000
    }   


    def start_requests(self):

        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
             
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "li.results-row", timeout=120000, state="attached"),
                    ]
                },
            )

    async def parse(self, response):

        page = response.meta["playwright_page"]

        try:

            items = response.css("li.results-row")
            for item in items:
                document_header = item.css("h4.result-title a p::text").get()
                source_url = response.urljoin(item.css("h4.result-title a::attr(href)").get(" "))
                title = item.css("h5.document-title p::text").get()
                source_pdf = response.urljoin(item.css("a.btn-details[href$='.pdf']::attr(href)").get(" "))


                yield {
                    "Document_Header": document_header,
                    "Source-URl": source_url,
                    "Title": title,
                    "Source_Pdf": source_pdf
                }

            while True:    

                next_button = await page.query_selector('li.page-item:not(.disabled) >> text="Next"')

                if not next_button:
                    break
                await next_button.wait_for_element_state("visible")
                await next_button.click()
                await page.wait_for_load_state("networkidle")
                content = await page.content()

                updated_content = HtmlResponse(
                    url=response.url,
                    body= content,
                    encoding= "utf-8",
                    request= response.request
                )

                async for item in self.parse(updated_content):
                    yield item

        except Exception as e:
            self.logger.warning(f"Playwright error {e}")
        finally:
            await page.close()



      
    

        
        