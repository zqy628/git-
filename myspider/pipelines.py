# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymongo
from myspider.config import MY_SPIDER_DB as SDB
from myspider.N import na_map, cleanItem
from myspider.config import *
import os


class JsonlineWriterPipeline(object):
    def __init__(self):
        self.files = {}
        # self.file = None
    def process_item(self, item, spider):

        site = item['site']

        if not (site in self.files):
            self.files[site] = open(site + '.jl', 'wb')
        line = json.dumps(dict(item)) + '\n'
        self.files[site].write(line)
        return item


class MongoPipeline(object):
    def __init__(self):
        MONGODB_SERVER = SDB['server']
        MONGODB_PORT = SDB['port']
        MONGODB_DB = SDB['db']

        client = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = client[MONGODB_DB]

    #
    # @classmethod
    # def from_crawler(cls, crawler):
    #     return cls(
    #         mongo_uri=crawler.settings.get('MONGO_URI'),
    #         mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
    #     )
    #
    # def open_spider(self, spider):
    #     self.client = pymongo.MongoClient(self.mongo_uri)
    #     self.db = self.client[self.mongo_db]


    def process_item(self, item, spider):
        site = item['site']
        # saveFlag = item[na_map['save']]
        # if saveFlag:
        #     content = item[na_map['c']]
        #     _item = cleanItem(item)
        #     path = MONGODB_DATA_BASE_DIR + '/' + site
        #
        #     print path
        print('[insert db]:', item['url'])
        inserted_id = self.db[site].insert_one(dict(item)).inserted_id
        self.db[site].create_index([('news_title','text'),('abstract','text'),('news_content','text')])#建立全文索引
        print inserted_id
        return item

