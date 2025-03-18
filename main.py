import requests as r
from tqdm import tqdm
import os


def download(url: str, fname: str):
    resp = r.get(url, stream=True)
    total = int(resp.headers.get("content-length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=fname.split("/")[-1],
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def while_get(url):
    ret = None
    while True:
        ret = r.get(url, cookies={"session": session})
        if ret.ok:
            break
        else:
            if ret.json()["message"] == "您没有权限完成此操作":
                print("请确认cookie输入是否正确！")
                exit(0)
    return ret


os.system("md download >nul 2>nul")

id = None
while id is None:
    url = input("请复制课程的链接：")
    if url.startswith("https://lnt.xmu.edu.cn/course/"):
        id = url.split("/")[4]
        break
    if id is None:
        print("不是合法链接")

session = None
print("请在课程界面执行以下js脚本获取返回内容：")
print("console.log(document.cookie)")
while session is None:
    cookie = input("输入返回内容：").replace(" ", "")
    d = cookie.split(";")
    for e in d:
        if e.startswith("session="):
            session = e[8::]
    if session is None:
        print("不是合法cookie")

data = while_get(f"https://lnt.xmu.edu.cn/api/courses/{id}/activities").json()

for e in data["activities"]:
    for i in e["uploads"]:
        reference_id = i["reference_id"]
        name = i["name"]
        content = while_get(
            f"https://lnt.xmu.edu.cn/api/uploads/reference/{reference_id}/url"
        ).json()
        url = content["url"]
        download(url, f"./download/{name}")
