# import os
# import time

# import requests
# from bs4 import BeautifulSoup

# def crawl_form_ebay(url):
#     time_avg = 0
#     num = 1

#     for i in range(num):
#         start = time.time()

#         res = requests.get(url)
#         res.encoding = 'utf-8'

#         soup = BeautifulSoup(res.text, 'lxml')
#         # print(soup)

#         # title
#         title_h1 = soup.select('.x-item-title__mainTitle')[0]
#         if title_h1:
#             title = title_h1.select('.ux-textspans')[0].text
#             print(title)

#         # price
#         price_span = soup.select('.ux-labels-values__values-content')[0]
#         if price_span:
#             price = price_span.select('.ux-textspans')[0].text
#             print(price)

#         # img
#         img_div = soup.select('.ux-image-carousel-item')[0]
#         if img_div:
#             img = img_div.find('img')['src']
#             print(img)

#         end = time.time()
#         time_avg += end - start

#     print(time_avg / num)


# if __name__ == '__main__':
#     ebay_url = "https://www.ebay.com/itm/235911315652?_skw=Jordan+1+Retro+OG+High+UNC+Toe&epid=14057802542&itmmeta=01JJ3C4CGYG84A1NQSA5T71EG7&hash=item36ed6900c4:g:NjEAAOSwuDJnhA~-&itmprp=enc%3AAQAJAAABACodCO1vSDjg2xNOt8By6oDE42xILehKBbdrN8Oj93PEECaLWzdCowwRmkg%2FtJVPpZjILKM3v%2FEWpyeT8hPxIyR7%2BFaMYhpWwUs7%2BjuHI4qYrW34afcNP6MOHpfxh9kQg5NYjOG%2FfmCluZo9QvV8SypclwMwy6KNBrtpeoKB8IFn6Fk2i7lAcmZgvs0ZWhzszep9s%2BaAJucTVxeHFeWXWZ9owN6FRZ1oK0fGnumdEeBBgZsyS8hHGxvwANBOCw%2BcCTrhmQlqMYR2Xd0WI5W2TH5xghigZavrtp6iwAQxAz5gm26DC%2BP2XfWzLdUqNGGRthu4eVf27eHawSXkeoL1SUs%3D%7Ctkp%3ABFBMysiR7JBl"
#     crawl_form_ebay(ebay_url)

import requests
from bs4 import BeautifulSoup
import time
import logging
import csv

def crawl_from_ebay(url, num=1, filename='ebay_data.csv'):
    time_avg = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/90.0.4430.85 Safari/537.36'
    }

    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 打开CSV文件
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['标题', '价格', '图片URL'])

        for i in range(num):
            start = time.time()
            try:
                res = requests.get(url, headers=headers, timeout=10)
                res.raise_for_status()
                res.encoding = 'utf-8'
            except requests.RequestException as e:
                logging.error(f"请求失败: {e}")
                continue

            soup = BeautifulSoup(res.text, 'lxml')

            # 提取标题
            try:
                title = soup.select_one('.x-item-title__mainTitle .ux-textspans').get_text(strip=True)
                logging.info(f"标题: {title}")
            except AttributeError:
                logging.warning("标题提取失败")
                title = 'N/A'

            # 提取价格
            try:
                price = soup.select_one('.ux-labels-values__values-content .ux-textspans').get_text(strip=True)
                logging.info(f"价格: {price}")
            except AttributeError:
                logging.warning("价格提取失败")
                price = 'N/A'

            # 提取图片
            try:
                img = soup.select_one('.ux-image-carousel-item img')['src']
                logging.info(f"图片URL: {img}")
            except (AttributeError, KeyError):
                logging.warning("图片提取失败")
                img = 'N/A'

            # 写入CSV
            writer.writerow([title, price, img])

            end = time.time()
            time_avg += end - start

            # 控制爬取频率
            time.sleep(1)

        if num > 0:
            logging.info(f"平均爬取时间: {time_avg / num:.2f}秒")

if __name__ == '__main__':
    ebay_url = "https://www.ebay.com/itm/235911315652?_skw=Jordan+1+Retro+OG+High+UNC+Toe&epid=14057802542&itmmeta=01JJ3C4CGYG84A1NQSA5T71EG7&hash=item36ed6900c4:g:NjEAAOSwuDJnhA~-&itmprp=enc%3AAQAJAAABACodCO1vSDjg2xNOt8By6oDE42xILehKBbdrN8Oj93PEECaLWzdCowwRmkg%2FtJVPpZjILKM3v%2FEWpyeT8hPxIyR7%2BFaMYhpWwUs7%2BjuHI4qYrW34afcNP6MOHpfxh9kQg5NYjOG%2FfmCluZo9QvV8SypclwMwy6KNBrtpeoKB8IFn6Fk2i7lAcmZgvs0ZWhzszep9s%2BaAJucTVxeHFeWXWZ9owN6FRZ1oK0fGnumdEeBBgZsyS8hHGxvwANBOCw%2BcCTrhmQlqMYR2Xd0WI5W2TH5xghigZavrtp6iwAQxAz5gm26DC%2BP2XfWzLdUqNGGRthu4eVf27eHawSXkeoL1SUs%3D%7Ctkp%3ABFBMysiR7JBl"
    crawl_from_ebay(ebay_url, num=1)



