# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy.loader import ItemLoader
from scrapy.selector import XmlXPathSelector
from ArticleSpider.items import ZDCXItem, ArticleItemLoader


class ZdcxSpider(scrapy.Spider):
    name = "zdcx"
    allowed_domains = ["http://openapi.aibang.com/bus/"]
    start_urls = ['http://openapi.aibang.com/bus/lines?app_key=f41c8afccc586de03a99c86097e98ccb&city=%E5%B9%BF%E5%B7%9E&q=B5%E8%B7%AF']

    def start_requests(self):
        zp = []
        pages = []
        with open("D:\\test2.txt", mode='r', encoding='utf-8') as f:
            for line in f:
                l = line.split()
                for i in l:
                    zp.append(i.replace("\ufeff", ""))
        for s in zp:
            city = '广州'
            new_page = scrapy.Request('http://openapi.aibang.com/bus/lines?app_key=f41c8afccc586de03a99c86097e98ccb&city=%s&q=%s' % (city, s)
                                      )
            pages.append(new_page)
        # print(len(pages))
        return pages

    def parse(self, response):
        x = XmlXPathSelector(response)
        zp_nodes = x.xpath("//lines")
        count = 0
        for zp_node in zp_nodes:
            road = zp_node.xpath("//lines/line/name/text()").extract()
            stats = zp_node.xpath("//lines/line/stats/text()").extract()
            for i in range(len(road)):
                s = stats[i].split(";")
                for j in range(len(s)):
                    count += 1
                    zd_item = ZDCXItem()
                    zd_item["road"] = road[i]
                    zd_item["station_name"] = s[j]
                    zd_item["station_num"] = count
                    yield zd_item
                count = 0





