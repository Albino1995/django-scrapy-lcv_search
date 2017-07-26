from scrapy.cmdline import execute

import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy","crawl","lagou2"])
# execute(["scrapy","crawl","gjzd"])
# execute(["scrapy","crawl","jobbole"])
# execute(["scrapy","crawl","gzjt"])
#暂停重启
#重新爬取新建一个目录如002
# scrapy crawl lagou -s JOBDIR=job_info/001