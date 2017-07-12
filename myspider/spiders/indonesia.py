#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy,pymongo
from scrapy import Spider
from myspider.items import CommonItem
import re
from datetime import datetime
from myspider.utils import duplicateFilter as dF
from myspider.config import MY_SPIDER_DB as SDB

sdb_collection = pymongo.MongoClient(SDB['server'], SDB['port'])[SDB['db']]

class IndonesiaSpider(Spider):
    name = 'indonesia'
    allowed_domains = ['indonesia.go.id',]
    start_urls = ['http://indonesia.go.id/']

    def parse(self, response):
        if not sdb_collection['sites'].find_one({"site":self.name}):#新建站点表,增加查重
            sdb_collection['sites'].insert_one({'site': self.name, 'url': 'http://indonesia.go.id/', 'nickname': '印尼政府', 'classify': '政府网站'})
        subSelector = response.xpath("//a[text()='Selengkapnya']")
        yield scrapy.Request(url=subSelector[2].xpath("./@href").extract()[0], callback=self.parse_KB_list)  #Kanal Berita
        yield scrapy.Request(url=subSelector[4].xpath("./@href").extract()[0], callback=self.parse_BN_pages)  #Berita Nasional

    def parse_KB_list(self, response):
        subSelector = response.xpath("//li[@class='feed-item']")
        for selector in subSelector:
            full_url = selector.xpath("./a/@href").extract()[0]
            df = dF({'url': full_url, 'site': self.name}) # 实现增量爬取
            if df:
                media = selector.xpath("./div//a/text()").extract()[0]
                date_box = selector.xpath("./div/span[2]/text()").extract()[0]
                date = '20' + '-'.join(reversed(re.findall(r'\d+', date_box))) + 'T00:00:00Z'
                # 列表新闻来源不同；设置dont_filter = True忽略allowed_domains
                if media == 'Provinsi Riau':
                    yield scrapy.Request(full_url,dont_filter = True,callback=self.parse_PR_news,meta = {'media':media,'date':date})
                elif media == 'Sulawesi Tengah':
                    yield scrapy.Request(full_url, callback=self.parse_ST_news,dont_filter = True,meta = {'media':media,'date':date})
                elif media == 'Papua Barat':
                    yield scrapy.Request(full_url, callback=self.parse_PB_news,dont_filter = True,meta = {'media':media,'date':date})

    def parse_BN_pages(self, response):
        lenth = len(response.xpath("//div[@id='loopage']/a"))
        for index in range(lenth):
            index += 1
            full_url = 'http://indonesia.go.id/?page=' + str(index) +'&project=agenda-nasional-2'
            yield scrapy.Request(full_url, callback=self.parse_BN_list)

    def parse_BN_list(self, response):
        subSelector = response.xpath("//h4")
        for selector in subSelector:
            full_url = selector.xpath("./a/@href").extract()[0]
            df = dF({'url': full_url, 'site': self.name}) # 实现增量爬取
            if df:
                news_title = selector.xpath("./a/text()").extract()[0]
                abstract = selector.xpath("../text()").extract()[1].strip()
                yield scrapy.Request(full_url, callback=self.parse_BN_news, meta={'news_title': news_title, 'abstract': abstract})

    def parse_PR_news(self, response):
        item = CommonItem()
        item["media"] = response.meta['media']
        date = response.meta['date']
        item['public_date'] = datetime.strptime(date,"%Y-%m-%dT%H:%M:%SZ")
        item['body'] = None
        item['url'] = response.url
        item['site'] = self.name
        item['news_title'] = response.xpath("//head/meta[@property='og:title']/@content").extract()[0]
        item['news_content'] = response.xpath("//head/meta[@property='og:description']/@content").extract()[0]
        item['author'] = None
        item['type'] = 'berita'
        item["abstract"] = None
        yield item

    def parse_ST_news(self, response):
        item = CommonItem()
        item["media"] = response.meta['media']
        date = response.meta['date']
        item['public_date'] = datetime.strptime(date,"%Y-%m-%dT%H:%M:%SZ")
        item['body'] = None
        item['url'] = response.url
        item['site'] = self.name
        item['news_title'] = response.xpath("//head/meta[@name='og:title']/@content").extract()[0]
        item['news_content'] = ''.join(response.xpath('//p/text()').extract())
        item['author'] = None
        item['type'] = 'berita'
        item["abstract"] = response.xpath("//head/meta[@name='og:description']/@content").extract()[0]
        yield item

    def parse_PB_news(self, response):
        item = CommonItem()
        item["media"] = response.meta['media']
        date = response.meta['date']
        item['public_date'] = datetime.strptime(date,"%Y-%m-%dT%H:%M:%SZ")
        item['body'] = None
        item['url'] = response.url
        item['site'] = self.name
        news_title = response.xpath("//div[@id='content']/h1/text()")
        if news_title:
            item['news_title'] = news_title.extract()[0]
        else:item['news_title'] = None
        item['news_content'] = ''.join(response.xpath("//p[@style='text-align: justify']//text()").extract())
        item['author'] = None
        item['type'] = 'berita'
        item["abstract"] = None
        yield item

    def parse_BN_news(self, response):
        item = CommonItem()
        item["media"] = None
        # date = response.meta['date']
        item['public_date'] = None
        item['body'] = None
        item['url'] = response.url
        item['site'] = self.name
        item['news_title'] = response.meta['news_title']
        item['news_content'] = ''.join(response.xpath("//div[contains(@class,'et_pb_text_0')]//text()").extract()).strip()
        item['author'] = None
        item['type'] = 'berita'
        item["abstract"] = response.meta['abstract']
        yield item

