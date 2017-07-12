# -*- coding: utf-8 -*-

import re
import scrapy,pymongo
from scrapy import Spider
from myspider.items import CommonItem
from datetime import datetime
import logging
from myspider.utils import duplicateFilter as dF
from myspider.config import MY_SPIDER_DB as SDB

sdb_collection = pymongo.MongoClient(SDB['server'], SDB['port'])[SDB['db']]

class DprSpider(Spider):
    name = 'dpr'
    allowed_domains = ['dpr.go.id']
    start_urls = ['http://www.dpr.go.id/berita']

    def parse(self, response):
        if not sdb_collection['sites'].find_one({"site":self.name}):#新建站点表,增加查重
            sdb_collection['sites'].insert_one({'site': self.name,'url': self.start_urls[0],'nickname':'印尼国会','classify':'政府网站'})
        base_url = '/berita/index/hal/'
        last_href = response.css('.pagination .text-right  li:last-child a::attr(href)').extract_first()
        last_index = int(re.findall(r'\d+$', last_href.encode())[0])
        for index in range(1):#爬取一页测试
            index += 1
            href = base_url + str(index)
            full_url = response.urljoin(href)
            yield scrapy.Request(full_url, callback=self.parse_news_list)

    def parse_news_list(self, response):
        # for href in response.css('.berita-item a::attr(href)'):
        #     full_url = response.urljoin(href.extract())
        # for summary in response.xpath('//*[@id="beritaDPR"]/div'):
        #     full_url = response.urljoin(summary.xpath('').extract())
        for summary in response.css('.berita-item a'):
            full_url = response.urljoin(summary.css('::attr(href)')[0].extract())
            df = dF({'url': full_url, 'site': 'dpr'}) # 实现增量爬取
            if df:
                # with open("/home/zaj/b.log", 'w') as f:
                #     f.write(full_url)
                # print('[crawl] ' + full_url)
                abstract = summary.xpath('div[starts-with(@class,"bl-content")]/text()')[0].extract()
                # abstract = summary.css('.bl-content:')[0].extract()
                yield scrapy.Request(full_url, callback=self.parse_news,meta = {'abstract':abstract})


    def parse_news(self, response):
        # 将爬到的新闻存储起来
        # filename = './data/' + response.url.split('/')[-3] + '.html'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        date_box = response.css('.main-content .date::text').extract()[0]
        date = '-'.join(reversed(re.findall(r'\d+',date_box)))+'T00:00:00Z'
        item = CommonItem()
        item["abstract"] = response.meta['abstract']
        web_body = response.css('body').extract()[0]
        # item['body'] = (filter(lambda x: x!='\n' and x!='\t' and x!='\r', web_body))#暂时注释body
        item['body'] = None
        item['url'] = response.url
        item['site'] = self.name
        item['news_title'] = response.css('.main-content .row h3::text').extract()[0]
        # item['news_content'] = response.css('.main-content .content').extract()[0]
        item['news_content'] = ''.join(response.xpath('//div[@class="content mb30"]//child::node()/text()').extract())
        # item['news_content'] = ' '.join(filter(lambda x: x!='\n' and x!='\t' and x!='\r', content))
        item['public_date'] = datetime.strptime(date,"%Y-%m-%dT%H:%M:%SZ")
        item['media'] = response.css('.main-content .date .green::text').extract()[0]
        item['author'] = None
        item['type'] = 'berita'
        # item['abstract'] = item['news_content'][:140]+'...'#摘要
        # item = na(DprItem, {
        #     'url': response.url,
        #     'site': self.name,
        #     't': response.css('.main-content .row h3::text').extract(),
        #     'c': response.css('.main-content .content').extract(),
        #     'pd': date,
        #     'm': response.css('.main-content .date .green::text').extract()
        # })
        yield item
