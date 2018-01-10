# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.spiders import CrawlSpider , Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

import re
import html2text as h2t
from ..items import (
    TripadvisorForumItem,
    TripadvisorTopicItem,
)
import datetime
from dateutil import parser
import logging  
import re 
logger = logging.getLogger()

ORIGIN_DOMAIN = 'https://www.tripadvisor.com'
REGEX_ID = re.compile('g\d+-i\d+-(k\d+)?', re.IGNORECASE | re.MULTILINE)

# re.sub(r'(i|k|g)','', r.search(x).group()).stri

class TripSpider(CrawlSpider):
    name            = "TripSpider"
    allowed_domains = ["www.tripadvisor.com"]
    
    start_urls = [
		'https://www.tripadvisor.com/ShowForum-g293921-i8432-Vietnam.html',
	]
    

    __queue = [
        'https://www.tripadvisor.com/ShowTopic-g293921-i8432-k11082870-PLEASE_READ_Forum_Guidelines_Updated-Vietnam.html'
        r'ShowTopic[-.?=\w\/]+.html'
	]
    
    
    rules = [
	    Rule(
	    	LinkExtractor(allow=(
	    		r'ShowForum[-.?=\w\/]+.html',
                r'ShowTopic[-.?=\w\/]+.html',
	    	), deny=__queue,
                restrict_xpaths=[
                    # r'//div[6]/section[1]/div/div/div/div[2]/div/div[3]',
                    # r'//div[6]/section[1]/div/div/div/div[2]/div',
                    # r'//div[6]/section[2]/div/div/div/div/div[1]/div[1]/div/div/div[1]',
                    # r'//div[6]/section[2]/div/div/div/div/div[1]/div[3]/div/div/div/div[3]/div/div/div[3]/div',
                    # r'//div[6]/section[2]/div/div/div/div/div[1]/div[3]/div/div/div/div[3]/div/div/div[4]',
                    # r'//div[6]/section[2]/div/div/div/div/div[1]/div[3]/div/div/div/div[4]/div',
                    # r'//div[6]/section[2]/div/div/div/div/div[1]/div[4]/div/div'
                ]), 
	    	    callback='parse_extract_forum', follow=True
	    	)
    ]

    def extract(self,sel,xpath):
        try:
            data = sel.xpath(xpath).extract()
            text = filter(lambda element: element.strip(), data)
            return ''.join(text)
			# return re.sub(r"\s+", "", ''.join(text).strip(), flags=re.UNICODE)
        except Exception as e:
            raise Exception("Invalid XPath: %s" % e)
    
    def parse_extract_topic(self, response):
        try:
            pass
        except Exception as e:
            logger.warning(e)
    
    def parse_extract_forum(self, response):
        try:
            sel = response
            list_items = sel.xpath('.//tr')[1:]
            for it in list_items:
                data = it.select('td')
                if len(data) > 4:
                    data = data[1:]
                item = TripadvisorForumItem()
                item['url'] = response.url
                item['forum'] = data[0].select('text()').get().strip()
                item['forum_id'] = re.sub(r'(i|k|g)','', REGEX_ID.search(response.url).group()).strip('-')
                url = data[0].select('td')[1].select('a/@href').get().strip() if len(data[0].select('td')) > 0 else None
                item['forum_url'] = f'{ORIGIN_DOMAIN}{url}' if url else None
                item['topic_url'] = f"{ORIGIN_DOMAIN}{data[1].select('.//a')[0].select('@href').get()}"
                item['topic_id'] = re.sub(r'(i|k|g)','', REGEX_ID.search(item['topic_url']).group()).strip('-')
                # yield Request(
                #     url=f"{ORIGIN_DOMAIN}{data[1].select('.//a')[0].select('@href').get()}",
                #     callback = self.parse_data,priority=1000
                # )
                item['topic'] = data[1].select('.//a/text()')[0].get().strip()
                item['created_by'] = data[1].select('.//a/text()')[1].get().strip()
                item['replies'] = data[2].select('text()').get().strip()
                time = data[3].select('.//text()')[0].extract().strip()
                if time == 'yesterday':
                    time = datetime.datetime.now() - datetime.timedelta(days=1)
                else:
                    try:
                        time = parser.parse(time)
                    except:
                        time = data[3].select('.//text()')[1].extract().strip()
                        time = parser.parse(time)
                    
                item['updated_at'] = time
                try:
                    item['last_post_by'] =  data[3].select('.//a/text()')[1].get().strip()
                except:
                    item['last_post_by'] =  data[3].select('.//a/text()')[0].get().strip()
                yield item
        except Exception as e:
            logger.warning(e)