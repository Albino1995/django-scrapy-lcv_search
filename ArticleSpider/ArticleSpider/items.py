# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re


import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATETIME_FORMAT,SQL_DATE_FORMAT
from models.es_types import ArticleType, JobType
from w3lib.html import remove_tags

from elasticsearch_dsl.connections import connections

es = connections.create_connection(ArticleType._doc_type.using)

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def remove_comment_tags(value):
    #去掉tag提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowcase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests

class ArticleItemLoader(ItemLoader):
    #自定义ItemLoader
    default_output_processor = TakeFirst()

class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()#md5 固定url长度
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comments_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )

    def get_insert_sql(self):
        insert_sql = """
                          insert into jobbole_article(title, create_date, url, url_object_id, front_image_url, front_image_path, comments_nums, fav_nums, praise_nums, tags, content)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
        params = (self["title"], self["create_date"], self["url"], self["url_object_id"], self["front_image_url"][0],
                  self["front_image_path"], self["comments_nums"], self["fav_nums"], self["praise_nums"], self["tags"],
                  self["content"])

        return insert_sql,params

    def save_to_es(self):
        # 将jobbole文章item转换为es的数据
        article = ArticleType()
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self['content'])
        article.front_image_url = self['front_image_url']
        if "front_image_path" in self:
            article.front_image_path = self['front_image_path']
        article.comments_nums = self['comments_nums']
        article.praise_nums = self['praise_nums']
        article.fav_nums = self['fav_nums']
        article.url = self['url']
        article.tags = self['tags']
        article.meta.id = self['url_object_id']
        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title, 10),(article.tags, 7)))

        article.save()

class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()
    # crawl_update_time = scrapy.Field()
    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
                        insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = self["title"][0]
        content = self["content"][0]
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))
        watch_user_num = extract_num("".join(self["watch_user_num"]))
        click_num = extract_num("".join(self["click_num"]))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (zhihu_id,topics,url,title,content,answer_num,comments_num,watch_user_num,click_num,crawl_time)

        return insert_sql, params

class ZhihuAnswerItem(scrapy.Item):
    #知乎的回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        pass


class GZJTItem(scrapy.Item):
    # 广州交通item
    time = scrapy.Field()
    road_name = scrapy.Field()
    road_id = scrapy.Field()
    dir_name = scrapy.Field()
    road_tti = scrapy.Field()
    cong_name = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                        insert into gzjt(time,road_id,road_tti,dir_id,cong_id)
                        VALUES (%s,%s,%s,
                        (SELECT dir_id FROM dir where dir_name=%s),
                        (SELECT cong_id FROM cong where cong_name=%s));
                        """
        params = (self["time"], self["road_id"], self["road_tti"], self["dir_name"], self["cong_name"])
        return insert_sql, params


class GZZBItem(scrapy.Item):
    # 广州指标item
    code = scrapy.Field()
    name = scrapy.Field()
    date = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                        insert into gzzb(code,name,date)
                        VALUES (%s,%s,%s);
                        """
        params = (self["code"], self["name"], self["date"])
        return insert_sql, params


class GJZDItem(scrapy.Item):
    name = scrapy.Field()
    lng = scrapy.Field()
    lat = scrapy.Field()
    source = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                        insert into gjzd(name,lng,lat,source)
                        VALUES (%s,%s,%s,%s);
                        """
        params = (self["name"], self["lng"], self["lat"], self["source"])
        return insert_sql, params

class ZDCXItem(scrapy.Item):
    road = scrapy.Field()
    station_num = scrapy.Field()
    station_name = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                        insert ignore into zdcx(road,station_num,station_name)
                        VALUES (%s,%s,%s);
                        """
        params = (self["road"], self["station_num"], self["station_name"])
        return insert_sql, params

class LiepinJobItemLoader(ItemLoader):
    #自定义ItemLoader
    default_output_processor = TakeFirst()

class LiepinJobItem(scrapy.Item):
    #猎聘网职位信息
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    work_years = scrapy.Field()
    degree_need = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field()
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    def get_insert_sql(self):
        #插入猎聘表的sql语句

        insert_sql = """
                                insert into liepin_job(url,url_object_id,title,salary,work_years,degree_need,publish_time,
                                tags,job_desc,job_addr,company_url,company_name,crawl_time)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                ON DUPLICATE KEY UPDATE publish_time=VALUES (publish_time)
                                """
        params = (self["url"], self["url_object_id"], self["title"], self["salary"], self["work_years"],
                  self["degree_need"], self["publish_time"], self["tags"], self["job_desc"], self["job_addr"], self["company_url"],
                  self["company_name"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params

    def save_to_liepin(self):
        # 将jobbole文章item转换为es的数据
        job = JobType()
        job.title = self['title']
        job.create_date = self['publish_time']
        job.salary = self['salary']
        job.url = self['url']
        job.work_years = self['work_years']
        job.degree_need = self['degree_need']
        job.content = self['job_desc']
        job.job_addr = self['job_addr']
        job.company_url = self['company_url']
        job.company_name = self['company_name']
        job.tags = self['tags']
        job.meta.id = self['url_object_id']
        job.suggest = gen_suggests(ArticleType._doc_type.index, ((job.title, 10), (job.tags, 7)))

        job.save()

def remove_splash(value):
    #去掉工作城市的斜线
    return value.replace("/","")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    #自定义ItemLoader
    default_output_processor = TakeFirst()

class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
                job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
                tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
            """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["tags"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params

class lagouJobItem(scrapy.Item):
    city = scrapy.Field()
    company_name = scrapy.Field()
    position_name = scrapy.Field()
    work_year = scrapy.Field()
    education = scrapy.Field()
    job_nature = scrapy.Field()
    create_time = scrapy.Field()
    salary = scrapy.Field()
    position_id = scrapy.Field()
    position_advantage = scrapy.Field()
    def get_insert_sql(self):
        insert_sql = """
                        insert into lagou2(city,company_name,position_name,work_year,education,job_nature,
                        create_time,salary,position_id,position_advantage)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                        """
        params = (self["city"], self["company_name"], self["position_name"], self["work_year"],
                  self["education"], self["job_nature"],self["create_time"], self["salary"], self["position_id"],
                  self["position_advantage"])
        return insert_sql, params