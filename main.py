import json
import os
import time
from urllib import parse
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

# 账户名和密码，自己填写
username = "34520242200990"
passwd = "Cgs761028!"

home_page = "https://course.xmu.edu.cn/"
select_video_js = "const sleep=(delay)=>new Promise((resolve)=>setTimeout(resolve,delay));var a=document.getElementsByClassName('mvp-ant-popover-inner-content')[1].getElementsByTagName('div')[0].getElementsByTagName('div');for(var i=0;i<a.length;i++){a[i].click();await sleep(1000)}"
select_file_js = "const sleep=(delay)=>new Promise((resolve)=>setTimeout(resolve,delay));var e=document.getElementsByClassName('activity-details')[0].getElementsByClassName('attachment-row');for(var i=0;i<e.length;i++){e[i].click();await sleep(7000);document.getElementsByClassName('right close')[1].click()}"
go_login_js = "go_login('https://c-identity.xmu.edu.cn/auth/realms/xmu/protocol/openid-connect/auth?client_id=new-menhu&response_type=code&redirect_uri=http://course.xmu.edu.cn/api/callback&scope=openid&realms=xmu',1)"
# 开启监听
caps = {
    "browserName": "chrome",
    "goog:loggingPrefs": {"performance": "ALL"},
}
browser = webdriver.Chrome(desired_capabilities=caps)

# 进行登录操作
browser.get(home_page)
# 进入登录界面
browser.execute_script(go_login_js)
# 等待页面变化
while browser.current_url == home_page:
    pass
time.sleep(1)
# 进行登录操作
if username == "" or passwd == "":
    pass
else:
    browser.execute_script("document.getElementById('userNameLogin_a').click()")
    browser.find_element(By.ID, "username").send_keys(username)
    browser.find_element(By.ID, "password").send_keys(passwd)
    browser.execute_script("document.getElementById('login_submit').click()")
# 等待登陆成功
while browser.current_url != home_page:
    pass
# 进入课程界面
browser.get("https://lnt.xmu.edu.cn/user/courses")
print("请打开课程的界面等待页面加载完毕后按下任意键")
os.system("pause>nul")
content_element = browser.find_elements(By.CLASS_NAME, "module-block")[0]
all_lis = content_element.find_elements(By.TAG_NAME, "li")
for e in all_lis:
    e.click()
    if len(browser.find_elements(By.TAG_NAME, "video")) != 0:
        browser.find_elements(By.CLASS_NAME, "mvp-controls-item")[1].click()
        time.sleep(1)
        # browser.execute_script(select_video_js)
    else:
        while 1:
            try:
                browser.execute_script(select_file_js)
                break
            except:
                pass
        time.sleep(1)
        browser.execute_script(
            "document.getElementsByClassName('right close')[1].click()"
        )
    time.sleep(5)
"""
top_lis = []
for e in all_lis:
    if e.get_attribute('ng-repeat') == 'module in course.modules':
        top_lis.append(e)
for e in top_lis:
    title = e.find_element(By.CLASS_NAME,'module-title')[0].get_attribute('innerText')
"""


def filter_type(_type: str):
    types = [
        "application/javascript",
        "application/x-javascript",
        "text/css",
        "webp",
        "image/png",
        "image/gif",
        "image/jpeg",
        "image/x-icon",
        "application/octet-stream",
    ]
    if _type not in types:
        return True
    return False


download_list = []
"""
每一个元素只能是以下两种情况
{"url":file_url,"isFile":True,"fileName":filename}
{"url":online_url,"isFile":False}
"""

performance_log = browser.get_log("performance")
for packet in performance_log:
    message = json.loads(packet.get("message")).get("message")
    if message.get("method") != "Network.responseReceived":
        continue
    packet_type = message.get("params").get("response").get("mimeType")
    if not filter_type(_type=packet_type):
        continue
    requestId = message.get("params").get("requestId")
    url = message.get("params").get("response").get("url")
    try:
        resp = browser.execute_cdp_cmd(
            "Network.getResponseBody", {"requestId": requestId}
        )
        if url.find("pdf-viewer") != -1:
            file_url = parse.parse_qs(parse.urlparse(url).query)["file"][0]
            filename = parse.parse_qs(parse.urlparse(file_url).query)["name"][0]
            download_list.append(
                {"url": file_url, "isFile": True, "fileName": filename}
            )
        elif url.startswith("https://wps.xmu.edu.cn"):
            # TODO:希望以后能够通过各种方法下载下来pptx之类的文件
            download_list.append({"url": url, "isFile": False})
    except WebDriverException:
        pass

print(download_list)
