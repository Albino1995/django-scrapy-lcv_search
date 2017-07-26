# -*- coding: utf-8 -*-

"""
crawlspider模式
scrapy genspider -t crawl lagou www.lagou.com
"""

from datetime import datetime
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import LiepinJobItemLoader, LiepinJobItem
from utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'liepin'
    allowed_domains = ['www.liepin.com']
    start_urls = ['https://www.liepin.com/']

    rules = (
        # Rule(LinkExtractor(allow=("company/\d+",)), follow=True),
        # Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=r'job/\d+.shtml'), callback='parse_job', follow=True),
    )

    # def parse_start_url(self, response):
    #     return []
    #
    # def process_results(self, response, results):
    #     return results

    def parse_job(self, response):
        #解析猎聘网职位
        item_loader = LiepinJobItemLoader(item=LiepinJobItem(), response=response)
        item_loader.add_css("title", ".title-info h1::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        salary = response.css(".job-item-title::text").extract()[0].strip()
        item_loader.add_value("salary", salary)
        item_loader.add_css("job_addr", ".basic-infor span a::text")
        publish_time = response.css(".basic-infor span::text").extract()[4].strip()
        item_loader.add_value("publish_time", publish_time)
        degree_need = response.css(".job-qualifications span::text").extract()[0]
        item_loader.add_value("degree_need", degree_need)
        work_years = response.css(".job-qualifications span::text").extract()[1]
        item_loader.add_value("work_years", work_years)
        tags = response.css(".tag-list span::text").extract()
        tag = ",".join(tags)
        item_loader.add_value("tags", tag)
        item_loader.add_css("company_name", ".title-info h3 a::text")
        item_loader.add_css("company_url", ".word::attr(href)")
        job_descs = response.css(".content.content-word::text").extract()
        job_desc = "".join(job_descs)
        item_loader.add_value("job_desc", job_desc)
        item_loader.add_value("crawl_time", datetime.now())
        job_item = item_loader.load_item()
        return job_item
