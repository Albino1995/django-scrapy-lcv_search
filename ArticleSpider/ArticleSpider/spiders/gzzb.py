# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.http import FormRequest
import json
from scrapy.loader import ItemLoader

from ArticleSpider.items import GZZBItem, ArticleItemLoader


class GzzbSpider(scrapy.Spider):
    name = "gzzb"
    allowed_domains = ["apply.gzjt.gov.cn"]
    start_urls = ['http://apply.gzjt.gov.cn/apply/norm/personQuery.html']

    def parse(self, response):
        # next_url = response.xpath('//div[@class="pageturn"]/ul/li[6]/a/@href')
        results = []
        for i in range(1, 565):
            results.append(scrapy.FormRequest.from_response(
                response,
                formdata={'pageNo': str(i),
                          'issueNumber': '201705'
                          },
                callback=self.parse_detail
            ))
        for result in results:
            yield result

    def parse_detail(self, response):
        person_nodes = response.css(".ge2_content tr")
        for person_node in person_nodes:
            person = person_node.css("td::text").extract()
            item_loader = ArticleItemLoader(item=GZZBItem(), response=response)
            if person:
                item_loader.add_value("code", person[0])
                item_loader.add_value("name", person[1])
                item_loader.add_value("date", "2017-05")
            gzzb_item = item_loader.load_item()
            yield gzzb_item
