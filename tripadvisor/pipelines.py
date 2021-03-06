# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy import log
from .middlewares import LSMEngine

class TripadvisorPipeline(object):
    def __init__(self):
        self.connection = MongoClient(settings.get('MONGODB_URI'))
        self.db = connection[settings['MONGODB_DATABASE']]
        # db.authenticate(settings['MONGODB_USERNAME'], settings['MONGODB_PASSWORD'])
        # self.collection = db[settings['CRAWLER_COLLECTION_TOPIC']]

    def process_item(self, item, spider):
        import ipdb; ipdb.set_trace()
        data = dict(item)
        
        if data['url'] not in LSMEngine.db:
            pass
            # LSMEngine.db[data['url']] = True
            # self.collection.insert(data)
        
        return item

