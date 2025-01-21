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
import os, stat
from decimal import Decimal, InvalidOperation
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.schemas import ProductDTO
from app.models.crawler import SelectorsConfig, SiteConfig
from app.config.settings import settings
from app.utils.logger import setup_logger
from app.utils.diagnostic import CrawlerDiagnostic

logger = setup_logger()


class ProductCrawler:
    """
    商品爬虫类，用于通过 Selenium 爬取商品数据。
    """

    MAX_RETRIES = 2
    TIMEOUT_SECONDS = 10

    def __init__(self):
        """
        初始化商品爬虫。
        """
        self.selectors = self._load_selectors()
        self.chrome_options = self._setup_chrome_options()
        self.diagnostic = CrawlerDiagnostic()

        try:
            chrome_driver_path = settings.CHROME_DRIVER_PATH
            if not chrome_driver_path:
                raise ValueError("CHROME_DRIVER_PATH not set in environment variables")

            if not Path(chrome_driver_path).exists():
                raise FileNotFoundError(f"ChromeDriver not found at: {chrome_driver_path}")

            # 检查并设置执行权限
            st = os.stat(chrome_driver_path)
            if not bool(st.st_mode & stat.S_IXUSR):
                logger.warning(f"Setting execute permission for ChromeDriver")
                os.chmod(chrome_driver_path, st.st_mode | stat.S_IXUSR)

            logger.info(f"Using ChromeDriver from: {chrome_driver_path}")
            self.service = Service(executable_path=chrome_driver_path)

            # 验证 ChromeDriver 是否可用
            test_driver = None
            try:
                test_driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
                chrome_version = test_driver.capabilities['browserVersion']
                driver_version = test_driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
                logger.info(f"Chrome version: {chrome_version}")
                logger.info(f"ChromeDriver version: {driver_version}")
            finally:
                if test_driver:
                    test_driver.quit()

        except Exception as e:
            logger.error(f"Error during ChromeDriver initialization: {str(e)}")
            raise

    def _load_selectors(self) -> SelectorsConfig:
        """
        加载选择器配置文件。
        """
        config_path = Path(__file__).parent.parent / "config" / "selectors.yml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
                return SelectorsConfig(**config_dict)
        except Exception as e:
            logger.error(f"Error loading selectors configuration: {str(e)}")
            raise

    def _setup_chrome_options(self) -> Options:
        """
        设置 Chrome 浏览器选项。
        """
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6834.84 Safari/537.36")
        return options

    def _get_site_config(self, url: str) -> SiteConfig:
        """
        根据 URL 获取对应的网站配置。
        """
        domain = urlparse(url).netloc
        for site_name, config in self.selectors.selectors.items():
            if any(d in domain for d in config.domain):
                return config
        raise ValueError(f"Unsupported domain: {domain}")

    @retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def crawl_product_data(self, url: str) -> ProductDTO:
        """
        爬取商品数据。
        """
        driver = None
        session_id = None
        try:
            driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            driver.get(url)
            
            # 获取页面快照
            html_snapshot = driver.page_source
            site_config = self._get_site_config(url)
            
            # 记录诊断信息
            session_id = self.diagnostic.log_crawl_attempt(
                url=url,
                site_config=site_config.dict(),
                html_snapshot=html_snapshot
            )
            
            wait = WebDriverWait(driver, self.TIMEOUT_SECONDS)
            product = ProductDTO(product_url=url)
            
            # 获取标题并记录
            try:
                product.title = self._get_title(driver, wait, site_config)
                self.diagnostic.log_element_state(
                    session_id=session_id,
                    element_type="title",
                    selector=site_config.title,
                    found=bool(product.title),
                    value=product.title
                )
            except Exception as e:
                self.diagnostic.log_element_state(
                    session_id=session_id,
                    element_type="title",
                    selector=site_config.title,
                    found=False,
                    error=str(e)
                )
                raise
            
            # 获取价格并记录
            try:
                product.price = self._extract_price(driver, wait, site_config)
                self.diagnostic.log_element_state(
                    session_id=session_id,
                    element_type="price",
                    selector=site_config.price.className,
                    found=bool(product.price),
                    value=product.price
                )
            except Exception as e:
                self.diagnostic.log_element_state(
                    session_id=session_id,
                    element_type="price",
                    selector=site_config.price.className,
                    found=False,
                    error=str(e)
                )
                raise

            # 获取图片并记录
            try:
                product.image_url = self._get_image(driver, wait, site_config)
                self.diagnostic.log_element_state(
                    session_id=session_id,
                    element_type="image",
                    selector=site_config.image,
                    found=bool(product.image_url),
                    value=product.image_url
                )
            except Exception as e:
                self.diagnostic.log_element_state(
                    session_id=session_id,
                    element_type="image",
                    selector=site_config.image,
                    found=False,
                    error=str(e)
                )
            
            if self._is_product_data_valid(product):
                self.diagnostic.log_extraction_result(
                    session_id=session_id,
                    success=True,
                    product_data=product.dict()
                )
                return product
            else:
                self.diagnostic.log_extraction_result(
                    session_id=session_id,
                    success=False,
                    error="Incomplete product data"
                )
                raise ValueError("Incomplete product data")
                
        except Exception as e:
            if session_id:
                self.diagnostic.log_extraction_result(
                    session_id=session_id,
                    success=False,
                    error=str(e)
                )
            raise
        finally:
            if driver:
                driver.quit()

    def _get_title(self, driver, wait, site_config) -> str:
        """
        获取商品标题。
        """
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, site_config.title)))
            return element.text.strip()
        except Exception as e:
            logger.error(f"Error getting title with primary selector: {str(e)}")
            # 尝试备用选择器
            backup_selectors = [
                "h1",
                ".product-title",
                ".title",
                "[class*='title']"
            ]
            for selector in backup_selectors:
                try:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if title := element.text.strip():
                        return title
                except:
                    continue
            raise ValueError("Could not find title element")

    def _extract_price(self, driver, wait, site_config) -> str:
        """
        提取商品价格。
        """
        try:
            if "amazon.com" in driver.current_url:
                # 亚马逊特殊处理
                price_selectors = [
                    ".a-offscreen",  # 主要价格选择器
                    ".a-price .a-offscreen",  # 备用选择器1
                    "#priceblock_ourprice",  # 备用选择器2
                    "#price_inside_buybox",  # 备用选择器3
                    ".a-price-whole"  # 备用选择器4
                ]
                
                for selector in price_selectors:
                    try:
                        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        price_text = element.text.strip()
                        if price_text:
                            logger.info(f"Found price with selector {selector}: {price_text}")
                            # 提取数字
                            price_match = re.search(r'[\d,.]+', price_text)
                            if price_match:
                                price = price_match.group(0).replace(',', '')
                                # 验证提取的价格
                                try:
                                    decimal_price = Decimal(price)
                                    if decimal_price > 0:
                                        logger.info(f"Successfully extracted price: {decimal_price}")
                                        return str(decimal_price)
                                except (InvalidOperation, ValueError):
                                    continue
                    except Exception as e:
                        logger.debug(f"Failed to get price with selector {selector}: {str(e)}")
                        continue
                    
                raise ValueError("Could not find valid price element")
                
            else:
                # 其他网站的处理逻辑
                selector = site_config.price.className
                if selector.startswith('.'):
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                else:
                    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector)))
                    
                price_text = element.text.strip()
                logger.info(f"Raw price text extracted: {price_text}")

                # 提取数字
                price_match = re.search(r'[\d,.]+', price_text)
                if price_match:
                    price = price_match.group(0).replace(',', '')
                    return str(Decimal(price))
                else:
                    raise ValueError(f"No valid price found in text: {price_text}")

        except Exception as e:
            logger.error(f"Error extracting price: {str(e)}")
            raise

    def _get_image(self, driver, wait, site_config) -> str:
        """
        获取商品图片。
        """
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, site_config.image)))
            if src := (element.get_attribute("src") or element.get_attribute("data-src")):
                return src
        except Exception as e:
            logger.error(f"Error getting image with primary selector: {str(e)}")
            # 尝试备用选择器
            backup_selectors = [
                "img[class*='product']",
                "img[class*='main']",
                ".product-image img",
                "[class*='image'] img"
            ]
            for selector in backup_selectors:
                try:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    if src := (element.get_attribute("src") or element.get_attribute("data-src")):
                        return src
                except:
                    continue
            return ""  # 如果找不到图片，返回空字符串而不是抛出异常

    def _is_product_data_valid(self, product: ProductDTO) -> bool:
        """
        验证商品数据的完整性。
        """
        return bool(product.title or product.price)