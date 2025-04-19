import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest


class UNTreatyCollection(scrapy.Spider):
    name = "untreatycollection"
    start_urls =  ["https://treaties.un.org/Pages/LatestTreaties.aspx?clang=_en"]
    custom_settings= {

        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 180000,
     
    }
    def parse(self, response):

        data = {

            "ctl00$ctl00$ScriptManager1": 'ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$AjaxPanalDropdown|ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$drpPageSizeLatestTreaties',
            "ctl00$ctl00$hdnLanguage": '_en',
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$ddlDate": 'Last12M',
            "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$drpPageSizeLatestTreaties": '1500'
        }

        yield FormRequest.from_response(

            response, 
            formdata=data,
            callback=self.parse_item
            
            )


    def parse_item(self, response):


        rows = response.css("tr.trBGGrey")
        for row in rows:
            title = row.xpath('.//span[contains(@id, "lnktitle")]/text()').get(default="").strip()
            treaty_type = row.xpath('.//td[2]/text()').get(default="").strip()
            data_place_conclusion = row.css("td:nth-child(3)::text").get().strip()
            registration_date = row.xpath('.//span[contains(@id, "lbl_RegDt")]/text()').get().strip()
            registration_number = row.xpath('.//a[contains(@id, "lnklbl_RegNo")]/text()').get().strip()
            regnumber_source_url = response.urljoin(row.xpath('.//a[contains(@id, "lnklbl_RegNo")]/@href').get().strip())

                    
            yield {
                "title": title,
                "treaty_type": treaty_type,
                "date_and_place_of_conclusion": data_place_conclusion,
                "registration_date": registration_date,
                "registraion_number": registration_number,
                "registration_number_source_url": regnumber_source_url
            }


class UnitedNationsTreatySeriesCumulativeIndex(scrapy.Spider):

    name = "unitednationstreatyseriescimulativeindex"
    start_urls = ["https://treaties.un.org/Pages/CumulativeIndexes.aspx?clang=_en"]


    def parse(self, response):

        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                callback=self.parse_item
            )

        for i in range(1, 7):
            
            page = str(i)
            data = {
                "ctl00$ctl00$ScriptManager1": "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$AjaxPanel1|ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$dgCI",
                "ctl00$ctl00$hdnLanguage": "_en",
                "ctl00$ctl00$ContentPlaceHolder1$HiddenJobRunningStatus": "",

                "__EVENTTARGET": "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$dgCI",
                "__EVENTARGUMENT": f"Page${page}"
                }

            yield FormRequest.from_response(
                response,
                formdata=data,
                callback=self.parse_item
            )

    def parse_item(self, response):


        open_in_browser(response)

        data_rows = response.css("table#ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolderInnerPage_dgCI tr")
        print(len(data_rows))

        with open("temp.html", "w", encoding="utf-8") as f:

            f.write(response.text)

        for data in data_rows:
            issure_number = data.css("td:nth-child(1)::text").get()
            if not issure_number:
                continue
            registration_period = data.css("td:nth-child(2)::text").get()
            if not registration_period:
                continue
            volume_range = data.css("td:nth-child(3)::text").get()
            if not volume_range:
                continue
            registered = data.css("td:nth-child(4)::text").get()
            if not registered:
                continue
            filed_and_recorded = data.css("td:nth-child(5)::text").get()
            if not filed_and_recorded:
                continue
            source_url = response.urljoin(data.css("td a::attr(href)").get())
            if not source_url:
                continue

            yield {
                "issue_number": issure_number,
                "registration_period": registration_period,
                "volume_range": volume_range,
                "registered": registered,
                "filed_and_recorded": filed_and_recorded,
                "source_url": source_url
            }

class LeagueOfNationTreatySeries(scrapy.Spider):

    name = "leagueofnationtreatySeries"
    start_urls = ["https://treaties.un.org/Pages/LONOnline.aspx?clang=_en"]
    custom_settings = {
        "PLAYWRIGHT_NAVIGATION_TIMEOUT": 180000
    }
    def parse(self, response):
   
        for i in range(1, 100):
        
            viewstate = response.xpath("//input[@id='__VIEWSTATE']/@value").get()
            eventvalidation = response.xpath("//input[@id='__EVENTVALIDATION']/@value").get()
            viewstategenerator = response.xpath("//input[@id='__VIEWSTATEGENERATOR']/@value").get()

     
            current = int(i)  
            total = 99  


            if current < total:
                next_page = current + 1

                data = {
                    "__VIEWSTATE": viewstate or "",
                    "__EVENTVALIDATION": eventvalidation or "",
                }
                if viewstategenerator:
                    data["__VIEWSTATEGENERATOR"] = viewstategenerator


                data.update({
                    "ctl00$ctl00$ScriptManager1": "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$AjaxPanel1|ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$dgCI",
                    "ctl00$ctl00$hdnLanguage": "_en",
                    "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$ddlDate": "Last12M",
                    "__EVENTTARGET": "ctl00$ctl00$ContentPlaceHolder1$ContentPlaceHolderInnerPage$dgCI",
                    "__EVENTARGUMENT": f"Page${next_page}"
                })

                self.logger.info(f"Posting formdata for page {next_page}: {data}")

                yield FormRequest.from_response(
                    response,
                    formxpath="//form[@id='form']",
                    formdata=data,
                    callback=self.parse_item,
                    dont_click=True  
                )

    def parse_item(self, response):

        data_rows = response.css("table.table.table-striped.table-bordered.table-hover.table-condensed td[align='left']")


        for data in data_rows:
            title = data.xpath('.//a[contains(@id, "lnktitle")]/text()').get().strip()
            source_url_title = response.urljoin(data.xpath('.//a[contains(@id, "lnktitle")]/@href').get().strip())
            object_name = data.xpath('.//span[contains(@id, "Object_name")]/following-sibling::text()').get().strip()
            registration_number = data.xpath('.//span[contains(@id, "Registration_Number")]/following-sibling::text()').get().strip()
            place_of_conclusion = data.xpath('.//span[contains(@id, "Place_of_Conclusion")]/following-sibling::text()').get().strip()
            treaty_type = data.xpath('.//span[contains(@id, "Type_label")]/following-sibling::text()').get().strip()
            creation_date = data.xpath('.//span[contains(@id, "Creation_Date")]/following-sibling::text()').get().strip()


            yield {
                "title": title,
                "source_url_title": source_url_title,
                "object_name": object_name,
                "registration_number": registration_number,
                "place_of_conclusion": place_of_conclusion,
                "treaty_type": treaty_type,
                "creation_date": creation_date
            }








