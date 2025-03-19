import time
import requests as r
import os
import re
import random
from Crypto.Cipher import AES
import base64

username = input("学号：")
passwd = input("密码：")

regex1 = '<input[^>]*?name="execution"[^>]*?value="([^"]*)"[^>]*?>'
regex2 = '<input[^>]*?id="pwdEncryptSalt"[^>]*?value="([^"]*)"[^>]*?>'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
aes_chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"


class Encrypt:
    def __init__(self, key, iv):
        self.key = key.encode("utf-8")
        self.iv = iv.encode("utf-8")

    # @staticmethod
    def pkcs7padding(self, text):
        """明文使用PKCS7填充"""
        bs = 16
        length = len(text)
        bytes_length = len(text.encode("utf-8"))
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        padding_text = chr(padding) * padding
        self.coding = chr(padding)
        return text + padding_text

    def aes_encrypt(self, content):
        """AES加密"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(content_padding.encode("utf-8"))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding="utf-8")
        return result

    def aes_decrypt(self, content):
        """AES解密"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        content = base64.b64decode(content)
        text = cipher.decrypt(content).decode("utf-8")
        return text.rstrip(self.coding)


def randomString(n):
    ret = ""
    for i in range(n):
        ret += random.choice(aes_chars)
    return ret


session = r.session()


def while_get(url):
    resp = session.get(url, headers=headers)
    headers["Referer"] = resp.url
    return resp


captcha = while_get(
    f"https://ids.xmu.edu.cn/authserver/checkNeedCaptcha.htl?username={username}_={int(time.time()*1000)}"
).json()

if captcha["isNeed"]:
    raise ("账号被风控无法登录")

url = while_get("https://lnt.xmu.edu.cn/").url
service = url[url.find("service=") + 8 : :]
# print(f"service={service}")

resp = while_get(
    f"https://ids.xmu.edu.cn/authserver/login?type=userNameLogin&service={service}"
)

cookies = resp.cookies
s = resp.text
execution = re.search(regex1, s).groups()[0]
# print(f"execution={execution}")
salt = re.search(regex2, s).groups()[0]
# print(f"salt={salt}")
passStr = randomString(64) + passwd
iv = randomString(16)
aes = Encrypt(salt, iv)
saltPassword = aes.aes_encrypt(passStr)

data = {
    "username": username,
    "password": saltPassword,
    "captcha": "",
    "_eventId": "submit",
    "cllt": "userNameLogin",
    "dllt": "generalLogin",
    "lt": "",
    "execution": execution,
}


headers["Referer"] = f"https://ids.xmu.edu.cn/authserver/login?service={service}"
headers["Origin"] = "https://ids.xmu.edu.cn"
url = f"https://ids.xmu.edu.cn/authserver/login?type=service={service}"

res = session.post(
    url, headers=headers, data=data, cookies=cookies, allow_redirects=True
)

result = r.utils.dict_from_cookiejar(res.cookies)


def get_session():
    if "session" in result:
        return result["session"]
    else:
        print("没有获取到session，最后终止于：")
        print(res.url)
        raise
