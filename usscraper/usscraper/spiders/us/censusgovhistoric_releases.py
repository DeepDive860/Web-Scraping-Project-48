import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.http import HtmlResponse


class CensusGov(scrapy.Spider):
    name = "ManufacturingandTradeInventoriesandSales"

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        
    }
    def start_requests(self):
        yield scrapy.Request(
             url="https://www.census.gov/mtis/historic_releases.html",
             meta={
                  "playwright": True,
                  "playwright_include_page": True,
                  "playwright_page_methods": [
                            PageMethod("wait_for_selector", "div.uscb-list-item-container", state= "attached", timeout=30000),
                    ],
                  "playwright_context_kwargs": {
                       "ignore_https_errors": True,
                  },
             },
        )

    async def parse(self, response):

        page = response.meta["playwright_page"]

        if not page:
            self.logger.info("No playwright page found in response")
        try:

            await page.click('a.year-select') 
            await page.wait_for_timeout(10000) 
            await page.wait_for_load_state("networkidle")
            await page.wait_for_selector("div.uscb-list-item-container", state="attached", timeout=30000)


            html = await page.content()
            updated_content = HtmlResponse(
                url=response.url,
                body=html.encode("utf-8"),
                encoding= "utf-8",
                request=response.request
            )

            for item in self.parse_item(updated_content):
                yield item
        except Exception as e:
             self.logger.info(f"Playwright error {e}")
        finally:
            await page.close()

    def parse_item(self, response):

        section_years = response.css("div.uscb-list-item-container")

        for section in section_years:
            year = section.css(".uscb-title-3::text").get()

            months = section.css("div.uscb-margin-TB-5")
            for month in months:

                month_name = month.css("a::text").get()
                file_link = month.css("a::attr(href)").get()
                
                yield {

                    "year": year,
                    "month_name": month_name,
                    "file_link": file_link
                    
                }