
import scrapy
from usscraper.items import ReportItem


class UnitedStatesCourtsGov(scrapy.Spider):

    name = "uscourtsgov"
 


    def start_requests(self):
        start_urls = [

        {
            "url": "https://www.uscourts.gov/data-news/reports/statistical-reports/civil-justice-reform-act-report",
            "callback": self.parse
        },
        {
            "url":  "https://www.uscourts.gov/data-news/reports/statistical-reports/bankruptcy-filings-statistics", 
            "callback": self.parse

        },
        {
            "url": "https://www.uscourts.gov/data-news/reports/statistical-reports/judicial-facts-and-figures",
            "callback": self.parse
        }
       
    ]

        for item in start_urls:

            yield scrapy.Request(
                url=item["url"],
                callback=item["callback"]
            )
    def parse(self, response):

        reports = response.css("p a::attr(href)").getall()
        items = [response.urljoin(a) for a in reports if a]
        
        for report in items:
            if not report:
                continue
            source_url = response.urljoin(report)

            yield scrapy.Request(
                url=source_url,
                callback=self.parse_pdf,
                meta={
                    "source_url": source_url
                }
            )
  
    def parse_pdf(self, response):
        source_url = response.meta["source_url"]

        tables = response.css("table.usa-table tbody tr")
        
        for table in tables:
            title = table.css("td.views-field.views-field-field-data-table-title a::text").get()
            publication_date = table.css("td.views-field.views-field-field-date-updated::text").get().strip()
            raw_pdf = table.css("a.button.button--download::attr(href)").get()
            source_pdf = response.urljoin(raw_pdf)

            yield self.save_data(title, publication_date, source_pdf, source_url)

            
    def save_data(self, title, publication_date, source_pdf, source_url):

        item = ReportItem()
        item["title"] = title
        item["source_url"] = source_url
        item["publication_date"] = publication_date
        item["source_pdf"] = source_pdf
        return item

 


