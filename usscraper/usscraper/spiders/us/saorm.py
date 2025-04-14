import scrapy


class SAORM(scrapy.Spider):

    name = "saorm"
    start_urls = ["https://www.archives.gov/records-mgmt/resources/saorm-reports"]
   
    def start_requests(self):
        
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):
        pdflink_by_year = []
        full_link = []
        items = response.css("div.table-responsive")

        for item in items:
            table_row = item.css("tr")

            for data in table_row:
                report_name = data.css("td li::text").get()

                if not report_name:
                    report_name = data.css("strong::text").get()

                year = data.css("td a.noIcon::text").getall()
                raw_pdf_link = data.css("td a.noIcon::attr(href)").getall()
                for link in raw_pdf_link:
                    full_link.append(response.urljoin(link))

                pdflink_by_year.append({str(year) : full_link})
            
                yield {
                    "report_name": report_name,
                    "year": year,
                    "source_pdf_link": full_link
                }

                

        