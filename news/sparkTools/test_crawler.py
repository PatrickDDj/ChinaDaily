import os
import datetime
import re
import urllib
import requests
from lxml import html
from bs4 import BeautifulSoup


def crawl():
    # 创建文件夹（依据日期）
    date = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) + '-' + str(datetime.datetime.now().day)
    # 文件夹路径
    filePath = 'static/news/' + date
    # 检验文件夹是否存在
    if os.path.exists(filePath) is False:
        os.makedirs(filePath)

    urlList = []
    box = []
    urlList.append('http://en.people.cn/90785/index.html')
    urlList.append('http://en.people.cn/90882/index.html')
    urlList.append('http://en.people.cn/business/index.html')
    urlList.append('http://en.people.cn/90777/index.html')
    urlList.append('http://en.people.cn/90786/index.html')
    urlList.append('http://en.people.cn/202936/index.html')
    urlList.append('http://en.people.cn/90779/index.html')
    urlList.append('http://en.people.cn/90782/index.html')
    urlList.append('http://en.people.cn/90882/index.html')

    for url in urlList:
        response = urllib.request.urlopen(url)
        html = response.read()
        data = html.decode('utf-8')
        soup = BeautifulSoup(data)

        for item in soup.find_all("a"):
            if item.string is None:
                continue
            else:
                if str(item.get("href")).find("/n3") != -1:
                    if 'http://en.people.cn' + str(item.get("href")) not in box:
                        box.append('http://en.people.cn' + str(item.get("href")))

    for url in box:
        try:
            response = urllib.request.urlopen(url)
            html = response.read()
            data = html.decode('utf-8')
            soup = BeautifulSoup(data)
        except:
            print('getting url failed:' + url)

        # 获取标题
        title = soup.title.string
        # 爬取网页并进行处理
        # 处理script和标签
        [script.extract() for script in soup.findAll('script')]
        [style.extract() for style in soup.findAll('style')]
        reg1 = re.compile("<[^>]*>")
        content = reg1.sub('', soup.prettify())
        # 处理空格和回车符
        s = content.split()
        contentFinal = ' '.join(s)

        # 创建txt文本路径
        # title.replace('"',' ')
        wordPath = filePath + '/' + title + '.txt'
        # 检验文件是否重名且合法
        if os.path.exists(wordPath) is False:
            try:
                txt1 = open(wordPath, 'w', encoding='utf-8')
                # 写入文本
                txt1.write(contentFinal)
                txt1.close()
            except OSError:
                print('invalid path' + wordPath)

    for filepath, dirnames, filenames in os.walk(filePath):
        for filename in filenames:
            fileP = os.path.join(filepath, filename)
            if fileP.find('.txt') is -1:
                os.remove(fileP)
    print('creat file and txt successfully')
    # return filePath
