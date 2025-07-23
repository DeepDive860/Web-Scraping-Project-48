# pipelines.py
import openpyxl
from openpyxl import Workbook

class ExcelExportPipeline:
    def open_spider(self, spider):
        self.filename = f"{spider.name}_output.xlsx"
        self.wb = Workbook()
        self.ws = self.wb.active
        self.headers_written = False

    def process_item(self, item, spider):
        # Write headers once
        if not self.headers_written:
            self.ws.append(list(item.keys()))
            self.headers_written = True
        
        self.ws.append([item.get(field, '') for field in item.keys()])
        return item

    def close_spider(self, spider):
        self.wb.save(self.filename)
