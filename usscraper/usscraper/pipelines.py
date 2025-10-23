# pipelines.py
import os
import csv
import json
from datetime import datetime
from itemadapter import ItemAdapter
from usscraper.items import EbayProducts, AmazonProduct  # your item classes


class MultiFormatExportPipeline:
    """
    Exports to:
      - CSV (.csv)
      - JSON Lines (.jsonl) -> one product per line (NDJSON)
    Files are saved under Storage_Data/<Platform>/.
    """

    def __init__(self):
        self.base_dir = os.path.abspath("Storage_Data")
        self.folder_path = None
        self.fieldnames = None

        # CSV
        self.csv_file = None
        self.csv_writer = None
        self.csv_headers_written = False

        # JSON Lines
        self.jsonl_file = None

    def open_spider(self, spider):
        os.makedirs(self.base_dir, exist_ok=True)

        # Detect platform + default field order from your Items (if known)
        name = spider.name.lower()
        platform = "Other"
        if "amazon" in name:
            platform = "Amazon"
            self.fieldnames = list(AmazonProduct.fields.keys())
        elif "ebay" in name:
            platform = "Ebay"
            self.fieldnames = list(EbayProducts.fields.keys())
        elif "lazada" in name:
            platform = "Lazada"
        elif "shopee" in name:
            platform = "Shopee"

        self.folder_path = os.path.join(self.base_dir, platform)
        os.makedirs(self.folder_path, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{spider.name}_{ts}"

        # CSV
        self.csv_filename = os.path.join(self.folder_path, f"{base}.csv")
        self.csv_file = open(self.csv_filename, "w", newline="", encoding="utf-8")
        if self.fieldnames:
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
            self.csv_writer.writeheader()
            self.csv_headers_written = True

        # JSON Lines (one object per line, no brackets)
        self.jsonl_filename = os.path.join(self.folder_path, f"{base}.jsonl")
        self.jsonl_file = open(self.jsonl_filename, "w", encoding="utf-8")

    def _ensure_headers_from_first_item(self, item_dict):
        # If we didn't know fields (non-Amazon/eBay), derive from first item
        if not self.fieldnames:
            self.fieldnames = list(item_dict.keys())

        if not self.csv_headers_written:
            # create csv writer now that we know fieldnames
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=self.fieldnames)
            self.csv_writer.writeheader()
            self.csv_headers_written = True

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()

        # Ensure headers for dynamic items
        self._ensure_headers_from_first_item(item_dict)

        # Normalize to known field order (fill missing with None)
        normalized = {field: item_dict.get(field) for field in self.fieldnames}

        # CSV
        if self.csv_writer:
            self.csv_writer.writerow(normalized)

        # JSON Lines (minified line: no spaces)
        json.dump(normalized, self.jsonl_file, ensure_ascii=False, separators=(",", ":"))
        self.jsonl_file.write("\n")

        return item

    def close_spider(self, spider):
        if self.csv_file:
            self.csv_file.close()
        if self.jsonl_file:
            self.jsonl_file.close()
