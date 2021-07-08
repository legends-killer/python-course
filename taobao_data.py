from bs4 import BeautifulSoup  # 网页解析获取数据
import re  # 正则表达式，进行文字匹配
import urllib.request
import urllib.error
import urllib.parse  # 指定url，获取网页数据
import xlwt  # 进行excel操作
import sqlite3  # 进行SQLite操作
from urllib.parse import quote
import ssl
import xlrd
import jieba
import operator
import pandas as pd
#from wordcloud import WordCloud
from matplotlib import pyplot as plt
import pandas as pd
import re
import collections
import jieba

from pyecharts.charts import WordCloud
from pyecharts import options as opts


ssl._create_default_https_context = ssl._create_unverified_context  # 全局取消证书验证


def main(goods):
    baseurl = "https://s.taobao.com/search?q=" + goods + \
        "&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.21814703.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306"
    datalist = getData(baseurl)
    savepath = "淘宝.xls"
    saveData(datalist, savepath)


def askURL(url):
    dirt = {
        #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "cookie": "_samesite_flag_=true; cookie2=1356dde9715b6ab75d2e95eef44976ea; t=6836dca8c6f083473246d7fbf6025c42; _tb_token_=e0631be3884e6; cna=t/dqGbXj4EYCAdpLe7qcXEdK; xlly_s=1; sgcookie=E100pvt9s1Im7ps7UIVjcv4asLB7ZQ4PQx%2FtDgG0OaW9S9dCrHQC5VxI0RtXyIAEFhXdMY%2FYF7WBrqKgNwCkDZCzAQ%3D%3D; uc3=nk2=AQhkCx1v46%2BL&id2=UU6m15E7CVbilg%3D%3D&lg2=W5iHLLyFOGW7aA%3D%3D&vt3=F8dCuwOwVGcHZS3U%2BFY%3D; csg=75c0cf28; lgc=blood0852; dnk=blood0852; skt=33536523cbde2818; existShop=MTYyNTU1NzQ0NA%3D%3D; uc4=id4=0%40U2xrelcbPewbDxnpG3pYkRD8X18b&nk4=0%40A6XvLdQx%2BVrOEIrxqqkgX6sdbFI%3D; tracknick=blood0852; _cc_=WqG3DMC9EA%3D%3D; enc=%2BD8QrQHbiaihuBh5S8DnIbfJGMRrwdcpv%2FZ5hYZN9TSO85TDhTl5ngbe6Yfl7i78cl%2FkBxJOtq%2BHRE%2BJHLHBxQ%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci=120_1; thw=cn; _m_h5_tk=400b29d46ee911c6500d7754d542d452_1625592587460; _m_h5_tk_enc=140898d6590c92ca13832d4ed5ecac43; uc1=cookie14=Uoe2yIUeQsEgFw%3D%3D&cookie21=V32FPkk%2FgihF%2FS5nr3O5&cookie16=UIHiLt3xCS3yM2h4eKHS9lpEOw%3D%3D&pas=0&existShop=false; JSESSIONID=5520FE2F64B4FBB8F2D6F04275C70D17; tfstk=cN-fBb2HvCKyXG3a0KMz7m7Tevs1ZdV5Eq1yheDuVpiog19fibrFO1jHS7ZRJT1..; l=eBrNNKguj5ESFU0CBOfZFurza7PFSIRxsuPzaNbMiOCPOH5p5pdcW6tWLPY9C3FVh62JR3yFlzS9BeYBcIv4n5U62j-la_kmn; isg=BExMGmoxQHqZ71SHX0VXMOpFHax-hfAv0cZhdKYNWPeaMew7zpXAv0KD1DkJTiiH"
    }

    request = urllib.request.Request(url, headers=dirt)
    html = " "
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)

    return html


findTitle = re.compile(r'"raw_title":"(.*?)"')
findPrice = re.compile(r'"view_price":"(.*?)"')
findLoc = re.compile(r'"item_loc":"(.*?)"')
findSal = re.compile(r'"view_sales":"(.*?)"')


