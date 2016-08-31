#-*- coding: utf-8 -*-

from TED5.items import Ted5Item
import scrapy
import time

import sys, os

from pprint import pprint
from elasticsearch import Elasticsearch

## http://ed.ted.com/lessons?subtitles=af&content_type=originals&student_level=1&page=1


class ted5Spider(scrapy.Spider):
    name = "ted5"
#    allowed_domains = ["ed.ted.com/lessons"]
    base_urls = 'http://ed.ted.com'
    start_urls = [base_urls + '/lessons']

    content_type = []
    student_level = []
    subtitles = []
    
    # key: url, value: object
    objs = {}
    
    
    def closed(self, reason):
        print(">>>> END")
    
    def makeNewUrl(self):
        for c_type in self.content_type:
            yield ('content_type', c_type.extract())

        for s_level in self.student_level:
            yield ('student_level', s_level.extract())
    
#        return
#    
#        for subt in self.subtitles:
#            yield ('subtitles', subt.extract())
    
    # make option list.
    def prepareData(self, response):
        if len(self.content_type) <= 0:
            self.content_type = response.css('li[data-track-action="Content Type"] input::attr(value)')
            self.student_level = response.css('li[data-track-action="Student Level"] input::attr(value)')
            self.subtitles = response.css('li[data-track-action="Subtitles"] input::attr(value)')
            
            return True
            
        return False
    
    def parse(self, response):

        self.prepareData(response)
        
        # http://doc.scrapy.org/en/latest/topics/request-response.html#topics-request-response-ref-request-callback-arguments
        for tmpType, tmpUrl in self.makeNewUrl():
            url_wo_page = self.start_urls[0] + '?' + tmpType + '=' + tmpUrl
            request = scrapy.Request(url_wo_page + '&page=' + str(1), self.parse_sub)
            request.meta['privateData'] = {tmpType: tmpUrl}
            request.meta['url_wo_page'] = url_wo_page
            request.meta['page'] = 2
            yield request
            
    def getObject(self, url):
        item = None
        if self.objs.get(url) is None:
            item = Ted5Item()
        else:
            item = self.objs[url]
        return item
    
    def setObject(self, url, obj):
        self.objs[url] = obj

    def isStoredItem(self, _id):
        try:
            res = es.exists(index=self.settings['ELASTICSEARCH_INDEX'], 
                            doc_type=self.settings['ELASTICSEARCH_TYPE'], 
                            id=_id)
            pprint (res)
        except:
            return False
        
        return res
        
        
        
    def parse_sub(self, response):
        # http://doc.scrapy.org/en/latest/topics/settings.html
        es = Elasticsearch(self.settings['ELASTICSEARCH_SERVERS'],
                           use_ssl=False)

        privateData = response.meta['privateData']
        
        opt_name = privateData.keys()[0]
        opt_value = privateData.values()[0]
        
        print('[META] k: ' + opt_name)
        print('[META] v: ' + opt_value)
        
        # <div class="lesson videoCell four columns" id="lesson_772192">
        ll = response.css('div[class="lesson videoCell four columns"]')

        for href in ll:
            perContents = href.css('div[class="video-text"]')[0]
            title = perContents.css('a::text')[0].extract()
            
            dur = perContents.css('span::text')[0].extract()
            suburl = perContents.css('a::attr(href)')[0].extract()
            suburl = self.base_urls + str(suburl)
            
            dur_d = dur.strip().split(" ")[1]
            
            item = self.getObject(suburl)
            item["url"] = suburl
            
            tmpList = item.get(opt_name)
            if tmpList is None:
                tmpList = list()
            
            if opt_value not in tmpList:
                tmpList.append(opt_value)
            item[opt_name] = tmpList
            
            self.setObject(suburl, item)
            
            # is exist item?
            if self.isStoredItem(suburl):
                yield item
            else:
                item["title"] = title
                item["duration"] = dur_d

                # to get youtube url... get more page
                request = scrapy.Request(suburl, self.parse_youtube)
                request.meta['item'] = item
                
                yield request
        
        if len(ll) > 0:
            request = scrapy.Request(response.meta['url_wo_page'] + "&page=" + str(response.meta['page']), self.parse_sub)
            request.meta['privateData'] = response.meta['privateData']
            request.meta['url_wo_page'] = response.meta['url_wo_page']
            request.meta['page'] = response.meta['page'] + 1
            
            yield request

            
    def parse_youtube(self, response):
        item = response.meta['item']
        
        ll = response.css('div[class="videoContainer"] div[id="playerContainer"]::attr(data-video-id)')
        
        if len(ll)>0:
            utubeId = ll[0].extract()
            item['youtube'] = utubeId
            
        yield item