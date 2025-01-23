import requests
from bs4 import BeautifulSoup
import csv
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_page(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.RequestException as e:
        logging.error(f"请求失败: {e}")
        return None

def parse_site_a(html):
    soup = BeautifulSoup(html, 'lxml')
    data = []
    for item in soup.select('.site-a-product'):
        title = item.select_one('.title').get_text(strip=True)
        price = item.select_one('.price').get_text(strip=True)
        img = item.select_one('.image img')['src']
        data.append({'标题': title, '价格': price, '图片URL': img})
    return data

def parse_site_b(html):
    soup = BeautifulSoup(html, 'lxml')
    data = []
    for item in soup.select('.site-b-item'):
        title = item.find('h2').text.strip()
        price = item.find('span', class_='cost').text.strip()
        img = item.find('img')['data-src']
        data.append({'标题': title, '价格': price, '图片URL': img})
    return data

def save_to_csv(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['标题', '价格', '图片URL'])
        writer.writerows(data)

def crawl(url, parse_function, headers, filename):
    html = fetch_page(url, headers)
    if html:
        data = parse_function(html)
        save_to_csv(data, filename)
        logging.info(f"已保存{len(data)}条数据到{filename}")

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/90.0.4430.85 Safari/537.36'
    }

    # 初始化CSV文件
    with open('data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['标题', '价格', '图片URL'])
        writer.writeheader()

    # 爬取网站A
    site_a_url = 'https://item.jd.com/10057735724247.html'
    crawl(site_a_url, parse_site_a, headers, 'data.csv')
    time.sleep(1)  # 延时

    # # 爬取网站B
    # site_b_url = 'https://www.siteb.com/items'
    # crawl(site_b_url, parse_site_b, headers, 'data.csv')
    # time.sleep(1)  # 延时