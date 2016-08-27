#-*- coding: utf-8 -*-

from TED.items import TedItem
import scrapy
import time

import sys, os

## http://ed.ted.com/lessons?subtitles=af&content_type=originals&student_level=1&page=1


class TEDSpider(scrapy.Spider):
    name = "ted"
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
#            print(">>> " + c_type.extract())
            yield ('content_type', c_type.extract())

        for s_level in self.student_level:
#            print(">>> " + s_level.extract())
            yield ('student_level', s_level.extract())
    
        for subt in self.subtitles:
#            print(">>> " + subt.extract())
            yield ('subtitles', subt.extract())
    
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
            item = TedItem()
        else:
            item = self.objs[url]
        return item
    
    def setObject(self, url, obj):
        self.objs[url] = obj

    def parse_sub(self, response):
        
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
            item["title"] = title
            item["duration"] = dur_d
            item["url"] = suburl
            
            tmpList = item.get(opt_name)
            if tmpList is None:
                tmpList = list()
            
            if opt_value not in tmpList:
                tmpList.append(opt_value)
            item[opt_name] = tmpList
            
            self.setObject(suburl, item)
            
#            yield item
        
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
#            print('>>> YOUTUBE: ' + utubeId)
            item['youtube'] = utubeId
            
        yield item