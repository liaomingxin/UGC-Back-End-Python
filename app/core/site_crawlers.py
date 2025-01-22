from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_crawler import BaseCrawler

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
        elements = driver.find_elements(By.CLASS_NAME, 'pdp-mod-product-badge-title')
        return elements[0].text if elements else ""
        
    def extract_price(self, driver):
        div_element = driver.find_elements(By.CLASS_NAME, 'pdp-product-price')[0]
        span_element = div_element.find_elements(By.TAG_NAME, 'span')
        return span_element[0].text if span_element else ""
        
    def extract_image(self, driver):
        elements = driver.find_elements(By.CLASS_NAME, 'pdp-mod-common-image')
        if elements:
            return elements[0].get_attribute('src')
        return "" 