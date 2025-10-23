import scrapy
from scrapy import Request
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod


class LawyersListSpider(scrapy.Spider):
    name = "lawyers"
    allowed_domains = ["elibrary.judiciary.gov.ph"]
    start_urls = ["https://elibrary.judiciary.gov.ph/lawyers_list"]

    custom_settings = {
     
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120_000,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "RETRY_TIMES": 2,
        "COOKIES_ENABLED": True,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                
                    "pw": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "#dt-length-0", timeout=60_000),
                        PageMethod("select_option", "#dt-length-0", "100"),
                        PageMethod("wait_for_selector", "table tbody tr"),
                    ],
                    "playwright_page_goto_kwargs": {
                        "wait_until": "networkidle",
                        "timeout": 120_000,
                    },
                },
                callback=self.parse,
                errback=self.errback,
            )

    async def parse(self, response):

        if "playwright_page" not in response.meta:
            self.logger.warning("No playwright_page on response; rescheduling with Playwright meta.")
            yield response.request.replace(meta={**response.request.meta, "playwright": True, "playwright_include_page": True})
            return

        page = response.meta["playwright_page"]

        async def scrape_current_table():
            html = await page.content()
            sel = Selector(text=html)
            for row in sel.css("table tbody tr"):
                tds = row.css("td")
                if len(tds) < 6:
                    continue
                yield {
                    "last_name": tds[0].xpath("normalize-space()").get() or None,
                    "first_name": tds[1].xpath("normalize-space()").get() or None,
                    "middle_name": tds[2].xpath("normalize-space()").get() or None,
                    "address": tds[3].xpath("normalize-space()").get() or None,
                    "roll_signed_date": tds[4].xpath("normalize-space()").get() or None,
                    "roll_no": tds[5].xpath("normalize-space()").get() or None,
                }


        async for item in scrape_current_table():
            yield item

 
        while True:
         
            next_disabled = await page.evaluate(
                """() => {
                    const b = document.querySelector('button.dt-paging-button.next');
                    if (!b) return true;
                    return b.disabled || b.getAttribute('aria-disabled') === 'true' || b.classList.contains('disabled');
                }"""
            )
            if next_disabled:
                break

     
            try:
                prev_html = await page.locator("table tbody").inner_html()
            except Exception:
                prev_html = ""

            await page.click("button.dt-paging-button.next")

    
            try:
                await page.wait_for_function(
                    """(prev) => {
                        const tb = document.querySelector('table tbody');
                        return tb && tb.innerHTML !== prev;
                    }""",
                    arg=prev_html,
                    timeout=60_000,
                )
            except Exception:
                await page.wait_for_selector("table tbody tr", timeout=60_000)

            async for item in scrape_current_table():
                yield item

 
        try:
            await page.close()
        except Exception:
            pass

    def errback(self, failure):
        self.logger.error(f"Request failed: {failure}")
