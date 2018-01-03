# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from w3lib.html import remove_tags

class TripadvisorItem(scrapy.Item):
    url = scrapy.Field()
    href = scrapy.Field()
    forum = scrapy.Field()
    forum_url = scrapy.Field()
    topic = scrapy.Field()
    topic_url = scrapy.Field()
    created_by = scrapy.Field()
    replies = scrapy.Field()
    last_post_by = scrapy.Field()
    updated_at = scrapy.Field()
