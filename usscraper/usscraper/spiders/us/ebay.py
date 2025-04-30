import scrapy
from scrapy_playwright.page import PageMethod
import random 


class EbayspyderSpider(scrapy.Spider):
    name = "ebayspyder"
    allowed_domains = ["ebay.ph"]

    user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14"
]
    

    proxy_list = [
        "http://123.45.67.89:8080",
        "http://98.76.54.32:8080",
        "http://112.34.56.78:8080",
        
    ]

    
    def start_requests(self):

        start_urls = {
                "https://www.ebay.ph/sch/Womens-Handbags-Bags/169291/i.html?LH_ItemCondition=1000&_nkw=kate+spade&LH_PrefLoc=1&rt=nc&LH_BIN=1&_trkparms=parentrq%3A01e119731940aa7125dc353dffff5f1a%7Cpageci%3A7c7e0aef-c35b-11ef-b578-de0528e21374%7Cc%3A2%7Ciid%3A2%7Cli%3A8874": {
                    "callback": self.parse,
                    "wait_for_selector": "div.s-item__wrapper.clearfix"
                },

                "https://www.ebay.ph/b/Womens-Bags-Handbags/169291/bn_738272?rt=nc&_from=R40&_nkw=&LH_BIN=1&LH_PrefLoc=1&_sop=12&_trkparms=parentrq%253A068934411940ad8b2a7d6cc3ffffeb4a%257Cpageci%253A631bd09d-c411-11ef-ad72-028e6864acc3%257Cc%253A4%257Ciid%253A1%257Cli%253A8874": {
                      "callback": self.parse_1,
                      "wait_for_selector": "div.s-item__wrapper.clearfix"
                },
            }
        for url, params in start_urls.items():
                    
                    yield scrapy.Request(
                        url=url,
                        callback=params["callback"],
                        headers={"User-Agent": random.choice(self.user_agent_list)},
                        meta={
                            "playwright": True,
                            "playwright_include_page": True,
                            "playwright_page_methods": [
                                PageMethod("wait_for_selector", params["wait_for_selector"], timeout=200000),
                                PageMethod("goto", url, wait_until="domcontentloaded", timeout=300000)
                            ]
                        },
                    )

    async def parse(self, response):
          
          items = response.css("div.s-item__wrapper.clearfix")

          for item in items:
                title = item.css("div.s-item__title > span[role='heading']::text").get()
                price = item.css("span.s-item__price::text").get()
                location = item.css("span.s-item__location::text").get()

                yield {
                      "title": title,
                      "price": price,
                      "location": location
                }

          next_page_link = response.css("a.pagination__next.icon-link::attr(href)").get()

          if next_page_link:
                full_nextpage_link = response.urljoin(next_page_link)

                yield scrapy.Request(
                      url=full_nextpage_link,
                      headers =  {  "User-Agent": random.choice(self.user_agent_list),
                                 "Referer": "https://www.ebay.ph/",
                                 "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),
                                 },
                      callback=self.parse,
                      meta = {
                            "playwright": True,
                            "playwright_page_methods": [
                                  PageMethod("evaluate", "document.querySelector('div.s-item__wrapper.clearfix') !== null"),
                                ]
                      },
                        errback=self.handle_error
                )
          else:
                self.logger.info("No more page")

    async def parse_1(self, response):
          items = response.css("div.s-item__wrapper.clearfix")


          for item in items:
                
                
                item_inside_link = item.css("div.s-item__image a::attr(href)").get()

                if item_inside_link:
                      proxy = random.choice(self.proxy_list)
                      
                      full_inside_link = response.urljoin(item_inside_link)

                      yield scrapy.Request(
                            url=full_inside_link,
                           
                            meta= {
                                  "playwright": True,
                                  "playwright_page_methods": [
                                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                                        PageMethod("wait_for_timeout", 2000)  
                                  ],
                                  "proxy": proxy

                            },
                             callback=self.parse_1_inside,
                      )
          next_page_link= response.css("a.pagination__next.icon-link::attr(href)").get()
          if next_page_link:
                
                proxy = random.choice(self.proxy_list)

                full_nextpage_link = response.urljoin(next_page_link)
                yield scrapy.Request(
                      url=full_nextpage_link,
                      callback=self.parse_1,
                      headers= {  "User-Agent": random.choice(self.user_agent_list),
                                 "Referer": "https://www.ebay.ph/",
                                 "Accept-Language": random.choice(["en-US", "en-GB", "en-CA"]),
                                 },
                      meta= {
                            "playwright": True,
                            "playwright_page_methods": [
                                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                                    PageMethod("wait_for_timeout", 2000)  
                            ],
                            "proxy": proxy
                      },
                      errback=self.handle_error

                )
          else:
                self.logger.info("No more page")
    async def parse_1_inside(self, response):

                title = response.css("h1.x-item-title__mainTitle span.ux-textspans.ux-textspans--BOLD::text").get()
                price = response.css("div.x-price-primary span.ux-textspans::text").get()
                other_details = response.css("div.ux-labels-values__values-content span.ux-textspans::text").getall() 
                
                
                yield {
                      "title": title,
                      "price": price,
                      "other_details": other_details,
                }

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(repr(failure))

        



