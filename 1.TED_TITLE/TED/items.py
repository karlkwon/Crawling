# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class TedItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
#    pass
    title = Field()
    duration = Field()
    url = Field()
    youtube = Field()
    content_type = Field(serializer=str)
    student_level = Field(serializer=str)
    subtitles = Field(serializer=str)