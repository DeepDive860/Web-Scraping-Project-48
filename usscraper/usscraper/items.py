# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ReportItem(scrapy.Item):


    source_url = scrapy.Field()
    title = scrapy.Field()
    source_pdf = scrapy.Field()
    publication_date = scrapy.Field()
    




class UsscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
