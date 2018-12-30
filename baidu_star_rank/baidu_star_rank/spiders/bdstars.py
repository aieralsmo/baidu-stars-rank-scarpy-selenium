# -*- coding: utf-8 -*-
import time
import json
import re
import scrapy

from baidu_star_rank.items import BaiduStarRankItem

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# 专业伪装浏览器
def gen_browser(driver_path):
    '''实例化一个driver'''
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-plugins-discovery")
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
    options.add_argument('user-agent="{0}"'.format(user_agent))
    # ############### 专业造假 ***************************
    def send(driver, cmd, params={}):
        '''
        向调试工具发送指令
        from: https://stackoverflow.com/questions/47297877/to-set-mutationobserver-how-to-inject-javascript-before-page-loading-using-sele/47298910#47298910
        '''
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        if response['status']:
            raise Exception(response.get('value'))
        return response.get('value')
    def add_script(driver, script):
        '''在页面加载前执行js'''
        send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script})
    # 给 webdriver.Chrome 添加一个名为 add_script 的方法
    webdriver.Chrome.add_script = add_script # 这里（webdriver.Chrome）可能需要改，当调用不同的驱动时
    # *************** 专业造假 ###################
    browser = webdriver.Chrome(
        executable_path=driver_path,
        chrome_options=options
    )
    # ################## 辅助调试 *********************
    existed = {
        'executor_url': browser.command_executor._url,  # 浏览器可被远程连接调用的地址
        'session_id': browser.session_id  # 浏览器会话ID
    }
    # pprint(existed)
    # ********************* 辅助调试 ##################
    # ############### 专业造假 ***************************
    browser.add_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });
    window.navigator.chrome = {
        runtime: {},
    };
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh']
    });
    Object.defineProperty(navigator, 'plugins', {
        get: () => [0, 1, 2],
    });
    """)
    # *************** 专业造假 ###################
    return browser



class BdstarsSpider(scrapy.Spider):
    name = 'bdstars'
    allowed_domains = ['index.baidu.com']
    start_urls = ['http://index.baidu.com/v2/rank/index.html/']

    def parse(self, response):
        driver_path = self.settings.get('DRIVER_PATH')
        # 实例化浏览器
        browser = gen_browser(driver_path)
        try:
            
            browser.get('http://index.baidu.com/v2/rank/index.html?#/industryrank/star')

            #########################################################################################
            # 一：获取导航栏上的导航标签 --> 分别是： 周榜，周上升榜，月榜
            type_banner_tabs = WebDriverWait(browser, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,'div.banner-tabs .tab-item'))
                )
            # 计算导航栏上导航标签的数量
            banner_tabs_count = len(type_banner_tabs)

            banner_tabs = ["周榜","周上升榜", "月榜"]

            # 分别循环点击每一个标签，获取标签点击之后对应的页面信息
            for x in range(banner_tabs_count):
                type_banner_tabs[x].click()
                time.sleep(1)
                
                items = self.parse_index_tab(browser,banner_type_tab=banner_tabs[x])
                for item in items:
                    yield item
            print("成功保存数据到文件中!!!")
        except Exception as e:
            with open('error.log','a',encoding='UTF8') as wf:
                emsg = 'parse-->'+str(e)+"\n"
                wf.write(emsg)
                
                browser.quit() # 退出相关驱动程序,并关闭所有窗口


    def parse_index_tab(self,browser,banner_type_tab=None):
        #########################################################################################
        try:
            # 二：获取详细排行榜上的两个指数标签按钮 --> 分别是：搜索指数，资讯指数
            index_tabs = WebDriverWait(browser, 5).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.top-list .tab-item'))
                        )
            # 计算指数标签按钮的数量
            tabs_count = len(index_tabs)

            type_index_tabs = ["搜索指数", "资讯指数"]

            # 分别循环点击每一个指数类型标签，获取标签点击之后对应的页面信息
            bit_list = []
            for y in range(tabs_count):
                
                index_tabs[y].click()
                time.sleep(1)
                # import ipdb;ipdb.set_trace()
                item = self.parse_detail(browser, index_type_tab=type_index_tabs[y],banner_type_tab=banner_type_tab)
                bit_list.extend(item)
            return bit_list
            
        except Exception as e:
            with open('error.log','a',encoding='UTF8') as wf:
                emsg = 'parse_index_tab-->'+str(e)+"\n"
                wf.write(emsg)
                # browser.close() # 关闭当前一个窗口
                browser.quit() # 退出相关驱动程序,并关闭所有窗口
            
    #########################################################################################
    def parse_detail(self, browser,index_type_tab=None,banner_type_tab=None):
        small_list = []
        # 三：获取第几周的标签（隐藏类型的标签），然后点击，此时隐藏标签就变成可见的，接着获取总共有几个子标签(span)
        # 循环遍历点击每一个span标签，接着获取点击之后的信息
        try:
            
            date_icon_up = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME,'date-icon-up'))
                )
               
            date_icon_up.click()
            time.sleep(1)

            spans_tag = browser.find_elements_by_css_selector('.date-item')
            spans_count = len(spans_tag)
       
            for z in range(spans_count):
                if z != 0:
                    date_icon_up.click()

                time.sleep(0.5)
                spans_tag[z].click()
                time.sleep(0.3)

                # 实例化一个Selector选择器 
                selector = scrapy.Selector(text=browser.page_source)

                # 排名
                ranks = selector.css('.rank::text').extract()
                # 姓名
                names = selector.css('.name::text').extract()
                # 周/月
                date = selector.css('.date-item.selected::text').extract_first()
                # 搜索指数量/资讯指数量的百分比
                lines = selector.css('.line-light::attr(style)').extract()
                if banner_type_tab == "周上升榜":
                    # 搜索指数量/资讯指数量的趋势，分别是：上升，下降，持平
                    trends = selector.css('.trend .value::text').extract()
                else:
                    # 搜索指数量/资讯指数量的趋势，分别是：上升，下降，持平
                    trends = selector.css('.icon::attr(class)').extract()
                    # 搜索指数量/资讯指数量
                    values = selector.css('.value::text').extract()

                temp = "上升"
                for i in range(len(names)):

                    pattern = re.compile(r'^width.*?(\d+.\d+%);$')
                    line =  re.search(pattern, lines[i].strip())
                    if line:
                        line = line.group(1)
                    else:
                        line = '0.00%'

                    if banner_type_tab == "周上升榜": 
                        temp=trends[i].strip()
                    else:
                        trend = trends[i].strip().split(' ')[-1]
                   
                        if trend == "trend-down":
                            temp = "下降"
                        elif trend == "trend-fair":
                            temp = "持平"


                    # 实例化存储对象
                    item = BaiduStarRankItem()

                    item['date'] = date
                    item['type_tab'] = index_type_tab
                    item['banner_tab'] = banner_type_tab

                    item['rank'] = ranks[i].strip()
                    item['name'] = names[i].strip() 

                    if banner_type_tab == "周上升榜":
                        item['value'] = 0.00
                    else:
                        item['value'] = values[i].strip() 


                    item['percentage'] = line
                    item['trend'] = temp

                    small_list.append(item)

            return small_list
        except Exception as e:
            with open('error.log','a',encoding='UTF8') as wf:
                emsg = 'parse_detail-->'+str(e)+"\n"
                wf.write(emsg)  
                # browser.close() # 关闭当前一个窗口
                browser.quit() # 退出相关驱动程序,并关闭所有窗口
            