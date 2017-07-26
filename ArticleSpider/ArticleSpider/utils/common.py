# -*- coding: utf-8 -*-
import hashlib
import re

def get_md5(url):
    if isinstance(url,str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def extract_num(text):
    #从字符串提取数字
    match_re = re.match(r".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

#当模块被直接运行时，以下代码块将被运行，当模块是被导入时，代码块不被运行
if __name__ == "__main__":
    print (get_md5("http://jobbole.com"))