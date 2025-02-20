import scrapy
import random


class DataGov(scrapy.Spider):
    #3202 data 

    name = "usdataset"
    start_urls = ["https://catalog.data.gov/dataset/?q=&sort=views_recent+desc&page=3767"]
    
    custom_settings = {
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.5,
        "ROBOTSTEXT_OBEY": True,
        "USER_AGENT_LIST":
         [ 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
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
          
         ],
        "RETRY_TIMES": 3, 
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429, 403],
        "ROTATING_PROXY_LIST": [
                "http://77.237.238.141:8888",
                "http://54.179.44.51:3128",
                "http://3.97.176.251:3128" 

        ],
     
    }

    def start_requests(self):
       
        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                callback=self.parse,
            )

    def parse(self, response):
   
        datasets = response.css("li.dataset-item")
        
        if "7667" in response.url:
            self.crawler.close()

        for data in datasets:
         
            source_link = data.css(".dataset-heading a::attr(href)").get()
            if source_link:

                full_link = response.urljoin(source_link)

                yield scrapy.Request(
                    url=full_link,
                    callback=self.parse_inside    
                )
        next_page = response.css("li.page-item.active + li.page-item a.page-link::attr(href)").get()
        if next_page:
            full_next_page = response.urljoin(next_page)
            print(full_next_page)

            yield response.follow(
                url=full_next_page,
                callback=self.parse,
                   headers={
                    "Referer": response.url
                },
            )

    def parse_inside(self, response):

        title = response.css("h1[itemprop='name']::text").get(" ").strip()
        details = " ".join(response.css("div.notes.embedded-content ::text").getall()).strip()
        source_url = response.url

        yield {
            "source_url": source_url,
            "title": title,
            "details": details,
        }






        

