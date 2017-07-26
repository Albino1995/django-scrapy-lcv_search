# -*- coding: utf-8 -*-
import scrapy
import json
import time
from scrapy.http import FormRequest

from ArticleSpider.items import lagouJobItem

class Lagou2Spider(scrapy.Spider):
    name = "lagou2"
    allowed_domains = ["www.lagou.com"]
    page_no = 1
    start_urls = ['https://www.lagou.com/jobs/positionAjax.json?city=%E5%B9%BF%E5%B7%9E&needAddtionalResult=false']
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.lagou.com",
        "Origin": "https://www.lagou.com",
        "Pragma": "no-cache",
        "Referer": "https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90?labelWords=&fromSearch=true&suginput=",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        "X-Anit-Forge-Code": "0",
        "X-Anit-Forge-Token": "None",
        "X-Requested-With": "XMLHttpRequest"
    }
    cookies = {
        "user_trace_token": "20170601123731-5d9f9681e353420fa16d0a00b6d4e2cd",
        "LGUID": "20170601123731-0643e4f1-4684-11e7-8710-525400f775ce",
        "_putrc": "74A399BD0E611E95",
        "login": True,
        "unick": "%E6%9D%8E%E6%AF%85%E6%88%90",
        "index_location_city": "%E5%B9%BF%E5%B7%9E",
        "JSESSIONID": "ABAAABAACDBAAIAE815FC279DF31DB710C63CB0AD1E648D",
        "TG-TRACK-CODE": "search_code",
        "X_HTTP_TOKEN": "342dfba0a96610b936eabe18c282d4ba",
        "SEARCH_ID": "ffb73236cb6d4ceeba011c77caade0bb",
        "_gid": "GA1.2.1437279124.1500948665",
        "_gat": 1,
        "_ga": "GA1.2.931073387.1496291847",
        "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1498549297",
        "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1500964612",
        "LGSID": "20170725125308-2703c627-70f5-11e7-b729-525400f775ce",
        "LGRID": "20170725114301-5bdd35f0-70eb-11e7-b64c-5254005c3644"
    }
    url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E5%B9%BF%E5%B7%9E&needAddtionalResult=false'
    data = {"first": "true", "pn": str(page_no), "kd": "数据分析师"}

    def start_requests(self):

        request = [scrapy.http.FormRequest(url=self.url, formdata=self.data, cookies=self.cookies,
                                               headers=self.headers, method='POST', callback=self.parse)]
        return request

    def parse(self, response):

        job_json = json.loads(response.text)
        max_num = len(job_json["content"]["positionResult"]["result"])
        for i in range(max_num):
            job_data = job_json["content"]["positionResult"]["result"][i]
            job_item = lagouJobItem()
            job_item["city"] = job_data["city"]
            job_item["company_name"]= job_data["companyShortName"]
            job_item["position_name"]  = job_data["positionName"]
            job_item["work_year"]  = job_data["workYear"]
            job_item["education"] = job_data["education"]
            job_item["job_nature"] = job_data["jobNature"]
            job_item["create_time"] = job_data["createTime"]
            job_item["salary"] = job_data["salary"]
            job_item["position_id"] = job_data["positionId"]
            job_item["position_advantage"] = job_data["positionAdvantage"]
            time.sleep(3)
            yield job_item
        if self.page_no <= 30:
            self.page_no += 1
            request = scrapy.http.FormRequest(url=self.url, formdata={"first": "true", "pn": str(self.page_no), "kd": "数据分析师"}, cookies=self.cookies,
                                               headers=self.headers, method='POST', callback=self.parse)
            yield request
        else:
            return 0





