import scrapy
from scrapy.http import HtmlResponse
from scrapy_playwright.page import PageMethod


class UnitedStatesCourtsForTheNinthCircuit(scrapy.Spider):

    name="unitedstatescourtsofninthcircuits"
    start_urls=[
        "https://www.ca9.uscourts.gov/opinions/"
    ]
    custom_settings={
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120000,
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 120000,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False
        }
    }


    def start_requests(self):
        
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle")
                    ]
                },
                callback=self.parse
            )

    async def parse(self, response):

        page =response.meta["playwright_page"]

        content = response.css("div#resultTable")
        
        html = None   
        while True:
            rows = content.css("tr")

            if rows:

                content_page = rows[-1]
                print("/n")
                print(f"Last Page {content_page}")
                print("/n")

                check_page = content_page.xpath("string(.//td)").get().strip()

                print(f'Check Page {check_page}')

                if not check_page and "More records available. " in check_page:
                    self.logger.info("No more records")
                    break
                
                try:

                    await page.click("text='Click here'")
                    await page.wait_for_load_state("networkidle")
                except Exception as e:
                    self.logger.info(f'No more page {str(e)}')
                    html = await page.content()
                    break

        updated_content = HtmlResponse(
            url=response.url,
            body=html,
            encoding="utf-8",
            request=response.request

        )

        for item in self.parse_data(updated_content):

            yield item
    def parse_data(self, response):

        
        table = response.css("div#resultTable")


        for item in table:

            rows = item.css("tr")

            for row in rows:

                case_title = row.css("td a::text").get()
                source_pdf = row.css("td a::attr(href)").get()

                yield {
                    "case_title": case_title,
                    "source_pdf": source_pdf
                }

                

                
            
                    


                
                
                

                


           