def getData(baseurl):
    datalist = []
    for i in range(0, 5):
        url = baseurl + str(i * 44)
        html = askURL(url)
        # 逐一解析

        title = re.findall(findTitle, html)
        price = re.findall(findPrice, html)
        locs = re.findall(findLoc, html)
        sales = re.findall(findSal, html)
        for i in range(len(title)):
            try:
                data = []
                data.append(title[i])
                data.append(price[i])
                data.append(locs[i])
                data.append(sales[i])
                datalist.append(data)
            except IndexError:
                break

    return datalist


def saveData(datalist, savepath):
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)
    col = ("product", "price", "location", "selling")
    for i in range(0, 4):
        sheet.write(0, i, col[i])
    for i in range(0, 200):
        print("第%d条" % (i + 1))
        data = datalist[i]
        for j in range(0, 4):
            sheet.write(i+1, j, data[j])

    book.save(savepath)


if __name__ == '__main__':
    goods = input("输入要搜索的商品：")
    main(quote(goods))
    # matplotlib中文显示
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['SimHei']

    # 读取数据
    file = xlrd.open_workbook('淘宝.xls')
    sheet = file.sheets()[0]
    name = sheet.col_values(0)
    price = sheet.col_values(1, 1, sheet.nrows)
    place = sheet.col_values(2, 1, sheet.nrows)

    # 价格分段
    price_range = []
    for x in price:
        price_range.append((float(x) // 100) * 100)

    # 价格分布
    plt.figure(figsize=(16, 9))
    plt.hist(price_range, bins=30, alpha=0.5, rwidth=0.8)
    plt.title('价格频率分布直方图')
    plt.xlabel('价格')
    plt.ylabel('频数')
    plt.savefig('价格分布.png')

    # 地区分布
    plt.figure(figsize=(16, 9))
    plt.hist(place, bins=11, alpha=0.5, rwidth=0.8)
    plt.title('地区频数据分布直方图')
    plt.xlabel('地区')
    plt.ylabel('频数')
    plt.savefig('地区分布.png')

    # #词云分析
    data = pd.read_excel('淘宝.xls')
    pattern = re.compile(u'\t|\n| |；|\.|。|：|：\.|-|:|\d|;|、|，|\)|\(|\?|"')
    # 将符合模式的字符去除，re.sub代表替换，把符合pattern的替换为空
    string_data = ''
    for i in data['product']:
        string_data += str(i)
    string_data = re.sub(pattern, '', string_data)

    # 3.文本分词
    seg_list_exact = jieba.cut(string_data, cut_all=False)  # 精确模式分词
    # object_list  = list(seg_list_exact) # list()函数可以把可迭代对象转为列表

    # 4.运用过滤词表优化掉常用词，比如“的”这些词，不然统计词频时会统计进去
    object_list = []

    # 读取过滤词表
    with open('./remove_words.txt', 'r', encoding="utf-8") as fp:
        remove_words = fp.read().split()

    # 循环读出每个分词
    for word in seg_list_exact:
        # 看每个分词是否在常用词表中或结果是否为空或\xa0不间断空白符，如果不是再追加
        if word not in remove_words and word != ' ' and word != '\xa0':
            object_list.append(word)  # 分词追加到列表

    # 5.进行词频统计，使用pyecharts生成词云
    # 词频统计
    word_counts = collections.Counter(object_list)  # 对分词做词频统计
    word_counts_top = word_counts.most_common(100)  # 获取前100最高频的词

    # 绘图
    # https://gallery.pyecharts.org/#/WordCloud/wordcloud_custom_mask_image
    # 去pyecharts官网找模板代码复制出来修改
    c = (
        WordCloud()
        .add("", word_counts_top)  # 根据词频最高的词
        .render("wordcloud.html")  # 生成页面
    )
