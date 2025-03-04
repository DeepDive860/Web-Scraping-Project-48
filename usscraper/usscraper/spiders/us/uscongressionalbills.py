import pymysql.cursors
import scrapy
import pymysql
from scrapy_playwright.page import PageMethod
from scrapy.http import HtmlResponse

class USspider(scrapy.Spider):

    name = "usbills"
    allowed_domains = ["govinfo.gov"]
    start_urls = ["https://www.govinfo.gov/app/search/%7B%22historical%22%3Atrue%2C%22offset%22%3A0%2C%22query%22%3A%22collection%3A(BILLS)%20AND%20publishdate%3Arange(%2C2025-03-03)%20%22%2C%22pageSize%22%3A100%7D"]
    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000
    }

    def __init__(self):

        try:
            self.connection = pymysql.connect(
                host="localhost",
                user="root",
                password="HAHAHA",
                database="usgovdata",
                charset="utf8mb4",
                cursorclass=    pymysql.cursors.DictCursor
            )
            self.cursor = self.connection.cursor()

        except Exception as e:
            self.logger.warning(f"Database can't connect {e}")

    def start_requests(self):

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta= {
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "li.results-row", timeout = 180000, state="visible" )
                        ]
                },

            )

    async def parse(self, response):

        items = response.css("li.results-row")

        for item in items:
            title = item.css("h4.result-title a p::text").get()
            link = response.urljoin(item.css("h4.result-title a::attr(href)").get())
            source_pdf = response.urljoin(item.css("a.btn-details[href$='.pdf']::attr(href)").get())

            yield {
                "title": title,
                "link": link,
                "source_pdf": source_pdf
            }
            self.save_to_database(title, link, source_pdf)

        page = response.meta["playwright_page"]
   
        try:
            while True:
                button = await page.query_selector("li.page-item:not(.disabled) >> text='Next'")

                if not button:
                    break

                await button.wait_for_element_state("visible")
    
                await button.click()
                
                content = await page.content()

                updated_content = HtmlResponse(
                    url=response.url,
                    body=content,
                    encoding="utf-8",
                    request=response.request
                )

                async for con in self.parse(updated_content):
                    yield con
                    

        except Exception as e:
            self.logger.warning(f"Playwright error {e}")

    def save_to_database(self, title, source_url, source_pdf):

        try:
            sql = "INSERT INTO data (title, source_url, source_pdf)  VALUES (%s, %s, %s)"
            values = (title, source_url, source_pdf)

            self.cursor.execute(sql, values)
            self.connection.commit()
            self.logger.info("Inserted Succcesfully")

        except Exception as e:

            self.logger.error(f"Error inserting {e}")
            self.connection.rollback()

            







        


   

            


