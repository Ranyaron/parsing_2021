# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import pymongo
from dotenv import load_dotenv


class GbParsPipeline:
    def process_item(self, item, spider):
        return item


class SaveToMongoPipeline:
    def __init__(self):
        load_dotenv('.env')
        data_base_url = os.getenv('DATA_BASE_URL')
        client = pymongo.MongoClient(data_base_url)
        self.db = client["parsing_2021"]

    def process_item(self, item, spider):
        self.db[type(item).__name__].insert_one(item)
        return item
