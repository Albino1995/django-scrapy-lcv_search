# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader

from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader

from ArticleSpider.utils.common import get_md5
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["blog.jobbole.com"]
    start_urls = ['http://blog.jobbole.com/all-posts/']

    # def __init__(self):
    #     self.browser = webdriver.Chrome(executable_path='D:/geckodriver/chromedriver.exe')
    #     super(JobboleSpider, self).__init__()
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def spider_closed(self, spider):
    #     # 当爬虫退出时，关闭chrome
    #     print("spider closed")
    #     self.browser.quit()


    def parse(self, response):
        '''
        1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2.获取下一页url并交给scrapy进行下载，下载完成后交给parse
        '''
        #获取文章列表页中的文章url并交给scrapy下载后并进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
        #提取下一页并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)



    def parse_detail(self,response):
        # article_item = JobBoleArticleItem()
        # #提取文章具体字段
        front_image_url = response.meta.get("front_image_url", "") #文章封面图
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace("·","").strip()
        # praise_nums = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()[0]
        # fav_nums = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract()[0]
        # match_re = re.match(r".*?(\d+).*",fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # comments_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # match_re = re.match(r".*?(\d+).*",comments_nums)
        # if match_re:
        #     comments_nums = int(match_re.group(1))
        # else:
        #     comments_nums = 0
        # content = response.xpath('//div[@class="entry"]').extract()[0]
        # tag_list =  response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comments_nums"] = comments_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content


        #用过item loader加载item
        item_loader = ArticleItemLoader(item = JobBoleArticleItem(),response = response)
        item_loader.add_value("url",response.url)
        item_loader.add_xpath("title",'//div[@class="entry-header"]/h1/text()')
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_xpath("create_date",'//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_xpath("praise_nums",'//span[contains(@class, "vote-post-up")]/h10/text()')
        item_loader.add_value("front_image_url",[front_image_url])
        item_loader.add_xpath("fav_nums",'//span[contains(@class, "bookmark-btn")]/text()')
        item_loader.add_xpath("comments_nums",'//a[@href="#article-comment"]/span/text()')
        item_loader.add_xpath("tags",'//p[@class="entry-meta-hide-on-mobile"]/a/text()')
        item_loader.add_xpath("content",'//div[@class="entry"]')
        article_item = item_loader.load_item()

        yield article_item
