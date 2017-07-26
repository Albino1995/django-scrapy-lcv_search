# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy.loader import ItemLoader
from scrapy.selector import XmlXPathSelector
from ArticleSpider.items import GJZDItem, ArticleItemLoader


class GjzdSpider(scrapy.Spider):
    name = "gjzd"
    allowed_domains = ["http://openapi.aibang.com/bus/"]
    start_urls = ["http://openapi.aibang.com/bus/stats?app_key=f41c8afccc586de03a99c86097e98ccb&city=%E5%B9%BF%E5%B7%9E&q=%E9%BB%84%E5%9F%94%E6%B8%AF"]

    def start_requests(self):
        zp = []
        pages = []
        with open("D:\\test.txt", mode='r', encoding='utf-8') as f:
            for line in f:
                l = line.split()
                for i in l:
                    zp.append(i.replace("\ufeff", ""))
        for s in zp:
            city = '广州'
            new_page = scrapy.Request('http://openapi.aibang.com/bus/stats?app_key=f41c8afccc586de03a99c86097e98ccb&city=%s&q=%s' % (city, s),
                                      meta={'source':s}
                                      )
            pages.append(new_page)
        return pages

    def parse(self, response):
        x = XmlXPathSelector(response)
        zp_nodes = x.xpath("//stats")
        source = response.meta.get("source", "")
        for zp_node in zp_nodes:
            name = zp_node.xpath("////stats/stat/name/text()").extract()
            xy = zp_node.xpath("//stats/stat/xy/text()").extract()
            for i in range(len(name)):
                gz_item = GJZDItem()
                gz_item["name"] = name[i]
                gz_item["source"] = source
                gz_item["lng"] = xy[i].split(",")[0]
                gz_item["lat"] = xy[i].split(",")[1]
                yield gz_item











