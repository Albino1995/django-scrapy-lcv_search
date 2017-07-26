# -*- coding: utf-8 -*-
import scrapy
import json


from ArticleSpider.items import GJZDItem

class GzjtSpider(scrapy.Spider):
    name = "gzjt"
    allowed_domains = ["www.gzjt.gov.cn"]
    start_urls = ['http://www.gzjt.gov.cn/gztraffic/GetData.ashx']

    def parse(self, response):
        jt_json = json.loads(response.text)
        time = jt_json["refreshTime"]
        for jt in jt_json["RoadData"]:
            jt_item = GJZDItem()
            jt_item["road_id"] = jt["RoadID"]
            jt_item["road_name"] = jt["RoadName"]
            jt_item["dir_name"] = jt["Dir"]
            jt_item["road_tti"] = jt["RoadTTI"]
            jt_item["cong_name"] = jt["CongName"]
            jt_item["time"] = time
            yield jt_item





