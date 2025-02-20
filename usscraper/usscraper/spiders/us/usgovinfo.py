import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.http import HtmlResponse

class UsgovinfoSpider(scrapy.Spider):
    name = "usgovinfo"
    allowed_domains = ["govinfo.gov"]
    start_urls = ["https://www.govinfo.gov/app/collection/budget/2011"]

    custom_settings = {

        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        "PLAYWRIGHT_PAGE_TIMEOUT": 180000,
        "PLAYWRIGHT_PAGE_GOTO_TIMEOUT": 180000,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000,
        "CONCURRENT_REQUESTS": 10,
        "DOWNLOAD_DELAY": 0.5
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.col-xs-12", state="attached", timeout=180000),
                    ],
                },
                callback=self.expand_all_buttons,
            )

    async def expand_all_buttons(self, response):
        page = response.meta["playwright_page"]

        try:
            await page.evaluate("""
                                       
            (async function() {
                function sleep(ms) {
                    return new Promise(resolve => setTimeout(resolve, ms));
                }

                async function clickElements(selector) {
                    let elements = Array.from(document.querySelectorAll(selector));
                    for (const element of elements) {
                        if (element) {
                            let parentPanel = element.closest(".panel");

                            let collapseDiv = parentPanel ? parentPanel.querySelector(".panel-collapse") : null;
                            if (collapseDiv && collapseDiv.style.display !== "block") {
                                element.scrollIntoView({ behavior: "smooth", block: "center" });
                                await sleep(800);
                                element.click();
                                await sleep(2000);

                                collapseDiv.classList.add("in");
                                collapseDiv.style.display = "block";
                            }
                        }
                    }
                }
                                
                await clickElements('i.pull-left.fa.fa-plus-circle');
                await sleep(3000);
                await clickElements('i.pull-left.fa.fa-plus-circle');
            })();
                                
        """)
            
            await page.wait_for_selector("div.panel-body", timeout=200000, state="visible")
            await page.wait_for_selector("div.panel.panel-default", timeout=180000, state="visible")
            await page.wait_for_selector("table.table", timeout=180000, state="visible")
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state("networkidle")

            html = await page.content()

            updated_response = HtmlResponse(
                url=response.url,
                body=html.encode('utf-8'),
                encoding='utf-8',
                request=response.request    
            )

            for item in self.parse_data(updated_response):
                yield item 

        except Exception as e:
            self.logger.warning(f"Playwright error: {e}")

        finally:
            await page.close()

    def parse_data(self, response):

        seen = set() 
        for panel in response.css("div.panel.panel-default"):
            fiscal_year = panel.css("div.panel-heading::attr(data-browsepath)").get("").strip()  

            panel_body = panel.css("div.panel-body")


            nested_panels = panel_body.css("div.panel.panel-default")
            if nested_panels:
                for section in nested_panels:
                    title = section.css("span.results-line1-title::text").get("").strip()
                    source_pdf_link = response.urljoin(section.css("a[href$='.pdf']::attr(href)").get(""))

                    for table in section.css("table.table"):
                        table_title = table.css("td.col-xs-12.col-sm-6 p b span.results-line1-title::text").get()
                        pdf_link = response.urljoin(table.css("div.btn-group-horizontal a[href$='.pdf']::attr(href)").get(""))

                        entry_key = (fiscal_year, title, table_title, pdf_link)
                        if title and pdf_link and entry_key not in seen:
                            seen.add(entry_key)
                            yield {
                                "Fiscal_Year": fiscal_year,
                                "Document_Title": title,
                                "Source_PDF": source_pdf_link,
                                "Table_Title": table_title,
                                "Document_URL": pdf_link
                            }


            else:
                for table in panel_body.css("table.table"):
                    table_title = table.css("td.col-xs-12.col-sm-6 p b span.results-line1-title::text").get()
                    pdf_link = response.urljoin(table.css("div.btn-group-horizontal a[href$='.pdf']::attr(href)").get(""))

                    entry_key = (fiscal_year, table_title, pdf_link)
                    if table_title and pdf_link and entry_key not in seen:
                        seen.add(entry_key)
                        yield {
                            "Fiscal_Year": fiscal_year,
                            "Table_Title": table_title,
                            "Document_URL": pdf_link
                        }
