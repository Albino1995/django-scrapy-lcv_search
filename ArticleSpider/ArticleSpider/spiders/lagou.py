# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import LagouJobItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com']
    cookies = {
        "user_trace_token": "20170601123731-5d9f9681e353420fa16d0a00b6d4e2cd",
        "LGUID": "20170601123731-0643e4f1-4684-11e7-8710-525400f775ce",
        "_putrc": "74A399BD0E611E95 ",
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
        "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1500954181",
        "LGSID": "20170725110600-2fbd6d92-70e6-11e7-b64a-5254005c3644",
        "LGRID": "20170725114301-5bdd35f0-70eb-11e7-b64c-5254005c3644"
    }
    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def start_requests(self):
        url = "https://www.lagou.com"
        time.sleep(3)
        yield scrapy.Request(url=url, cookies=self.cookies, method='GET')

    def parse_job(self, response):
        #解析拉勾网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        publish_time = response.css(".publish_time::text").extract()[0].split(" ")[0].strip()
        item_loader.add_value("publish_time", publish_time)
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())
        time.sleep(3)
        job_item = item_loader.load_item()

        return job_item
