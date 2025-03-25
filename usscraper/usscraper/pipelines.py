# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from usscraper.models import UNDATASETS, UNITEDSTATESCODE, engine


MODEL_MAPPING = {
    'un_spider': UNDATASETS,
    'unitedstatescode': UNITEDSTATESCODE
     
}

Session = sessionmaker(bind=engine)

class UsscraperPipeline:

    def __init__(self):
        self.session = Session()

    def process_item(self, item, spider):
        
        if spider.name.startswith('undataset'):
            model = UNDATASETS
        elif spider.name.startswith('uscode'):
            model = UNITEDSTATESCODE
        else:
            spider.logger.warning('No model mapping for spider: %s', spider.name )
            return item
        record = model(**dict(item))

        try:
            self.session.add(record)
            self.session.commit()
            spider.logger.info("Inserted record for spider %s: %s", spider.name, item)

        except IntegrityError:
            self.session.rollback()
            spider.logger.info("Duplicate found for spider %s: %s: ", spider.name, item)
        return item
        
    def close_spider(self, spider):
        self.session.close()

