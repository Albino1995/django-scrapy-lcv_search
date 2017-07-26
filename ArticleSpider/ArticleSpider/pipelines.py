# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


import MySQLdb
import MySQLdb.cursors

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):

        return item

class JsonWithEncodingPipeline(object):
    #自定义导出json文件
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding="utf-8")
    def process_item(self, item, spider):
        #json.dumps:将dict转化成str格式
        lines = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_closed(self,spider):
        self.file.close()

class JsonExporterPipleline(object):
    #调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class MysqlPipeline(object):
    #同步插入到数据库（适用于数据量少）
    def __init__(self):
        self.conn = MySQLdb.connect('localhost','root','',' article_spider',charset="utf8",use_unicode=True)
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, create_date, url, url_object_id, front_image_url, front_image_path, comments_nums, fav_nums, praise_nums, tags, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

        """
        self.cursor.execute(insert_sql,(item["title"], item["create_date"], item["url"], item["url_object_id"], item["front_image_url"][0],item["front_image_path"], item["comments_nums"], item["fav_nums"], item["praise_nums"], item["tags"], item["content"]))
        self.conn.commit()

class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            password = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)
    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error, item, spider) #处理异常
    def handle_error(self, failure, item, spider):
        #处理异步插入异常
        print (failure)
    def do_insert(self,cursor,item):
        #执行具体的插入
        #根据不同的item构建不同的sql语句并插入到myysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)

class ArticleImagePipeline(ImagesPipeline):
    # 保存图片本地地址
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok,value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item

class ElasticsearchPipeline(object):
    #将数据写入ES
    def process_item(self, item, spider):
        item.save_to_liepin()
        return item