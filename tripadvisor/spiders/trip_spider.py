# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.spiders import CrawlSpider , Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

import re
import html2text as h2t
from ..items import TripadvisorItem
import datetime
from dateutil import parser
ORIGIN_DOMAIN = 'https://www.tripadvisor.com'

class TripSpider(CrawlSpider):
    name            = "TripSpider"
    allowed_domains = ["www.tripadvisor.com"]
    
    start_urls = [
		'https://www.tripadvisor.com/ShowForum-g293921-i8432-Vietnam.html',
	]
    

    __queue = [
	]
    
    
    rules = [
	    Rule(
	    	LinkExtractor(allow=(
	    		r'ShowForum[-.?=\w\/]+.html',
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
	    	    callback='parse_extract_data', follow=True
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
    
    
    def parse_extract_data(self, response):
        items = []
        import ipdb; ipdb.set_trace()
        try:
            sel = response
            list_items = sel.xpath('.//tr')[1:]
            for it in list_items:
                data = it.select('td')
                if len(data) > 4:
                    data.pop(0)
                item = TripadvisorItem()
                item['url'] = response.url
                item['forum'] = data[0].select('text()').get()
                url = data[0].select('td')[1].select('a/@href').get()
                item['forum_url'] = f'{ORIGIN_DOMAIN}{url}' if url else None
                item['topic_url'] = f"{ORIGIN_DOMAIN}{data.select('td')[2].select('.//a')[0].select('@href').get()}"
                item['topic'] = data.select('td')[2].select('.//a/text()')[0].get()
                item['created_by'] = data.select('td')[2].select('.//a/text()')[1].get()
                item['replies'] = data.select('td')[3].select('text()').get()
                time = data.select('td')[4].select('.//a/text()')[0].get()
                if time == 'yesterday':
                    time = datetime.datetime.now() - datetime.timedelta(days=1)
                else:
                    time = parser.parse(time)
                item['updated_at'] = time
                item['last_post_by'] = data.select('td')[4].select('.//a/text()')[0].get()
                items.append(item)
        except:
            pass
        
        return items