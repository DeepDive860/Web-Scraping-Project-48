from scrapy_selenium import SeleniumRequest
from scrapy import Spider
from selenium.webdriver.common.by import By


class TiasSpider(Spider):
    name = 'tias_spider'

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_selenium.SeleniumMiddleware": 800
        },
        "SELENIUM_DRIVER_NAME": "chrome",
        "SELENIUM_DRIVER_EXECUTABLE_PATH": r"C:\Users\Jezreel\Downloads\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe",
        "SELENIUM_DRIVER_ARGUMENTS": [
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080"
        ]
    }

    def start_requests(self):
        yield SeleniumRequest(
            url='https://www.state.gov/2025-tias/',
            callback=self.parse,
            wait_time=3,
            wait_until=lambda d: len(d.find_elements(By.CSS_SELECTOR, "ul.summary__list > li")) > 0,
            screenshot=False
        )

    def parse(self, response):
        driver = response.meta['driver']
        page_source = driver.page_source

        # Optional: save HTML for debugging
        with open("tias_selenium_scrapy.html", "w", encoding="utf-8") as f:
            f.write(page_source)

        # Parse each document entry
        lis = driver.find_elements(By.CSS_SELECTOR, "ul.summary__list > li")
        for li in lis:
            try:
                a_tag = li.find_element(By.TAG_NAME, 'a')
                title = a_tag.text.strip()
                link = a_tag.get_attribute('href')
                yield {
                    "title": title,
                    "source_url": link
                }
            except Exception:
                continue
