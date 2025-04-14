import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.http import HtmlResponse


class UsSpending(scrapy.Spider):

    name = "federalregister"
    start_urls = ["https://www.usaspending.gov/federal_account"]

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,
            "args": ["--disable-blink-features=AutomationControlled"],
            },
        "PLAYWRIGHT_CONTEXT_KWARGS": {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000,
        "PLAYWRIGHT_DEFAULT_PAGE_GOTO_TIMEOUT": 180000
    }


    def start_requests(self):
        
        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
     
                        PageMethod("wait_for_load_state", "networkidle", timeout= 180000)
                    ],
                },
                callback=self.accessing_content
            )

    async def accessing_content(self, response):

        page1 = response.meta["playwright_page"]
        page2 = await page1.context.new_page()
        await page2.goto(response.url)
        await page2.wait_for_load_state("networkidle")

        content = await page2.content()

        updated_content = HtmlResponse(
            url=response.url,
            body=content,
            encoding="utf-8",
            request=response.request
        )

        updated_content.meta["playwright_page"] = page2

        async for item in self.parse(updated_content):
            yield item

    async def parse(self, response):
        tables = response.css("tr.results-table__row")
        
        for table in tables:
            account_number = table.css("div.results-table-cell__content::text").get()
            source_url = response.urljoin(table.css("div.results-table-cell__content a::attr(href)").get())
            title = table.css("div.results-table-cell__content::text").get()
            targeted_agency = table.css("div.results-table-cell__content::text").getall()
            owning_agency = " "

            if len(targeted_agency) >= 2:
                owning_agency = targeted_agency[1]

            budget_resources_current_year = table.css("div.cell-content::text").get()

            yield {
                "account_number": account_number,
                "source_url": source_url,
                "title": title,
                "owning_agency": owning_agency,
                "budget_resources_2025": budget_resources_current_year
            }

    
        page = response.meta["playwright_page"]
        next_selector = 'button.pager__button[title="Next page"]:not([disabled])'
        try:
               
            await page.wait_for_selector(next_selector, state="visible", timeout=180000)
            next_button = await page.query_selector(next_selector)
            if not next_button:
                self.logger.warning(f"No button")
                

            await next_button.scroll_into_view_if_needed()
            await next_button.click(delay=100)


            content = await page.content()

            updated_response = HtmlResponse(
                url=response.url,
                body=content,
                encoding="utf-8",
                request=response.request
            )

            async for item in self.parse(updated_response):
                yield item

        except Exception as e:
            self.logger.warning(f"Playwright error {e}")









        


        










    

    