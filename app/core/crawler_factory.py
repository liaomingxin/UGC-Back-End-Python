from urllib.parse import urlparse
from .site_crawlers import (
    TaobaoTmallCrawler,
    AmazonCrawler,
    TemuCrawler,
    LazadaCrawler,
    EbayCrawler
)
from app.config.settings import settings

class CrawlerFactory:
    """爬虫工厂类"""
    
    @staticmethod
    def get_crawler(url: str):
        """根据URL获取对应的爬虫实例"""
        domain = urlparse(url).netloc.lower()
        
        if any(site in domain for site in ['taobao.com', 'tmall.com']):
            return TaobaoTmallCrawler(settings.CHROME_DRIVER_PATH)
        elif 'amazon.com' in domain:
            return AmazonCrawler(settings.CHROME_DRIVER_PATH)
        elif 'temu.com' in domain:
            return TemuCrawler(settings.CHROME_DRIVER_PATH)
        elif 'lazada' in domain:
            return LazadaCrawler(settings.CHROME_DRIVER_PATH)
        elif 'ebay.com' in domain:
            return EbayCrawler(settings.CHROME_DRIVER_PATH)
        else:
            raise ValueError(f"Unsupported domain: {domain}")