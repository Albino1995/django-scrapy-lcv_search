#!/usr/bin/env python
__author__ = 'Albino'

from selenium import webdriver
from scrapy.selector import Selector
import time

# url = "https://www.zhihu.com/#signin"
# url = "https://passport.bilibili.com/login
# url = "http://www.acfun.cn/login/"
url = "http://mail.163.com/"

#设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs)
# browser = webdriver.Chrome(executable_path='D:/geckodriver/chromedriver.exe', chrome_options=chrome_opt)

#实例化对象
browser = webdriver.Chrome(executable_path='D:/geckodriver/chromedriver.exe')
browser.get(url)
time.sleep(5)

#模拟登陆知乎
# browser.find_element_by_css_selector(".view-signin input[name='account']").send_keys("")
# browser.find_element_by_css_selector(".view-signin input[name='password']").send_keys("")
# browser.find_element_by_css_selector(".view-signin button.sign-button").click()

#模拟登陆bilibili
# browser.find_element_by_css_selector("#login-username").send_keys("")
# browser.find_element_by_css_selector("#login-passwd").send_keys

#模拟登陆acfun
# browser.find_element_by_css_selector("#ipt-account-login").send_keys("")
# browser.find_element_by_css_selector("#ipt-pwd-login").send_keys("")
# browser.find_element_by_css_selector(".btn-login").click()

#模拟下拉
# for i in range(3):
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
#     time.sleep(3)

#天猫获取js填充的价格
# t_selector = Selector(text=browser.page_source)
# a = t_selector.css(" .tb-rmb-num::text").extract()[1]
# browser.quit()

#登录163邮箱
#切换表单
browser.switch_to.frame("x-URS-iframe")
browser.find_element_by_name("email").send_keys("")
browser.find_element_by_name("password").send_keys("")
browser.find_element_by_css_selector("#dologin").click()
#在表单里面操作完毕后，无论页面是否进行跳转，必须有退出表单的操作
# browser.switch_to_default_content()
