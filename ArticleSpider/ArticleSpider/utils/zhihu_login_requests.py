import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

session = requests.session()
#使用它的save方法
# session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
# #导入cookies
# try:
#     session.cookies.load(ignore_discard=True)
# except:
#     print ("cookie未能加载")

agent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
header = {
    "HOST":"www.zhihu.com",
    "Referer":"https://www.zhihu.com",
    'User-Agent':agent,
    'Cookie':'q_c1=151cb97c530e49a696c0b24515049b4d|1493007756000|1493007756000; _zap=d0d3573f-ca7e-487e-a98f-84be14fee3f9; d_c0="AICCZUagpwuPTsXqeSK4Wa7_4QQepgCBLgY=|1493007756"; capsion_ticket="2|1:0|10:1493009446|14:capsion_ticket|44:YTkzYWVhNzE1NDNkNDMyYWE3ZTdlMWJhOTZhZWY3M2M=|b834e3a2dc32905ba2e2f225ef71f86a5db90facf16755edef39fb2c1c3c1801"; _xsrf=bd1ca82df15a663db92292314ef6dfcf; aliyungf_tc=AQAAALGX6CVS+wwA+bT4Olqz8oogR53v; acw_tc=AQAAAOYtaE3UlAAA+bT4OlPiDEnH0weH; r_cap_id="NjE1M2YwYmNkNDRmNGU2M2FjYjljZWYwNTQ5NTE0N2Y=|1494316613|4d0306126848ba6175dc6aa06941e067e34a88e2"; cap_id="ZDQwMzRjMjMyYWZlNGM3NGE2ZWVkZDZkOGJmNWNkNjE=|1494316613|438149dacc1e6df01f98542ebd154dbfdf3029dc"; __utma=51854390.1023525481.1494313467.1494313467.1494316613.2; __utmb=51854390.0.10.1494316613; __utmc=51854390; __utmz=51854390.1494313467.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=51854390.000--|2=registration_date=20170423=1^3=entry_date=20170424=1; l_n_c=1; z_c0=Mi4wQUdDQzN0YmhwZ3NBZ0lKbFJxQ25DeGNBQUFCaEFsVk5sQU01V1FDQ0cyQzFGQjd0b1lSQVNoRWYwS25XUTVIa1VR|1494316692|baf946896b7e94eebedd24559d992530d65e8e63'}

def is_login():
    #通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/inbox"
    respone = session.get(inbox_url, headers=header, allow_redirects=False)
    pass

def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")

def get_xsrf():
    #获取xsrf code
    response = session.get("https://www.zhihu.com", headers=header)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        return (match_obj.group(1))
    else:
        return ""

def zhihu_login(account, password):
    #知乎登录
    if re.match("^1\d{10}",account):
        print ("手机号码登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password
        }
    else:
        if "@" in account:
            # 判断用户名是否为邮箱
            print("邮箱方式登录")
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": get_xsrf(),
                "email": account,
                "password": password
            }
    response_text = session.post(post_url, data=post_data, headers=header)
    session.cookies.save()
# zhihu_login("13160658727", "123321123")
get_index()
is_login()