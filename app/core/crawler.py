from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
    def __init__(self):
        """
        商品爬虫初始化。
        初始化选择器配置和Chrome浏览器选项。
        """
        self.selectors = self._load_selectors()
        self.chrome_options = self._setup_chrome_options()
        self.service = Service(executable_path=settings.CHROME_DRIVER_PATH)

    def _load_selectors(self) -> SelectorsConfig:
        """
        加载选择器配置文件。
        返回：
            SelectorsConfig: 选择器配置对象。
        """
        config_path = Path(__file__).parent.parent / "config" / "selectors.yml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
            return SelectorsConfig(**config_dict)

    def _setup_chrome_options(self) -> Options:
        """
        设置Chrome浏览器选项。
        返回：
            Options: Chrome浏览器选项对象。
        """
        options = Options()
        if not settings.DEBUG:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-allow-origins=*")
        return options

    def _get_site_config(self, url: str) -> SiteConfig:
        """
        根据URL获取对应的网站配置。
        参数：
            url (str): 商品页面URL。
        返回：
            SiteConfig: 对应网站的配置对象。
        异常：
            ValueError: 如果域名不支持。
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
            url (str): 商品页面URL。

        返回：
            ProductDTO: 包含商品信息的数据传输对象。
        """
        try:
            driver = webdriver.Chrome(
                service=self.service,
                options=self.chrome_options
            )

            try:
                driver.get(url)
                wait = WebDriverWait(driver, 10)  # 等待最多10秒
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

            finally:
                driver.quit()

        except Exception as e:
            logger.error(f"Error crawling product: {str(e)}")
            raise

    def _get_title(self, driver, wait, site_config) -> str:
        """
        获取商品标题。

        参数：
            driver: WebDriver实例。
            wait: WebDriverWait实例。
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
            driver: WebDriver实例。
            wait: WebDriverWait实例。
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
            driver: WebDriver实例。
            wait: WebDriverWait实例。
            site_config: 网站配置对象。

        返回：
            str: 商品图片的URL。
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
            driver: WebDriver实例。
            wait: WebDriverWait实例。
            site_config: 网站配置对象。

        返回：
            str: 商品价格。

        异常：
            如果无法提取价格，将记录并抛出异常。
        """
        try:
            # 尝试使用class_name提取价格
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
            # 如果通过class_name失败，尝试使用CSS选择器
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