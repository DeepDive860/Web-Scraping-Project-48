import scrapy
from scrapy_playwright.page import PageMethod
from docx import Document



class Pytorch(scrapy.Spider):

    name = "pytorch"
    start_urls = ["https://docs.pytorch.org/docs/stable/index.html"]

    def start_requests(self):
        
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                # meta={
                #     "playwright": True,
                #     "playwright_include_page": True,
                #     "playwright_page_methods":[
                #         PageMethod("wait_for_selector", "li.toctree-l1", state="visible", timeout=120000)
                #     ]
                # },
                callback=self.parse

            )

    def parse(self, response):

        function_list = []


        urls = response.css("li.toctree-l1 > a::attr(href)").getall()

        for url in urls:

            function_list.append(response.urljoin(url))
        

    

        for x in function_list:
            print(x)
         
        



        






