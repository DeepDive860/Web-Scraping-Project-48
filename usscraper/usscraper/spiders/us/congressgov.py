import scrapy
from scrapy_playwright.page import PageMethod


class UsCongressGov(scrapy.Spider):
    name = "uscongressgov"
    start_urls = [
        "https://www.congress.gov/search?q=%7B%22congress%22%3A%22all%22%2C%22source%22%3A%22all%22%7D"
    ]

    OX_USERNAME = "deepdive_0TdFW"
    OX_PASSWORD = "i_NhRAuyg4uRM_J"
    OX_SERVER = "unblock.oxylabs.io:60000"

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False,
            "timeout": 120000
        },
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 120000,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 120000,

        "CONCURRENT_REQUESTS": 5,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 5,
        "CONCURRENT_REQUESTS_PER_IP": 2,

    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_pages": True,
                    "playwright_context": "new_context",
                    "playwright_context_args": {
                        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                                      "Chrome/115.0.0.0 Safari/537.36",
                        "viewport": {"width": 1366, "height": 768},
                        "ignore_https_errors": True,
                        # "proxy": {
                        #     "server": f"http://{self.OX_SERVER}",
                        #     "username": self.OX_USERNAME,
                        #     "password": self.OX_PASSWORD,
                        # },
                        "java_script_enabled": True,
                        "bypass_csp": True,
                        "record_video_dir": None,
                        "permissions": [],
                        "locale": "en-US",
                        "color_scheme": "light",
                        "timezone_id": "America/New_York",
                        "extra_http_headers": {
                            "DNT": "1",
                            "Upgrade-Insecure-Requests": "1",
                        },
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle", timeout=120000),
                        PageMethod("evaluate", "window.scrollBy(0, 500)"),
                        PageMethod("wait_for_selector", "body", timeout=120000),
                    ],
                    "playwright_include_page": True,
                },
                callback=self.parse,
            )

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        try:
            items = response.css("li.expanded")
            
            for item in items:
                legislative_bill = item.css("span.result-heading > a::text").get()
                raw_url = item.css("span.result-heading a::attr(href)").get()
                source_url = response.urljoin(raw_url)

                other_details = item.css("span.result-item")
                sponsor = commitee = latest_action = None

                if len(other_details) >= 3:
                    sponsor = other_details[0].css("a::text").get()
                    commitee = other_details[1].xpath("./strong/following-sibling::text()").get()
                    latest_action = other_details[2].xpath("./strong[.='Latest Action:']/following-sibling::text()").get()
                
                if commitee:
                    commitee = commitee.strip()
                if latest_action:
                    latest_action = latest_action.strip()

                yield {
                    "legislative_bill": legislative_bill,
                    "source_url": source_url,
                    "sponsor": sponsor,
                    "commitee": commitee,
                    "latest_action": latest_action
                }

            next_page_btn = response.css("a.next::attr(href)").get()
            if next_page_btn:
                next_page_url = response.urljoin(next_page_btn)
                yield scrapy.Request(
                    url=next_page_url,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "body", timeout=120000),
                            PageMethod("wait_for_function", "document.readyState === 'complete'", timeout=120000),
                            PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        ]
                          
                    },
                    callback=self.parse
                )
                
        finally:
      
            if page and not page.is_closed():
                await page.close()