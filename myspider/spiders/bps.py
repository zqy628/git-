# -*- coding: utf-8 -*-
import scrapy


class BpsSpider(scrapy.Spider):
    name = "bps"
    allowed_domains = ["bps.go.id"]
    start_urls = ['http://bps.go.id/']

    def parse(self, response):
        pass
