from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.models.schemas import ProductDTO
from app.utils.logger import setup_logger
from abc import ABC, abstractmethod

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
            driver = self._create_driver()
            driver.get(url)
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            if driver.page_source:
                logger.info(f"page loaded")
            else:
                logger.info(f"page not loaded")
            
            # 提取数据
            title = self.extract_title(driver)
            price = self.extract_price(driver)
            image_url = self.extract_image(driver)
            
            return ProductDTO(
                title=title,
                price=price,
                image_url=image_url,
                product_url=url
            )
            
        finally:
            if driver:
                driver.quit() 