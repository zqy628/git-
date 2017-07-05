# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from myspider.N import na_map


# 定义一个公共Item，网站新闻结构类似的应用此规则
class CommonItem(Item):
    news_title = Field()
    news_content = Field()
    url = Field()
    site = Field()
    type = Field()
    public_date = Field()
    body = Field()
    abstract = Field()
    author = Field()

# dpr.go.id网站对应的Item
class DprItem(CommonItem):
    media = Field()