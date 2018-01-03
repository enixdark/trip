# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import os
import random
from scrapy.conf import settings
from stem.control import Controller, EventType
from stem import Signal
import time
from stem import CircStatus
import random
from stem.util import log
from lsm import LSM
from scrapy.conf import settings
import os 

class LSMEngine(object):
	# create lsm key-value database to cache key for update data in other DB
    db = LSM(''.join([settings['LSM_PATH'],settings['LSM_DBNAME']]))


class RandomUserAgentMiddleware(object):
    def process_request(self, request, spider):
        ua  = random.choice(settings.get('USER_AGENT_LIST'))
        if ua:
            request.headers.setdefault('User-Agent', ua)

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('HTTP_PROXY')

class TorIpChangeMiddleware(object):
    
    def __init__(self):
        self._tor_lock = True
        
        # mute the logger for this test since otherwise the output is overwhelming
        stem_logger = log.get_logger()
        stem_logger.setLevel(log.logging_level(None))
    def conn_init(self):
        self.controller = Controller.from_port(port=9051)
        self.controller.authenticate('quandc')

    def _change_tor_lock(self, event):
        self._tor_lock = False

        
    def process_request(self, request, spider):

        self._tor_lock = True


        controller = Controller.from_port(port=9051)
        controller.authenticate('quandc')

        controller.add_event_listener(self._change_tor_lock, EventType.SIGNAL)
        controller.signal(Signal.NEWNYM)


        #print ("network changed")
        
        circuits = controller.get_circuits()
        num_circ = len(circuits)
        circ_ids = []
        
        count = 0
        for circ in circuits: 

            if circ.status != CircStatus.BUILT:
                continue
     
            exit_fp, exit_nickname = circ.path[-1]
     
            exit_desc = controller.get_network_status(exit_fp, None)
            exit_address = exit_desc.address if exit_desc else 'unknown'
     
            circ_ids.append(circ.id)
            count +=1

            

        while self._tor_lock:
            time.sleep(controller.get_newnym_wait())
        else:
            if len(circ_ids) > 6:
                try:
                    while len(circ_ids) <= 6:
                        controller.close_circuit(circ_ids[0])
                except:
                    pass
            controller.new_circuit()
            controller.close()




class TripadvisorSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TripadvisorDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
