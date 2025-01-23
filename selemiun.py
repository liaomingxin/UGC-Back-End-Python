from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def crawl_from_tbtm(url):
    time_avg = 0
    num = 1

    for i in range(num):
        start = time.time()

        # 设置 ChromeDriver 的路径
        chrome_driver_path = '/opt/homebrew/bin/chromedriver'

        # 创建 ChromeOptions 对象，可用于设置浏览器的一些选项
        chrome_options = Options()
        # 设置加载策略为 eager
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument('--headless')

        # 创建 Service 对象，用于启动 ChromeDriver 服务
        service = Service(chrome_driver_path)

        # 启动 Chrome 浏览器
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # 访问网页
            driver.get(url)

            # 使用 WebDriverWait 等待元素可见，最多等待 10 秒
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'h1'))  # 这里等待页面中第一个 h1 元素可见，可根据需要修改
            )

            # print(element.text)

            # title
            elements = driver.find_elements(By.CLASS_NAME, 'mainTitle--O1XCl8e2')
            if elements:
                title = elements[0].text
                print(title)

            # price
            elements = driver.find_elements(By.CLASS_NAME, 'text--Mdqy24Ex')
            if elements:
                price = elements[0].text
                print(price)

            # img
            elements = driver.find_elements(By.CLASS_NAME, 'mainPicWrap--Ns5WQiHr')
            if elements:
                img = elements[0].find_element(By.TAG_NAME, 'img').get_attribute('src')
                print(img)


        finally:
            # 关闭浏览器
            driver.quit()

        end = time.time()
        time_avg += end - start

    print(time_avg / num)

def crawl_from_amazon(url):
    time_avg = 0
    num = 10

    for i in range(num):
        start = time.time()

        # 设置 ChromeDriver 的路径
        chrome_driver_path = '/opt/homebrew/bin/chromedriver'

        # 创建 ChromeOptions 对象，可用于设置浏览器的一些选项
        chrome_options = Options()
        # 设置加载策略为 eager
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument('--headless')

        # 创建 Service 对象，用于启动 ChromeDriver 服务
        service = Service(chrome_driver_path)

        # 启动 Chrome 浏览器
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # 访问网页
            driver.get(url)

            # 使用 WebDriverWait 等待元素可见，最多等待 10 秒
            # element = WebDriverWait(driver, 10).until(
            #     EC.visibility_of_element_located((By.TAG_NAME, 'h1'))  # 这里等待页面中第一个 h1 元素可见，可根据需要修改
            # )
            # print(element.text)

            # title
            elements = driver.find_elements(By.ID, 'title')
            if elements:
                title = elements[0].text
                print(title)

            # price
            price_whole = driver.find_elements(By.CLASS_NAME, 'a-price-whole')[0].text
            price_fraction = driver.find_elements(By.CLASS_NAME, 'a-price-fraction')[0].text
            print(price_whole + '.' + price_fraction)

            # img
            elements = driver.find_elements(By.CLASS_NAME, 'a-dynamic-image')
            if elements:
                img = elements[0].get_attribute('src')
                print(img)

        finally:
            # 关闭浏览器
            driver.quit()

        end = time.time()
        time_avg += end - start

    print(time_avg / num)


def crawl_from_temu(url):
    time_avg = 0
    num = 10

    for i in range(num):
        start = time.time()

        # 设置 ChromeDriver 的路径
        chrome_driver_path = r'D:\devolopment_tools\Cursor\workspace\UGC-Back-End\src\main\resources\chromedriver.exe'

        # 创建 ChromeOptions 对象，可用于设置浏览器的一些选项
        chrome_options = Options()
        # 设置加载策略为 eager
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument('--headless')

        # 创建 Service 对象，用于启动 ChromeDriver 服务
        service = Service(chrome_driver_path)

        # 启动 Chrome 浏览器
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # 访问网页
            driver.get(url)

            # 使用 WebDriverWait 等待元素可见，最多等待 10 秒
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.TAG_NAME, 'h1'))  # 这里等待页面中第一个 h1 元素可见，可根据需要修改
            )
            print(element.text)

            # title
            elements = driver.find_elements(By.ID, 'title')
            if elements:
                title = elements[0].text
                print(title)

            # price
            price_whole = driver.find_elements(By.CLASS_NAME, 'a-price-whole')[0].text
            price_fraction = driver.find_elements(By.CLASS_NAME, 'a-price-fraction')[0].text
            print(price_whole + '.' + price_fraction)

            # img
            elements = driver.find_elements(By.CLASS_NAME, 'a-dynamic-image')
            if elements:
                img = elements[0].get_attribute('src')
                print(img)

        finally:
            # 关闭浏览器
            driver.quit()

        end = time.time()
        time_avg += end - start

    print(time_avg / num)

