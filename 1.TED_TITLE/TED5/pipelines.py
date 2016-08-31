# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pprint import pprint
from elasticsearch import Elasticsearch

import sys

class Ted5Pipeline(object):
    
    es = None
    settings = None
    
    @classmethod
    def from_crawler(cls, crawler):
        print (">>> from_crawler")
        
        ext = cls()
        ext.settings = crawler.settings

        ext.es = Elasticsearch(ext.settings['ELASTICSEARCH_SERVERS'],
                           use_ssl=False)
        
        print (str(ext.settings['ITEM_PIPELINES']))
        
        return ext
    
    def process_item(self, item, spider):
        
        try:
            print (">>> PIPELINE")
            pprint(item)

            res = self.es.index(index=self.settings['ELASTICSEARCH_INDEX'],
                                doc_type=self.settings['ELASTICSEARCH_TYPE'], 
                                id=item[self.settings['ELASTICSEARCH_UNIQ_KEY']], 
                                body=dict(item))
        except:
            e = sys.exc_info()[0]
            print ("Error: " + e)
            print ("Pipelie error! - %s" % (item[self.settings['ELASTICSEARCH_UNIQ_KEY']]))
        
        
        return item
    