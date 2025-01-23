from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.models.schemas import ProductDTO
from app.utils.logger import setup_logger
from abc import ABC, abstractmethod
from urllib.parse import urlparse
import decimal
import time

logger = setup_logger()

class BaseCrawler(ABC):
    """基础爬虫类，定义通用的爬虫功能"""
    
    def __init__(self, chrome_driver_path):
        self.chrome_driver_path = chrome_driver_path
        self.chrome_options = self._setup_chrome_options()
        self.service = Service(chrome_driver_path)
        
    def _setup_chrome_options(self) -> Options:
        """设置Chrome浏览器选项"""
        options = Options()
        options.page_load_strategy = 'eager'
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return options
        
    def _create_driver(self):
        """创建WebDriver实例"""
        return webdriver.Chrome(service=self.service, options=self.chrome_options)
        
    @abstractmethod
    def extract_title(self, driver: webdriver.Chrome) -> str:
        """提取商品标题"""
        pass
        
    @abstractmethod
    def extract_price(self, driver: webdriver.Chrome) -> str:
        """提取商品价格"""
        pass
        
    @abstractmethod
    def extract_image(self, driver: webdriver.Chrome) -> str:
        """提取商品图片URL"""
        pass
        
    def crawl(self, url: str) -> ProductDTO:
        """执行爬取操作"""
        driver = None
        try:
            logger.info(f"Starting crawl for URL: {url}")
            start_time = time.time()
            
            driver = self._create_driver()
            driver.get(url)
            logger.info("Browser initialized and navigating to URL")
            
            # 等待页面加载
            domain = urlparse(url).netloc.lower()
            logger.info(f"Detected domain: {domain}")
            
            if any(site in domain for site in ['taobao.com', 'tmall.com']):
                logger.info("Waiting for Taobao/Tmall page to load...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
            else:
                logger.info("Waiting for page to load...")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            
            # 提取数据
            title = self.extract_title(driver)
            logger.info(f"Extracted title: {title}")
            
            price = self.extract_price(driver)
            logger.info(f"Extracted price: {price}")
            
            image_url = self.extract_image(driver)
            logger.info(f"Extracted image URL: {image_url}")
            
            product_dto = ProductDTO(
                title=title,
                price=price,
                image_url=image_url,
                product_url=url
            )
            
            end_time = time.time()
            logger.info(f"Crawl completed in {end_time - start_time:.2f}s")
            logger.info(f"Crawled data: {product_dto.dict()}")
            
            return product_dto
        except Exception as e:
            logger.error(f"Error during crawl: {str(e)}", exc_info=True)
            raise
        finally:
            if driver:
                driver.quit()
                logger.info("Browser closed")