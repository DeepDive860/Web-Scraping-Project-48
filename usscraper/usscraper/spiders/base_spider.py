# base_spider.py
import scrapy
from scrapy.utils.project import get_project_settings

class BaseSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = get_project_settings()
        self.spider_id = settings["SPIDER_REGISTRY"].get(self.name, "UNKNOWN")
