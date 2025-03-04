import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.http import HtmlResponse


class USCodeOfFederalRegulations(scrapy.Spider):


    name = "uscodeoffederalregulations"
    allowed_domains = ["govinfo.gov"]
    start_urls = ["https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(CFR)%20AND%20publishdate%3Arange(%2C2025-03-04)%20%22%2C%22pageSize%22%3A100%7D"]

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000
    }

    def start_requests(self):

        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
               
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods":
                    [
                        PageMethod("wait_for_selector", "li.results-row", timeout=180000, state="visible")
                    ]
                },
            )
    async def parse(self, response):

        page = response.meta["playwright_page"]

        headers = response.css("li.results-row")

        for header in headers:


            title = header.css("h4.result-title a p::text").get()

            document_title = header.css("h5.document-title p::text").get()
            source_url = header.css("h4.result-title a::attr(href)").get()
            source_pdf = header.css("a.btn-details[href$= '.pdf'] ").get()

            yield {
                "Title": title,
                "Document_Title": document_title,
                "Source_Url": source_url,
                "Source_Pdf": source_pdf
            }

        try:
            while True:
            
                next_button = await page.query_selector("li.page-item:not(.disabled) >> text='Next'")

                if not next_button:
                    break

                await next_button.wait_for_element_state("visible")
                await next_button.click()

                content = await page.content()

                updated_content = HtmlResponse(
                    url = response.url,
                    body=content,
                    encoding="utf-8",
                    request=response.request
                )

                async for item in self.parse(updated_content):
                    yield item

                


        except Exception as e:
            self.logger.warning("Playwright error {e}")