
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
    os.system(
        r'start .\\chromedriver.exe --remote-debugging-port=9222 --user-data-dir="C:\\App\\Chrome"')
    # os.system(r'sudo /usr/local/bin/chromedriver --remote-debugging-port={} --user-data-dir="/Users/ljz/temp"'.format(user_port))
    print('使用端口:', user_port)


class ItemClass:
    def __init__(self, url_keyword):
        self.img_url = None
        self.url_keyword = url_keyword
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
        chrome_options = webdriver.ChromeOptions()
        # 设置无头模式
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option(
            "debuggerAddress", "127.0.0.1:{}".format(user_port))
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
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

    def searchwords(self):
        self.Chrome.get('https://taobao.com')
        self.Chrome.find_element_by_xpath(
            '//*[@id="q"]').send_keys('{}'.format(self.url_keyword))
        time.sleep(0.3)
        self.Chrome.find_element_by_xpath(
            '//button[@class="btn-search tb-bg"]').click()

    # 如果出现验证码拦截
    def intercept(self):
        if '验证码拦截' in self.Chrome.title:
            print('滑动验证码')
            slider = self.Chrome.find_element_by_xpath(
                "//span[contains(@class, 'btn_slide')]")
            try:
                # 找到滑块
                # 判断滑块是否可见
                if slider.is_displayed():
                    # 点击并且不松开鼠标
                    ActionChains(self.Chrome).click_and_hold(
                        on_element=slider).perform()
                    # 往右边移动258个位置
                    ActionChains(self.Chrome).move_by_offset(
                        xoffset=258, yoffset=0).perform()
                    # 松开鼠标
                    ActionChains(self.Chrome).pause(0.5).release().perform()
            except Exception as err:
                print('验证码滑动出错')
                print(err)
                self.err_log.append(err)
            time.sleep(1)

    # 直接下拉到固定的最底栏
    def scrolldown(self):
        y_plus = 450
        y = 0
        for i in range(9):
            y += y_plus
            self.Chrome.execute_script("window.scroll(0,{})".format(y))
            time.sleep(0.2)
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
    def sales_sort(self):
        time.sleep(1)
        self.Chrome.find_element_by_xpath(
            '//a[@data-value="sale-desc"]').click()

    # 点击下一页
    def click_next(self):
        self.Chrome.execute_script("window.scroll(400,150)")
        self.Chrome.find_element_by_xpath('//a[@title="下一页"]').click()
        time.sleep(1)

    # 获得评论信息并储存
    def get_content(self):
        time.sleep(0.2)
        self.scrolldown()
        time.sleep(0.5)
        for item in self.Chrome.find_elements_by_xpath('.//*[@class="item J_MouserOnverReq  "]'):
            try:
                self.order_number += 1
                self.img_url = \
                    item.find_element_by_xpath(
                        './/*[@class="J_ItemPic img"]').get_attribute('src').split('_360')[0]
                self.item_url = item.find_element_by_xpath('.//*[@class="pic-link J_ClickStat J_ItemPicA"]')\
                    .get_attribute('href').split('&')[0]
                sales_tem = item.find_element_by_xpath(
                    './/*[@class="deal-cnt"]').text
                self.sales = int(''.join(re.findall(r'\d*\d', sales_tem)))
                self.price = float(item.find_element_by_xpath(
                    './/*[@class="price g_price g_price-highlight"]/strong').text)
                self.detail_head = item.find_element_by_xpath(
                    './/*[@class="J_ItemPic img"]').get_attribute('alt')
                self.shop_name = item.find_element_by_xpath(
                    './/*[@class="shopname J_MouseEneterLeave J_ShopInfo"]').text
                if '万' in sales_tem:
                    self.sales = int(
                        float(re.findall(r'\d+.\d*', sales_tem)[0])*10000)
                if '.gif' in self.img_url:
                    self.img_err += 1
                    print('排名第{}位:\t销量:{}件,\t价格为:{}元,  \t店铺名:{},  \t图片错误:{}'.format(
                        self.order_number, self.sales, self.price, self.shop_name, self.img_url))
                else:
                    print('排名第{}位:\t销量:{}件,\t价格为:{}元,  \t店铺名:{}'.format(
                        self.order_number, self.sales, self.price, self.shop_name))
                self.t_dic = [self.item_url, self.img_url, self.shop_name,
                              self.detail_head, self.price, self.sales]
                # 储存在多张表
                # self.save_content()
                # 储存在一表
                self.save_content_one()
            except Exception as err:
                print('第{}号出错,出错代码为: '.format(self.order_number), err)
                self.err_log.append(
                    '第{}号,出错代码为:{} '.format(self.order_number, err))
                continue

    # 储存在一张表中
    def save_content_one(self):
        # 时间
        t_time = time.strftime('%Y-%m-%d %H:%M:%S',
                               time.localtime(time.time()))
        # 获取商品id
        t_id = int(self.item_url.split('=')[1])
        # 字典里加入时间
        self.t_dic.append(t_time)
        # 字典里加入商品id
        self.t_dic.append(t_id)
        # 用搜索关键词当表名
        table_name = self.url_keyword
        # 创建表sql代码,如果不存在则创建表
        sql_if_exists = '''
                        CREATE TABLE IF NOT EXISTS [{}] (
                        key_id       INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT,
                        order_number    INT,
                        id          INT,
                        time        TEXT,
                        sales       INT,
                        price       REAL,
                        header      TEXT,
                        shop        TXEXT,
                        item        TEXT,
                        img         TEXT);
                        '''
        # 写入表sql代码,如果表里有匹配到的数据,则写入否则不写入
        sql_insert_or_ignore = '''
                     INSERT INTO [{0}] (order_number,id,time,sales,price,header,shop,img,item) \
                     SELECT '{2}',{1[7]},'{1[6]}','{1[5]}','{1[4]}','{1[3]}','{1[2]}','{1[1]}','{1[0]}'
                     WHERE NOT EXISTS (SELECT *FROM [{0}] WHERE id='{1[7]}' AND sales='{1[5]}');
                     '''
        # 执行创建表sql代码
        self.cursor.execute(sql_if_exists.format(table_name))
        # 执行写入表sql代码
        self.cursor.execute(sql_insert_or_ignore.format(
            table_name, self.t_dic, self.order_number))
        # 保存
        self.conn.commit()
        # 字典归零
        self.t_dic = []

    # 二维码登录

    def login_with_qrcode(self):
        url = 'https://s.taobao.com/search?q={}'.format(self.url_keyword)
        self.Chrome.get(url)
        self.Chrome.find_element_by_class_name('icon-qrcode').click()  # 切换扫码登录
        time.sleep(1)
        os.system(r'rm -r ./qrLogin.png')
        self.Chrome.set_network_conditions(
            offline=True, latency=5, throughput=500 * 1024)
        # self.Chrome.find_element_by_class_name(
        #     'qrcode-img').screenshot('qrLogin.png')
        self.Chrome.set_network_conditions(
            offline=False, latency=5, throughput=500 * 1024)
        time.sleep(10)
        self.intercept()

    # 开始
    def start(self, s_path=r'comment.db'):
        print('开始运行')
        self.conn = sqlite3.connect(s_path)
        self.cursor = self.conn.cursor()
        conn = sqlite3.connect(r'content.db')
        cursor = conn.cursor()
        # 提示登录
        self.login_with_qrcode()
        for row in cursor.execute('select item from {} '.format(self.url_keyword)):
            print(row)

        get_page = 0  # 查询到了多少页
        # self.Chrome.get('https://www.taobao.com')

        # time.sleep(20)
        # self.searchwords()
        # time.sleep(1)
        # self.intercept()
        # self.sales_sort()   # 按销量排序
        # try:
        #     while get_page < self.user_page:
        #         get_page += 1
        #         print('抓取第{}页:'.format(get_page))
        #         self.get_content()
        #         if get_page != self.user_page:
        #             self.click_next()
        # except Exception as err:
        #     print('出现错误:', err)
        #     self.err_log.append(err)
        #     self.cursor.close()
        #     self.conn.commit()
        #     self.conn.close()
        # else:
        #     print('抓取结束一共抓取了{}位'.format(self.order_number))
        #     self.cursor.close()
        #     self.conn.commit()
        #     self.conn.close()


if __name__ == '__main__':
    start_time = time.time()
    # 打开远程调用浏览器
    user_port = 9515
    url_keyword = '手机'
    # if '9515' not in os.popen('netstat -ano|findstr 9515').read():
    # print('打开chrome浏览器')
    open_chrome()
    # 程序开始
    browser = ItemClass(url_keyword=url_keyword)
    browser.start()

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
