from selenium import webdriver
import time
import re
import os
import sqlite3
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


def open_chrome():
    user_port = 9515
    find_port = os.popen('netstat -ano|findstr {}'.format(user_port)).read()
    while str(user_port) in find_port:
        print(user_port, '端口已被占用，正在更换端口')
        user_port += 1
        find_port = os.popen(
            'netstat -ano|findstr {}'.format(user_port)).read()
    # window 用注释掉的这个，把下面的os.system注释掉。macOS不用变
    # 不管Windows还是macOS都要装chromdriver，注意下目录位置，还有兼容的版本！！！
    # user-data 参数指定一个文件夹就ok了，用来缓存
    os.system(r'start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\App\\Chrome"')
    # os.system(r'sudo /usr/local/bin/chromedriver --remote-debugging-port={} --user-data-dir="/Users/ljz/temp"'.format(user_port))
    print('使用端口:', user_port)


class ItemClass:
    def __init__(self, url_keyword, user_page):
        self.url_keyword = url_keyword
        self.user_page = user_page
        self.img_url = None
        self.item_url = None
        self.sales = None
        self.price = None
        self.detail_head = None
        self.shop_name = None
        self.order_number = 0
        self.t_dic = []
        self.conn = None
        self.cursor = None
        self.img_err = 0
        self.err_log = []
        self.star = 0
        self.cnt_connect = None
        self.cnt_cursor = None
        chrome_options = webdriver.ChromeOptions()
        # 设置无头模式
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option(
            "debuggerAddress", "127.0.0.1:{}".format(user_port))

        try:
            self.Chrome = webdriver.Chrome()
        except Exception as err:
            print('开启浏览器错误:\n', err)
            self.err_log.append(err)
        # 设置位置和宽高
        self.Chrome.set_window_position(x=1000, y=353)
        self.Chrome.set_window_size(width=1900, height=900)
        # 拦截webdriver检测代码
        self.Chrome.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
                      Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                      })
                      """})

        # 初始化评论数据库
        self.conn = sqlite3.connect('./comment.db')
        self.cursor = self.conn.cursor()
        # ---连接数据库取出url
        self.cnt_connect = sqlite3.connect('./content.db')
        self.cnt_cursor = self.cnt_connect.cursor()
        print("Opened database successfully")
        table = "手机"
        cursor = self.cnt_cursor.execute("SELECT item from " + table)
        ii = 1
        for row in cursor:
            print("URL=", row[0])
            try:
                self.item_url = row[0]
                self.searchbyURL()
                print(f'第{ii}件商品')
            except Exception as err:
                print('出现错误:', err)

    # ----访问商页面并点击评价
    def searchbyURL(self):
        self.Chrome.get(self.item_url)
        time.sleep(0.3)

        _button = self.Chrome.find_element_by_xpath(
            '//*[@id="detail"]/div[1]/ul/li[5]')
        _div = self.Chrome.find_element_by_xpath(
            '//div[@class="m m-aside popbox"]')
        div2 = _div.find_element_by_xpath('.//*[@class="mc"]')
        star = div2.find_element_by_xpath(
            './/*[@class="star-gray"]').get_attribute("title")
        print(star)
        self.star = star
        self.save_stars()

        _button.click()

        time.sleep(0.5)
        get_page = 0

        while get_page < self.user_page:
            get_page += 1
            print('抓取第{}页:'.format(get_page))
            try:
                self.get_comment()
            except Exception as err:
                print('出现错误1:', err)
            if get_page != self.user_page:
                self.click_next()
                if self.commentover:
                    break

    # 直接下拉到固定的最底栏

    def scrolldown(self):
        y_plus = 550
        y = 0
        for i in range(9):
            y += y_plus
            self.Chrome.execute_script("window.scroll(0,{})".format(y))
            time.sleep(0.1)
        # self.Chrome.execute_script("window.scroll(400,200)")

    # 下拉到最底栏第二种,检查是否到最底栏
    def scrolldown_two(self):
        t = True
        y = 400
        x = self.Chrome.execute_script("return document.body.scrollHeight;")
        while t:
            check_height = self.Chrome.execute_script(
                "return document.body.scrollHeight;")
            x += y
            self.Chrome.execute_script("window.scroll(0,{})".format(x))
            time.sleep(0.5)
            check_height1 = self.Chrome.execute_script(
                "return document.body.scrollHeight;")
            if check_height == check_height1:
                # print(str(check_height1))
                t = False
        self.Chrome.execute_script("window.scroll(0,200)")

    # 按照销量排序
    # def sales_sort(self):
    #     time.sleep(1)
    #     self.Chrome.find_element_by_xpath(
    #         '//a[@data-value="sale-desc"]').click()

    # 点击下一页
    def click_next(self):
        time.sleep(2)
        self.Chrome.execute_script("window.scroll(400,150)")
        try:
            self.Chrome.find_element_by_css_selector('#comment-0 > div.com-table-footer > div > div > a.ui-pager-next').click()
            time.sleep(1)
            self.commentover = 0
        except Exception as err:
            print("评论页数不足")
            self.commentover = 1

    # ---部分修改---获得商品评价信息并储存
    def get_comment(self):
        time.sleep(0.2)
        self.scrolldown()
        time.sleep(0.5)

        com_list = self.Chrome.find_elements_by_xpath(
            '//*[@id="comment-0"]')
        print(com_list)
        for com in com_list:
            com_text = com.find_element_by_xpath(".//*[@class='comment-column J-comment-column']/p").text
            comment = {'评价': com_text, 'item': self.item_url}
            print(comment)
            self.t_dic = [com_text, self.item_url]
            # self.t_dic.append(comment)
            self.save_content_one()

    def save_stars(self):
        print('saving stars')
        table_name = self.url_keyword
        sql = 'update ' + "'" + table_name + "'" + ' set stars = ' + \
            self.star + ' where item = ' + "'" + self.item_url + "'"
        print(sql)
        print(self.cnt_cursor.execute(sql))
        self.cnt_connect.commit()

    # ---部分修改---储存在一张表中

    def save_content_one(self):
        # 时间
        print('saving')
        print(self.t_dic)
        table_name = self.url_keyword
        # 创建表sql代码,如果不存在则创建表
        sql_if_exists = '''
                        CREATE TABLE IF NOT EXISTS [{}] (
                        key_id       INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT,
                        comment          TEXT,
                        url         TEXT);
                        '''
        # 执行创建表sql代码
        self.cursor.execute(sql_if_exists.format(table_name+"comment"))
        # 执行写入表sql代码
        self.cursor.execute("INSERT INTO "+table_name+"comment" + " (comment, url) " +
                            " VALUES("+"'"+self.t_dic[0]+"'"+","+"'"+self.t_dic[1]+"'"+")")
        # 保存
        self.conn.commit()
        # 字典归零
        # self.t_dic = []

    # 二维码登录

    def login_with_qrcode(self):
        # url = 'https://s.taobao.com/search?q={}'.format(self.url_keyword)
        # self.Chrome.get(url)
        # self.Chrome.find_element_by_class_name('qrcode-img').click()  # 切换扫码登录
        time.sleep(1)
        os.system(r'rm -r ./qrLogin.png')
        # self.Chrome.set_network_conditions(
        #     offline=True, latency=5, throughput=500 * 1024)
        self.Chrome.find_element_by_class_name(
            'qrcode-img').screenshot('qrLogin.png')
        # self.Chrome.set_network_conditions(
        #     offline=False, latency=5, throughput=500 * 1024)
        time.sleep(15)
        self.intercept()

    # 开始
    def start(self, t_path=r'content.db'):
        print('开始运行')
        self.conn = sqlite3.connect(t_path)
        self.cursor = self.conn.cursor()
        get_page = 0  # 查询到了多少页
        # self.Chrome.get('https://www.taobao.com')

        # self.searchwords()
        try:
            self.login_with_qrcode()
        except Exception as err:
            print('不需要登录')
        time.sleep(1)
        # self.intercept()
        # self.sales_sort()   # 按销量排序
        try:
            while get_page < self.user_page:
                get_page += 1
                print('抓取第{}页:'.format(get_page))
                self.get_content()
                if get_page != self.user_page:
                    self.click_next()
        except Exception as err:
            print('出现错误:', err)
            self.err_log.append(err)
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        else:
            print('抓取结束一共抓取了{}位'.format(self.order_number))
            self.cursor.close()
            self.conn.commit()
            self.conn.close()


if __name__ == '__main__':
    start_time = time.time()
    # 打开远程调用浏览器
    user_port = 9515
    # if '9515' not in os.popen('netstat -ano|findstr 9515').read():
    # print('打开chrome浏览器')
    open_chrome()
    # 程序开始
    # browser = ItemClass(url_keyword=input('输入要查询的关键词:')
    #                     or '手机', user_page=int(input('查询的页数(默认10):') or 10))
    browser = ItemClass(url_keyword=input('输入要查询的关键词:')
                        or '手机', user_page=int(input('输入一个无效数字') or 10))
    # browser.start()

    # 程序结束打印信息
    end_time = time.time()
    run_time = '%.2f' % (end_time-start_time)
    print('运行了:{}秒'.format(run_time))
    # 写入日志
    with open('log.txt', 'a+') as f:
        f.write('\n程序运行结束日期:{}\n抓取数量:{}\n使用时间:{}秒\n图片获取错误:{}个\n程序出错信息:{}个\n'.format
                (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                 browser.order_number, run_time, browser.img_err, len(browser.err_log)))
        for err_tosrt in browser.err_log:
            f.write(str(err_tosrt)+'\n')
