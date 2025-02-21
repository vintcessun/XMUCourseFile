import chromedriver_autoinstaller
import sys
import os
from selenium import webdriver


def download_chromedriver():
    # 自动下载并安装与当前Chrome版本匹配的ChromeDriver
    chromedriver_autoinstaller.install()


def main():
    # 检查是否已安装 Chrome 浏览器
    try:
        # 验证 Chrome 是否安装
        browser_version = webdriver.Chrome().capabilities["browserVersion"]
        print(f"当前安装的 Chrome 版本: {browser_version}")
    except Exception as e:
        print("未能检测到 Chrome 浏览器。请确保已安装 Chrome 浏览器。")
        sys.exit(1)

    # 下载并安装匹配的 ChromeDriver
    download_chromedriver()
    print("已自动下载并安装与当前 Chrome 版本匹配的 ChromeDriver。")

    # 创建 Chrome 浏览器实例并启动
    try:
        driver = webdriver.Chrome()
        driver.get("https://www.baidu.com")
        print("ChromeDriver 安装成功，可以使用 Selenium 控制 Chrome 浏览器。")
        driver.quit()
    except Exception as e:
        print("启动浏览器失败。")
        sys.exit(1)


if __name__ == "__main__":
    main()
