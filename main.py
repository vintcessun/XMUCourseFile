import json
import os
import time
import shutil
from urllib import parse
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from fuzzywuzzy import process
import logging

# 账户名和密码，自己填写
username = ""
passwd = ""

logging.basicConfig(
    format="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",
    level=logging.INFO,
)

home_page = "https://course.xmu.edu.cn/"
select_video_js = "const sleep=(delay)=>new Promise((resolve)=>setTimeout(resolve,delay));var a=document.getElementsByClassName('mvp-ant-popover-inner-content')[1].getElementsByTagName('div')[0].getElementsByTagName('div');for(var i=0;i<a.length;i++){a[i].click();await sleep(1000)}"
select_file_js = "const sleep=(delay)=>new Promise((resolve)=>setTimeout(resolve,delay));var e=document.getElementsByClassName('activity-details')[0].getElementsByClassName('attachment-row');var ret=[];for(var i=0;i<e.length;i++){ret.push(e[i].getElementsByTagName('div')[0].textContent);e[i].click();await sleep(10000);document.getElementsByClassName('right close')[1].click()}return ret;"
go_login_js = "go_login('https://c-identity.xmu.edu.cn/auth/realms/xmu/protocol/openid-connect/auth?client_id=new-menhu&response_type=code&redirect_uri=http://course.xmu.edu.cn/api/callback&scope=openid&realms=xmu',1)"
# 开启监听
caps = {
    "browserName": "chrome",
    "goog:loggingPrefs": {"performance": "ALL"},
}
download_list = []
"""
每一个元素只能是以下两种情况
{"url":file_url,"isFile":True,"fileName":filename}
{"url":online_url,"isFile":False}
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


def update_download_list():
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
            elif url.startswith("https://wps.xmu.edu.cn/weboffice/office/p"):
                # TODO:希望以后能够通过各种方法下载下来pptx之类的文件
                download_list.append({"url": url, "isFile": False})
            elif url.find("download-url") != -1:
                file_url = json.loads(resp["body"])["url"]
                filename = parse.parse_qs(parse.urlparse(file_url).query)["name"][0]
                download_list.append(
                    {"url": file_url, "isFile": True, "fileName": filename}
                )
        except WebDriverException:
            pass


browser = webdriver.Chrome(desired_capabilities=caps)
browser.set_script_timeout(1200)

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
    print("请扫码后按下任意键……")
    os.system("pause>nul")
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
print("请打开课程的界面等待页面加载完毕后按下任意键……")
os.system("pause>nul")
content_element = browser.find_elements(By.CLASS_NAME, "module-block")[0]
all_lis = content_element.find_elements(By.TAG_NAME, "li")
all_lis[0].find_elements(By.XPATH, "./*")[0].click()
time.sleep(1)
dir_list = []
file_dir_list = {}  # 格式{'filename':[dir1,dir2,...]}
dir_list.append("download/" + browser.title.replace(" - 课程中心", ""))
dir_list.append("Error")
for e in all_lis:
    logging.info(f"点击元素{e}")
    title = e.find_elements(By.XPATH, "./*")[0].text
    try:
        (
            e.find_elements(By.XPATH, "./*")[0]
            .find_elements(By.XPATH, "./*")[0]
            .find_elements(By.XPATH, "./*")[1]
        ).click()
    except:
        e.find_elements(By.XPATH, "./*")[0].click()
    if len(e.find_elements(By.XPATH, "./*")) == 1:
        dir_list.append(title)
        time.sleep(5)
        logging.info("需要获取资源")
        parent_path = "./" + "/".join(dir_list)
        os.system(f'md "{parent_path}"')
        logging.info(f"创建目录{parent_path}")
        if len(browser.find_elements(By.TAG_NAME, "video")) != 0:
            logging.info("发现视频")
            titles = browser.find_elements(By.CLASS_NAME, "activity-title")
            exact_title = None
            for i in titles:
                if i.tag_name == "div":
                    exact_title = i
                    break
            file = exact_title.text + ".mp4"
            if not file in file_dir_list:
                file_dir_list[file] = []
            file_dir_list[file].append(parent_path + "/" + file)
        else:
            logging.info("未发现视频")
            ret = None
            while True:
                try:
                    ret = browser.execute_script(select_file_js)
                    break
                except:
                    logging.warning("执行选择脚本出现错误，刷新页面后重试")
                    browser.refresh()
                    time.sleep(1)
            for i in ret:
                file = i.replace("\n", "").replace(" ", "")
                if not file in file_dir_list:
                    file_dir_list[file] = []
                file_dir_list[file].append(parent_path + "/" + file)
        update_download_list()
        dir_list.pop()
    else:
        dir_list.pop()
        logging.info(f"识别到目录：{title}")
        dir_list.append(title)

new = []
for e in download_list:
    if not e in new:
        new.append(e)

download_list = new

other_links = []
for e in download_list:
    if e["isFile"]:
        logging.info(f'"{e["url"]}"=>"{e["fileName"]}"')
        file = e["fileName"].replace("\n", "").replace(" ", "")
        if not file in file_dir_list:
            new_file = process.extractOne(file, file_dir_list.keys())[0]
            logging.warning(f"{file}不存在，自动矫正为{new_file}")
            file = new_file
        logging.info(f'curl "{e["url"]}" -o "{file}"')
        os.system(f'curl "{e["url"]}" -o "{file}"')
        for i in file_dir_list[file]:
            shutil.copyfile(file, i)
        os.remove(file)
    else:
        other_links.append(e["url"])

other_txt = "./" + dir_list[0] + "/others.txt"
f = open(other_txt, "w")
for e in other_links:
    f.write(f"{e}\n")

f.close()
browser.close()


def remove_empty_folders(directory):
    # 遍历目录及其子目录
    for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
        # 对每一个子目录进行检查
        for dirname in dirnames:
            dir_to_check = os.path.join(dirpath, dirname)
            # 如果子目录为空，删除它
            if not os.listdir(dir_to_check):
                os.rmdir(dir_to_check)
                logging.warning(f"已删除空文件夹: {dir_to_check}")


remove_empty_folders(dir_list[0])
