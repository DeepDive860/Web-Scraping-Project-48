import scrapy
from scrapy_playwright.page import PageMethod




class DataGovOrganization(scrapy.Spider):

    name = "organization_catalog"

    start_urls = ["https://catalog.data.gov/organization/"]

    custom_settings = {

        "CONCURRENT_REQUESTS": 4,

        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": False
        },
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000,
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 180000

    }


    def start_requests(self):
        

        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True
                }
                
            )

    def parse(self, response):

        
        organizations = response.css("li.media-item")

        for organization in organizations:
            organization_name = organization.css("h2.media-heading::text").get()
            raw_url = organization.css("a.media-view::attr(href)").get()

            print(f"RAW URL {raw_url}")
            source_url = None
            if raw_url:
                source_url = response.urljoin(raw_url)
                print(f"Source URL {source_url}")

                yield scrapy.Request(
                    url=source_url,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "networkidle")

                        ],

                        "organization_name": organization_name,
                        "organization_source_url": source_url,
                        "dataset_items": []
                    },
                    callback=self.parse_dataset,
                    priority=0

                )

        
    def parse_dataset(self, response):

        organization_name = response.meta.get("organization_name")
        organization_source_url = response.meta.get("organization_source_url")

        dataset_list = response.css("li.dataset-item.has-organization")

        dataset_item = response.meta.get("dataset_items", [])

        for dataset in dataset_list:

            raw_dataset_source_url = dataset.css("h3.dataset-heading a::attr(href)").get()
            if raw_dataset_source_url:
                dataset_source_url = response.urljoin(raw_dataset_source_url)
            title = dataset.css("h3.dataset-heading a::text").get()
            description = dataset.css("div.note div::text").get() 
            data_formats = dataset.css("ul.dataset-resources.unstyled li a.label.label-default::attr(href)").getall() 

            dataset_item.append(

                {
                    "dataset_source_url": dataset_source_url,
                    "title": title,
                    "description": description,
                    "data_formats": data_formats 
                }
            )

            
        raw_next_page_url = response.css("ul.pagination.justify-content-center li.page-item a.page-link::attr(href)").getall()

        if raw_next_page_url:
            next_page_url = response.urljoin(raw_next_page_url[-1])

            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_dataset,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle")
                    ],
                    "dataset_items": dataset_item
                },
                priority=100
            )
            return

        yield {

            "organization_name" : organization_name if organization_name else None,
            "organization_source_url": organization_source_url,
            "datasets": dataset_item
        }   
        


        








            