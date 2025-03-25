import pymysql.cursors
import scrapy
from scrapy_playwright.page import PageMethod
import pymysql


class UNDatasetSpider(scrapy.Spider):
    name = "undataset"
    start_urls = ["http://data.un.org/Explorer.aspx"]

    custom_settings = {
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
        "PLAYWRIGHT_DEFAULT_PAGE_GOTO_TIMEOUT": 60000
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                    
                    PageMethod("wait_for_selector", "body", timeout=60000),
                    PageMethod(
                    "evaluate",
                    """
                    (async () => {
                    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
                    // Set overall maximum time (in milliseconds) and stability period.
                    const maxTime = 30000;       // maximum overall time (30 seconds)
                    const stableThreshold = 5000; // exit if no new toggles appear for 5 seconds
                    const startTime = Date.now();
                    let lastToggleTime = Date.now();
                    
                    while (true) {
                        // Get all toggles not yet clicked
                        const toggles = Array.from(document.querySelectorAll('a.ygtvspacer:not(.expanded)'));
                        console.log("Found toggles: " + toggles.length);
                        
                        if (toggles.length > 0) {
                        // Update the time when toggles were found
                        lastToggleTime = Date.now();
                        // Click each toggle sequentially
                        for (const toggle of toggles) {
                            toggle.click();
                            toggle.classList.add('expanded');
                            await delay(300);  // short delay after each click
                        }
                        // Wait after the round to allow new toggles to load
                        await delay(1000);
                        } else {
                        // If no new toggles appear for the stability period, break out.
                        if (Date.now() - lastToggleTime >= stableThreshold) {
                            console.log("No new toggles for " + stableThreshold + " ms; assuming expansion complete.");
                            break;
                        }
                        // Otherwise, wait a little and check again.
                        await delay(1000);
                        }
                        
                        // If we've been running for more than the max time, exit.
                        if (Date.now() - startTime >= maxTime) {
                        console.log("Max time reached; exiting expansion loop.");
                        break;
                        }
                    }
                    
                    console.log("Finished expansion.");
                    return true;
                    })();
                    """
                ),

                    PageMethod("wait_for_timeout", 2000),
                    PageMethod("wait_for_selector", "div.ygtvchildren", timeout=60000, state="attached")
                    ],
                },
                callback=self.parse
            )

    async def parse(self, response):
        all_urls = []
        top_level = response.css("div.ygtvitem")

        for data in top_level:

            siblings = data.css("div.ygtvchildren")
            for sibling in siblings:
                rows = sibling.css("div.ygtvitem")
                for data in rows:

                    name = data.css("span.node::text").get()
                    source_url = response.urljoin(data.css("span.view a::attr(href)").get())
                    all_urls.append((name, source_url))

                    yield {
                        "table_name": name,
                        "source_url": source_url
                    } 
    
        


    
    
    
    
    

    
        



                





        











    
        
    


