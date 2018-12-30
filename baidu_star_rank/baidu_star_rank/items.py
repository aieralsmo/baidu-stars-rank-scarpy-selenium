# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduStarRankItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass

    date = scrapy.Field()
    rank = scrapy.Field()
    name = scrapy.Field()
    value = scrapy.Field()
    percentage = scrapy.Field()
    trend = scrapy.Field()
    type_tab = scrapy.Field()
    banner_tab = scrapy.Field()

