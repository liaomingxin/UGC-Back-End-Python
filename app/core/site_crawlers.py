from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_crawler import BaseCrawler
import requests
from bs4 import BeautifulSoup
from app.utils.logger import setup_logger
from app.models.schemas import ProductDTO
import re
import time

# 初始化日志记录器
logger = setup_logger()

class TaobaoTmallCrawler(BaseCrawler):
    """淘宝/天猫爬虫"""
    
    def extract_title(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'mainTitle--O1XCl8e2')
        return elements[0].text if elements else ""
        
    def extract_price(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'text--Mdqy24Ex')
        return elements[0].text if elements else ""
        
    def extract_image(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'mainPicWrap--Ns5WQiHr')
        if elements:
            img = elements[0].find_element(By.TAG_NAME, 'img')
            return img.get_attribute('src')
        return ""

class AmazonCrawler(BaseCrawler):
    """亚马逊爬虫"""
    
    def extract_title(self, driver):
        elements = driver.find_elements(By.ID, 'title')
        return elements[0].text if elements else ""
        
    def extract_price(self, driver):
        try:
            price_whole = driver.find_elements(By.CLASS_NAME, 'a-price-whole')[0].text
            price_fraction = driver.find_elements(By.CLASS_NAME, 'a-price-fraction')[0].text
            return f"{price_whole}.{price_fraction}"
        except:
            return ""
            
    def extract_image(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'a-dynamic-image')
        if elements:
            return elements[0].get_attribute('src')
        return ""

class TemuCrawler(BaseCrawler):
    """Temu爬虫"""
    
    def extract_title(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'goods-title')
        return elements[0].text if elements else ""
        
    def extract_price(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'cur-price')
        return elements[0].text if elements else ""
        
    def extract_image(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'goods-image')
        if elements:
            img = elements[0].find_element(By.TAG_NAME, 'img')
            return img.get_attribute('src')
        return ""

class LazadaCrawler(BaseCrawler):
    """Lazada爬虫"""
    
    def extract_title(self, driver):
        # 滚动页面以加载更多内容
        for _ in range(2):  # 根据需要调整滚动次数
            self.scroll_to_bottom(driver)  # Use self to call the method
        elements = driver.find_elements(By.CLASS_NAME, 'pdp-mod-product-badge-title')
        if elements:
            title = elements[0].text
            print(title)
    
    def scroll_to_bottom(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 等待新内容加载

    def extract_price(self, driver):
        div_element = driver.find_elements(By.CLASS_NAME, 'pdp-product-price')[0]
        span_element = div_element.find_elements(By.TAG_NAME, 'span')
        if span_element:
            price = span_element[0].text
            print(price)

        
    def extract_image(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'pdp-mod-common-image')
        if elements:
            return elements[0].get_attribute('src')
        return ""

class EbayCrawler(BaseCrawler):
    """eBay爬虫实现"""
    
    def crawl(self, url: str):
        """重写基类的爬取方法，使用 requests + BeautifulSoup"""
        try:
            res = requests.get(url)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'lxml')
            
            # 提取标题
            title = ""
            title_h1 = soup.select('.x-item-title__mainTitle')
            if title_h1 and len(title_h1) > 0:
                title_span = title_h1[0].select('.ux-textspans')
                if title_span and len(title_span) > 0:
                    title = title_span[0].text.strip()
            
            # 提取价格
            price = ""
            price_span = soup.select('.ux-labels-values__values-content')
            if price_span and len(price_span) > 0:
                price_text = price_span[0].select('.ux-textspans')
                if price_text and len(price_text) > 0:
                    raw_price = price_text[0].text.strip()
                    price_match = re.search(r'\d+(\.\d+)?', raw_price)
                    if price_match:
                        price = price_match.group()
            
            # 提取图片
            image_url = ""
            img_div = soup.select('.ux-image-carousel-item')
            if img_div and len(img_div) > 0:
                img = img_div[0].find('img')
                if img and 'src' in img.attrs:
                    image_url = img['src']
            
            return ProductDTO(
                title=title,
                price=price,
                image_url=image_url,
                product_url=url
            )
            
        except Exception as e:
            logger.error(f"Error crawling eBay product: {str(e)}")
            raise
    
    # 以下方法是为了满足基类接口，但实际不会被调用
    def extract_title(self, driver):
        return ""
        
    def extract_price(self, driver):
        return ""
        
    def extract_image(self, driver):
        return ""