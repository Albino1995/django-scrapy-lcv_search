# -*- coding: utf-8 -*-
import re
import json
import datetime

from urllib import parse

import scrapy
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    # question的第一页answer的请求url
    start_answer_url = "http://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    cookie = 'q_c1=151cb97c530e49a696c0b24515049b4d|1493007756000|1493007756000; _zap=d0d3573f-ca7e-487e-a98f-84be14fee3f9; d_c0="AICCZUagpwuPTsXqeSK4Wa7_4QQepgCBLgY=|1493007756"; capsion_ticket="2|1:0|10:1493009446|14:capsion_ticket|44:YTkzYWVhNzE1NDNkNDMyYWE3ZTdlMWJhOTZhZWY3M2M=|b834e3a2dc32905ba2e2f225ef71f86a5db90facf16755edef39fb2c1c3c1801"; _xsrf=bd1ca82df15a663db92292314ef6dfcf; aliyungf_tc=AQAAALGX6CVS+wwA+bT4Olqz8oogR53v; acw_tc=AQAAAOYtaE3UlAAA+bT4OlPiDEnH0weH; r_cap_id="NjE1M2YwYmNkNDRmNGU2M2FjYjljZWYwNTQ5NTE0N2Y=|1494316613|4d0306126848ba6175dc6aa06941e067e34a88e2"; cap_id="ZDQwMzRjMjMyYWZlNGM3NGE2ZWVkZDZkOGJmNWNkNjE=|1494316613|438149dacc1e6df01f98542ebd154dbfdf3029dc"; __utma=51854390.1023525481.1494313467.1494313467.1494316613.2; __utmb=51854390.0.10.1494316613; __utmc=51854390; __utmz=51854390.1494313467.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=51854390.000--|2=registration_date=20170423=1^3=entry_date=20170424=1; l_n_c=1; z_c0=Mi4wQUdDQzN0YmhwZ3NBZ0lKbFJxQ25DeGNBQUFCaEFsVk5sQU01V1FDQ0cyQzFGQjd0b1lSQVNoRWYwS25XUTVIa1VR|1494316692|baf946896b7e94eebedd24559d992530d65e8e63'
    agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhihu.com",
        'User-Agent': agent,
        'Cookie': cookie
    }

    #自定义设置
    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        '''
        提取出html页面中所有的html,并跟踪这些url进一步爬取
        如果提取url格式为/question/xxx，就下载后直接进入解析函数
        '''
        with open("index_page.html", "wb") as f:
            f.write(response.text.encode("utf-8"))
        print("ok")
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 提取到question页面则下载后提交函数提取
                request_url = match_obj.group(1)
                question_id = int(match_obj.group(2))
                yield scrapy.Request(request_url, headers=self.headers, meta={"zhihu_id": question_id}, callback=self.parse_question)
            else:
                # 如果不是question页面则进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面，从页面中提取具体的question item
        question_id = response.meta.get("zhihu_id", "")
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-actions button::text")
        item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]
        # 提取answer具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        # 重写scrapy开始
        inbox_url = "https://www.zhihu.com"
        yield scrapy.Request(url=inbox_url, cookies={}, dont_filter=True, headers=self.headers, method='GET')

    # def check_login(self,response):
    #     # 验证服务器的返回数据判断是否成功
    #     with open("index_page2.html", 'wb') as f:
    #         f.write(response.text.encode("utf-8"))
    #     pass
