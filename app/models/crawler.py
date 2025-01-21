from pydantic import BaseModel
from typing import List, Optional, Dict

class PriceSelector(BaseModel):
    """
    商品价格选择器配置。
    属性：
        class_name (str): 价格元素的类名。
        pattern (Optional[str]): 提取价格的正则表达式模式，可选。
    """
    class_name: str
    pattern: Optional[str] = None

class SiteConfig(BaseModel):
    """
    网站配置模型。
    属性：
        domain (List[str]): 支持的域名列表。
        title (str): 商品标题的CSS选择器。
        price (PriceSelector): 商品价格选择器配置。
        image (str): 商品图片的CSS选择器。
    """
    domain: List[str]
    title: str
    price: PriceSelector
    image: str

class SelectorsConfig(BaseModel):
    """
    全部网站的选择器配置。
    属性：
        selectors (Dict[str, SiteConfig]): 每个站点的配置字典，键为站点名称。
    """
    selectors: Dict[str, SiteConfig]