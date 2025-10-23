import scrapy



class HiutDenimCoUk(scrapy.Spider):

    name = "hiutdenimcouk"
    start_urls = [
        "https://hiutdenim.co.uk/collections/mens"
    ]

    def start_requests(self):
        
        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                callback=self.parse
            )
    def parse(self, response):

        products = response.css("a.product-item.group::attr(href)").getall()

        product_urls = [response.urljoin(a) for a in products if a ]

        for url in product_urls:

            yield scrapy.Request(
                url=url,
                callback=self.parse_products
            )      
    def parse_products(self, response):
        product_title = response.css("h2.max-w-prose.font-helvetica-display.font-bold.text-xl.mt-8.text-pretty.leading-tight::text").get()
        price = response.css("div.product-price div::text").get()
        description = response.css("div.text-xs.text-pretty").xpath("string()").get()


        yield {
            "product_title": product_title,
            "price": price,
            "description": description
        }

