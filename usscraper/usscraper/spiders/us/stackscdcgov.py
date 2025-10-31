import scrapy
from scrapy_playwright.page import PageMethod

class CDCStacksNationalNotifiableDiseasesSurveilanceSystem(scrapy.Spider):

    name = "nationalnotifiablediseasessurveilacesystem"

    start_urls = [
        "https://stacks.cdc.gov/cbrowse?parentId=cdc%3A49375"
    ]

    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120000,
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 120000,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False
        },
        "RETRY_TIMES": 5,
        "RETRY_HTTP_CODES": [403, 501,  503],
        "CONCURRENT_REQUESTS": 6,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 6

    }
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                    
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("select_option", "select#resultsPerPage", "100"),
                        PageMethod("wait_for_selector", "div.search-results", timeout=60000),
                        PageMethod("wait_for_load_state", "networkidle")
                        
                    ]
                }
            )

    async def parse(self, response):

        content = response.css("div.search-results")

        documents = content.css("li div.object-title-row.pb-4")
        
        for document in documents:

            raw_url = document.css("div.object-title a::attr(href)").get()
            
            source_url = None

            if raw_url:
                source_url = response.urljoin(raw_url)


                yield scrapy.Request(

                    url=source_url,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "networkidle"),
                        ]
                    },
                    callback=self.parse_item
                )
        raw_page = response.css("div.d-flex.justify-content-between a#nextPage::attr(href)").get()

        if raw_page:
            next_page = response.urljoin(raw_page)

            self.logger.info(f"Next Page {next_page}")
           
            yield scrapy.Request(
                url=next_page,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                        PageMethod("select_option", "select#resultsPerPage", "100"),
                        PageMethod("wait_for_selector", "div.search-results", timeout=60000),
                        PageMethod("wait_for_load_state", "networkidle")
                    ]
                },

                callback=self.parse

            )

    async def parse_item(self, response):

        publication_title = response.css("h1.title::text").get()
        publication_date = response.css("div.col-lg-3.bookHeaderListData p::text").get()
        source_pdf = response.css("div#documentPDF.bookDetailListValueChecksum a.linebreak::attr(href)").get()

        yield {
            "publication_title": publication_title.strip() or "",
            "publication_date": publication_date.strip() or "",
            "source_pdf": source_pdf,
            "source_url": response.url
        }
        



            
           



