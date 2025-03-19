import requests as r
from tqdm import tqdm
import os

from qrcodeLogin import get_session

# from passwdLogin import get_session


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


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
        ret = r.get(url, cookies={"session": session}, headers=headers)
        if ret.ok:
            break
        else:
            try:
                if ret.json()["message"] == "您没有权限完成此操作":
                    print("请确认cookie输入是否正确！")
                    exit(0)
            except:
                print(ret.text)
                print("无效访问")
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

session = get_session()

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
