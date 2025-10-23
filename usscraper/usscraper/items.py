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
    

class AmazonProduct(scrapy.Item):

    product_name = scrapy.Field()
    current_price = scrapy.Field()
    original_price = scrapy.Field()
    discount_percent = scrapy.Field()
    ratings = scrapy.Field()
    review_count = scrapy.Field()
    brand = scrapy.Field()
    # units_sold = scrapy.Field()
    stock_availability = scrapy.Field()
    product_url = scrapy.Field()
    image_url = scrapy.Field()
    currency = scrapy.Field()
    manufacturer = scrapy.Field()
    category = scrapy.Field()
    scraped_date = scrapy.Field()
    sold_last_month = scrapy.Field()
    sold_by = scrapy.Field()
class EbayProducts(scrapy.Item):

    product_name = scrapy.Field()
    product_id = scrapy.Field()
    current_price = scrapy.Field()
    original_price = scrapy.Field()
    discount_percent = scrapy.Field()
    category = scrapy.Field()
    # ratings = scrapy.Field()
    # review_count = scrapy.Field()
    brand = scrapy.Field()
    condition = scrapy.Field()
    units_sold = scrapy.Field()
    number_watching = scrapy.Field()
    stock_availability = scrapy.Field()
    product_url = scrapy.Field()
    image_url = scrapy.Field()
    seller = scrapy.Field()
    currency = scrapy.Field()
    scraped_date = scrapy.Field()



class UsscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
