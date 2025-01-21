from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import re
from urllib.parse import urlparse
import yaml
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.schemas import ProductDTO, ProductResponse
from app.models.crawler import SelectorsConfig, SiteConfig
from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger()

class ProductCrawler:
    """
    商品爬虫类，用于通过 Selenium 爬取商品数据。
    """

    def __init__(self):
        """
        初始化商品爬虫。
        初始化选择器配置、浏览器选项和 ChromeDriver。
        """
        self.selectors = self._load_selectors()
        self.chrome_options = self._setup_chrome_options()

        # 动态设置 ChromeDriver
        if not settings.CHROME_DRIVER_PATH:
            logger.warning("CHROME_DRIVER_PATH not set, using default path from ChromeDriverManager")
            self.service = Service(ChromeDriverManager().install())
        else:
            logger.info(f"Using ChromeDriver from path: {settings.CHROME_DRIVER_PATH}")
            self.service = Service(executable_path=settings.CHROME_DRIVER_PATH)

    def _load_selectors(self) -> SelectorsConfig:
        """
        加载选择器配置文件。

        返回：
            SelectorsConfig: 选择器配置对象。
        """
        config_path = Path(__file__).parent.parent / "config" / "selectors.yml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
                return SelectorsConfig(**config_dict)
        except FileNotFoundError as e:
            logger.error(f"Selectors configuration file not found: {str(e)}")
            raise

    def _setup_chrome_options(self) -> Options:
        """
        设置 Chrome 浏览器选项。

        返回：
            Options: 配置好的 Chrome 浏览器选项。
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        return options

    def _get_site_config(self, url: str) -> SiteConfig:
        """
        根据 URL 获取对应的网站配置。

        参数：
            url (str): 商品页面 URL。

        返回：
            SiteConfig: 对应网站的配置对象。

        异常：
            ValueError: 如果域名不受支持。
        """
        domain = urlparse(url).netloc
        for site_name, config in self.selectors.selectors.items():
            if any(d in domain for d in config.domain):
                return config
        raise ValueError(f"Unsupported domain: {domain}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def crawl_product_data(self, url: str) -> ProductDTO:
        """
        爬取商品数据。

        参数：
            url (str): 商品页面 URL。

        返回：
            ProductDTO: 包含商品信息的数据传输对象。
        """
        driver = None
        try:
            logger.info(f"Initializing Chrome Driver for URL: {url}")
            driver = webdriver.Chrome(
                service=self.service,
                options=self.chrome_options
            )

            logger.info("Chrome Driver initialized successfully")
            driver.get(url)

            # 显式等待页面加载完成
            wait = WebDriverWait(driver, 10)
            site_config = self._get_site_config(url)

            # 获取商品信息
            title = self._get_title(driver, wait, site_config)
            price = self._get_price(driver, wait, site_config)
            image_url = self._get_image(driver, wait, site_config)

            return ProductDTO(
                title=title,
                price=price,
                image_url=image_url,
                product_url=url
            )

        except Exception as e:
            logger.error(f"Error during crawling: {str(e)}")
            raise

        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Chrome Driver closed successfully")
                except Exception as e:
                    logger.error(f"Error closing Chrome Driver: {str(e)}")

    def _get_title(self, driver, wait, site_config) -> str:
        """
        获取商品标题。

        参数：
            driver: WebDriver 实例。
            wait: WebDriverWait 实例。
            site_config: 网站配置对象。

        返回：
            str: 商品标题。
        """
        try:
            title_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, site_config.title)
                )
            )
            return title_element.text.strip()
        except Exception as e:
            logger.error(f"Error getting title: {str(e)}")
            raise

    def _get_price(self, driver, wait, site_config) -> str:
        """
        获取商品价格。

        参数：
            driver: WebDriver 实例。
            wait: WebDriverWait 实例。
            site_config: 网站配置对象。

        返回：
            str: 商品价格。
        """
        try:
            return self._extract_price(driver, wait, site_config)
        except Exception as e:
            logger.error(f"Error getting price: {str(e)}")
            raise

    def _get_image(self, driver, wait, site_config) -> str:
        """
        获取商品图片。

        参数：
            driver: WebDriver 实例。
            wait: WebDriverWait 实例。
            site_config: 网站配置对象。

        返回：
            str: 商品图片的 URL。
        """
        try:
            image_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, site_config.image)
                )
            )
            return image_element.get_attribute('src')
        except Exception as e:
            logger.error(f"Error getting image: {str(e)}")
            raise

    def _extract_price(self, driver, wait, site_config) -> str:
        """
        提取商品价格。

        参数：
            driver: WebDriver 实例。
            wait: WebDriverWait 实例。
            site_config: 网站配置对象。

        返回：
            str: 商品价格。

        异常：
            如果无法提取价格，将记录并抛出异常。
        """
        try:
            # 尝试使用 class_name 提取价格
            price_element = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, site_config.price.class_name)
                )
            )
            price_text = price_element.text.strip()

            # 如果配置了价格匹配模式，使用正则提取
            if site_config.price.pattern:
                match = re.search(site_config.price.pattern, price_text)
                if match:
                    price_text = match.group(0)

            return price_text

        except TimeoutException:
            # 如果通过 class_name 失败，尝试使用 CSS 选择器
            logger.warning("Class name extraction failed, trying CSS selector.")
            price_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f".{site_config.price.class_name}")
                )
            )
            price_text = price_element.text.strip()

            if site_config.price.pattern:
                match = re.search(site_config.price.pattern, price_text)
                if match:
                    price_text = match.group(0)

            return price_text