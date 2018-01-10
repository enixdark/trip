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
from ..utils.enum import PostType

logger = logging.getLogger()

ORIGIN_DOMAIN = 'https://www.tripadvisor.com'
REGEX_ID = re.compile('g\d+-i\d+-(k\d+)?', re.IGNORECASE | re.MULTILINE)

# re.sub(r'(i|k|g)','', r.search(x).group()).stri

class TripTopicSpider(CrawlSpider):
    name            = "TripTopicSpider"
    allowed_domains = ["www.tripadvisor.com"]
    
    start_urls = [
		'https://www.tripadvisor.com/ShowTopic-g293921-i8432-k10867350-o10-Vietnam_Trip_Reports_JBRs_Please_post_here-Vietnam.html#postreply',
	]
    

    __queue = [
        'https://www.tripadvisor.com/ShowTopic-g293921-i8432-k11082870-PLEASE_READ_Forum_Guidelines_Updated-Vietnam.html'
	]
    
    
    rules = [
	    Rule(
	    	LinkExtractor(allow=(
	    		# r'ShowForum[-.?=\w\/]+.html',
                r'ShowTopic[-.?=\w\/]+.html',
	    	), deny=__queue,
                restrict_xpaths=[
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

    def _create_topic_item(self, url, type, data):
        item = TripadvisorForumItem()
        item['type'] = type
        item['url'] = url
        profile = data.select(".//div[@class='profile']")
        item['location'] = ''.join(profile.select(".//div[contains(@class, 'username')]").extract()).strip()
        item['post_username'] = ''.join(profile.select(".//div[@class='username']//text()").extract()).strip()
        item['level'] = ''.join(profile.select(".//div[contains(@class, 'levelBadge')]").css('div::attr(class)').extract()).split('lvl_').pop()).lstrip('0')
        item['total_post'] = ''.join(''.join(data.select(".//div[contains(@class, 'postBadge')]//span//text()").extract()).split('posts')).strip(' ')
        item['total_review'] = ''.join(''.join(data.select(".//div[contains(@class, 'reviewerBadge')]//span//text()").extract()).split('reviews')).strip(' ')
        comment = data.select(".//div[contains(@class, 'postRightContent')]")
        item['created_at'] = parser.parse(''.join(comment.select(".//div[contains(@class, 'postDate')]/text()").extract()))
        item['comment'] = ''.join(comment.select(".//div[contains(@class, 'postBody')]//text()").extract())
        item['topic_id'] = re.sub(r'(i|k|g)','', REGEX_ID.search(url).group()).strip('-')
        return item
    
    def parse_extract_topic(self, response):
        try:
            first_comment = response.xpath("//div[@class='firstPostBox']").pop()
            if first_comment:
                yield self._create_topic_item(response.url, PostType.CREATE, first_comment)
            comments = response.xpath("//div[contains(@class, 'post ') and not(contains(@class,'firstReply'))]")
            for comment in comments:
                yield self._create_topic_item(response.url, PostType.REPLY, comment)
        except Exception as e:
            logger.warning(e)
    
    def parse_extract_forum(self, response):
        try:
            list_items = response.xpath('.//tr')[1:]
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