if __name__ == '__main__':
    tbtm_url = 'https://detail.tmall.com/item.htm?id=837755502062&spm=608.29877528.3261491990.1.764d4d19saubWR&fromChannel=bybtChannel&fpChannel=101&fpChannelSig=38f2a02b8fe76b1d74e3a863a77e00c77520bbbf&skuId=5765196134947&pisk=g5uZrpbcrFLa590wnW4VzXJ4EhzTRPvWnqwbijc01R2il5M4gvDICo2XXxrqhvEm5PGsLtDnwRATShe4iJck6RaMHr8qpfk_GPNsivP4MG2cjPq3tSVcnR0qMZPmixdThCKI6fUYoL9S3UGt6rJ7L60amejn9SQGjHZGLCeCHL9WPEShyJ92FAaE-d_3a740sobGtBP8NZ4cjNAUKSPRmOD0oBRUi7b0n5bcKJVTZrX0INXh-7NznS40ikAUMJjgorceJAHvE7EMiszZZH84hlyosJ7rw2PiWGhaLMsK8YruETwFoZ0UsX98pn_yc8m8CuwKKe_auXVqU7kNKpzmTV3zxVvduYkEqyPKvKS4Umcs2mqesFcU7RrrRk1G0PomBqrtbsd-tPDK28EMvpFE54Z4ekWHIXGUIuoqCpQ0C0lnLugCdaanZDzF4yXYt0fSkcWc0lVLT8OeT4zWaG_LMp9ADiE3qWyW1iIADlVQT8OetiIYXZFUFCsh.'
    crawl_from_tbtm(tbtm_url)

    amazon_url = 'https://www.amazon.com/dp/B0DMN3WFGC/ref=sr_1_1_sspa?_encoding=UTF8&content-id=amzn1.sym.860dbf94-9f09-4ada-8615-32eb5ada253a&dib=eyJ2IjoiMSJ9.HVZ5sdFbAoRVrXOM_x3kFixfJ6ZJoqEd_XJmNh2p5QCPX_OfYOSv83scETpZBmcAz2f9Dv9ecmSB7wNgpDPj015NOrl-DCgQVZTwRQRWRG4kzobMKU0nav2VXpHeLQ1YIQEpdamf1E_QefEbVz41nwc57KIhvTRXx9MvidL8eFbs1MjPL_ZDXvsKveV-mIEyF17fEUoNTEiaynoZAYZMJSrzlmCQCNxFZ89LNcddkWAPqQHz5bCLugdDgjyy5dzddgTsFqWQWdkZp9D7VfZfpm_bem8ofi5Im-A-1ugm1xI.A7wrr4BwttVb7otVdxcV6pTzOqNbmqJfMBCj6iOaVLs&dib_tag=se&keywords=gaming&pd_rd_r=3fbee587-33f5-4a79-8946-2748d7462c6b&pd_rd_w=HVZQE&pd_rd_wg=jsBML&pf_rd_p=860dbf94-9f09-4ada-8615-32eb5ada253a&pf_rd_r=25DJQEPE5RATJCW2D32Z&qid=1737465755&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1'
    # crawl_from_amazon(amazon_url)

    temu_url = 'https://www.temu.com/elegant-9pcs-modern-dining-set-for-8-sleek-rectangular-tempered-glass-table-with-golden-metal-legs-upholstered-chairs-easy-to-clean--for-kitchen-dining-room-dining-table-decoration-g-601099923171305.html?_oak_mp_inf=EOnPlNun1ogBGhZmbGFzaF9zYWxlX2xpc3RfNWF1bG94IMiKw8nIMg%3D%3D&top_gallery_url=https%3A%2F%2Fimg.kwcdn.com%2Fproduct%2Ffancy%2Fa2d5e5db-2670-4885-8a24-9c4e742041be.jpg&spec_gallery_id=3423341366&refer_page_sn=10132&refer_source=0&freesia_scene=116&_oak_freesia_scene=116&_oak_rec_ext_1=NTg4OTc&refer_page_el_sn=201401&_x_channel_src=1&_x_channel_scene=spike&_x_sessn_id=d9x4cvqhd9&refer_page_name=lightning-deals&refer_page_id=10132_1737468463003_chvefmvwui'
    # crawl_from_temu(temu_url)
