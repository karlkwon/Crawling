# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os

class TedPipeline(object):
    def process_item(self, item, spider):
        
        with open("title.csv", "a") as myfile:
            myfile.write('"')
            myfile.write(item['title'])
            myfile.write('","')
            myfile.write(item['duration'])
            myfile.write('","')
            myfile.write(item['url'])
            myfile.write('","')
            myfile.write(item['utube'])
            myfile.write('","')
                        
            myfile.write(os.linesep)

        return item
