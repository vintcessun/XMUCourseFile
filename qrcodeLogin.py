# conda activate selenium4
import time
import requests as r
import re
from tqdm import tqdm
from pyzbar.pyzbar import decode
from PIL import Image
import qrcode
import os

regex = '<input[^>]*?name="execution"[^>]*?value="([^"]*)"[^>]*?>'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
session = r.session()


def show_code(url):
    os.system("cls")
    download(
        url,
        "qrcode.png",
    )
    barcode_url = ""
    barcodes = decode(Image.open("./qrcode.png"))
    for barcode in barcodes:
        barcode_url = barcode.data.decode("utf-8")
    os.remove("qrcode.png")
    qr = qrcode.QRCode()
    qr.add_data(barcode_url)
    # print(barcode_url)
    qr.print_ascii(invert=True)


def download(url: str, fname: str):
    resp = session.get(url, headers=headers)
    with open(fname, "wb") as code:
        code.write(resp.content)


def while_get(url):
    resp = session.get(url, headers=headers)
    headers["Referer"] = resp.url
    return resp


url = while_get("https://lnt.xmu.edu.cn/").url
service = url[url.find("service=") + 8 : :]

resp = while_get(
    f"https://ids.xmu.edu.cn/authserver/login?type=qrLogin&service={service}"
)
s = resp.text[resp.text.find("qrLoginForm") : :]
execution = re.search(regex, s).groups()[0]

qrcode_id = while_get(
    f"https://ids.xmu.edu.cn/authserver/qrCode/getToken?ts={int(time.time()*1000)}"
).text

show_code(f"https://ids.xmu.edu.cn/authserver/qrCode/getCode?uuid={qrcode_id}")

while True:
    ret = while_get(
        f"https://ids.xmu.edu.cn/authserver/qrCode/getStatus.htl?ts={int(time.time()*1000)}&uuid={qrcode_id}"
    ).text
    if ret == "0":
        # print("等待中")
        pass
    elif ret == "1":
        # print("请求成功")
        break
    elif ret == "2":
        # print("已扫描二维码")
        pass
    elif ret == "3":
        # print("二维码已失效")
        qrcode_id = while_get(
            f"https://ids.xmu.edu.cn/authserver/qrCode/getToken?ts={int(time.time()*1000)}"
        ).text
        show_code(f"https://ids.xmu.edu.cn/authserver/qrCode/getCode?uuid={qrcode_id}")

data = {
    "lt": "",
    "uuid": qrcode_id,
    "cllt": "qrLogin",
    "dllt": "generalLogin",
    "execution": execution,
    "_eventId": "submit",
    "rmShown": "1",
}

res = session.post(
    f"https://ids.xmu.edu.cn/authserver/login?display=qrLogin&service={service}",
    data=data,
    headers=headers,
)

result = r.utils.dict_from_cookiejar(res.cookies)


def get_session():
    if "session" in result:
        return result["session"]
    else:
        print("没有获取到session，最后终止于：")
        print(res.url)
        raise
