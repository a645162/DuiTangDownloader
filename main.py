import settings

import os
import time

import requests

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# keyword = "orie"
# dir = "/Users/konghaomin/Downloads/duitang/"

def getDuiTangPic(url):
    content = requests.get(url).text
    soup = BeautifulSoup(content, "lxml")
    img_box = soup.find("a", attrs={"class": "img-out"})
    # print(imgBox)

    img_src = img_box['href']

    # print(src)

    text_area = soup.find("h1", attrs={"class": "js-favorite-blogtit"})
    # print(imgBox)

    text = str(text_area.get_text()).strip()
    # print(text)

    return text, img_src


def downloadDuiTang(url):
    title, url = getDuiTangPic(url)
    # print(title, url)

    # 文件名合法化
    block = "\/:*?\"<>→".strip()
    for i in block:
        title = title.replace(i, "_")

    # 获取url原始后戳名
    dot_index = url.rfind(".")
    slash_index = url.rfind("/")
    extension = ".jpg"
    if dot_index > slash_index:
        extension = url[dot_index:]

    # 防止文件名重复
    file_path1 = file_path = settings.current_dir + "/" + title
    i = 1
    while os.path.isfile(file_path1 + extension):
        file_path1 = file_path + "(" + str(i) + ")"
        i += 1

    # 下载前再次确认目录是否存在
    os.makedirs(settings.current_dir, exist_ok=True)

    # 下载
    import requests
    r = requests.get(url)
    with open(file_path1 + extension, 'wb') as f:
        f.write(r.content)


def pageDown(driver):
    js = "window.scrollTo(0, document.body.scrollHeight);"
    driver.execute_script(js)
    time.sleep(1)
    if int(driver.execute_script("return $('.blockOverlay').length")) != 0:
        driver.execute_script(
            "$('.blockOverlay')[0].remove()"
        )
        driver.execute_script(
            "$('.blockMsg')[0].remove()"
        )
    while int(driver.execute_script("return $(\".woo-loading\").length")) != 0:
        driver.execute_script(js)
        time.sleep(1)


def process(content):
    soup = BeautifulSoup(content, "lxml")

    div_src = \
        str(soup.find("div",
                      attrs={"class": "woo-swb woo-cur"}))

    url_list = []
    src_split = div_src.split("href=\"/blog/")
    for i in range(1, len(src_split)):
        current = src_split[i]
        if current.find("?id=\"") == -1:
            url_list.append("https://www.duitang.com/blog/" +
                            current[:current.find("\"")])
    # print(url_list)
    print("----------------------------------")
    print("本页解析到", len(url_list), "条记录")
    print("开始下载任务:")
    for i in range(len(url_list)):
        print("正在下载第", i + 1, "个:", url_list[i])
        try:
            downloadDuiTang(url_list[i])
        except Exception:
            print(Exception)
    print("下载完成！")
    settings.count += len(url_list)
    print("----------------------------------")


# 目录是否存在,不存在则创建
mkdir = lambda x: os.makedirs(x) if not os.path.exists(x) else True
mkdir(settings.current_dir)

# driver = webdriver.PhantomJS(
#     executable_path='/Users/konghaomin/DataScience/phantomjs-2.1.1-macosx/bin/phantomjs')

chrome_options = Options()
if settings.hide:
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(
    executable_path=settings.chromedriver_path,
    options=chrome_options)
driver.get("https://www.duitang.com/search/?kw="
           + settings.keyword + "&type=feed")

if int(driver.execute_script("return $('.zero-cont').length")) == 1:
    print("没有搜索到内容")
    driver.close()
    exit()

# 滚动到所有都加载完成
pageDown(driver)

# 加载完成，下面处理当前页
process(driver.page_source)

# 分页判断
while int(driver.execute_script("return $('.woo-nxt').length")) == 1:
    # 发现下一页按钮后，点击它进行翻页
    driver.execute_script("$('.woo-nxt')[0].click()")
    time.sleep(2)

    # 滚动到不能再滚动
    pageDown(driver)

    # 处理当前页码
    process(driver.page_source)

driver.close()

print("----------------------------------")
print("----------------------------------")
print("总计下载了", settings.count, "张图片")
