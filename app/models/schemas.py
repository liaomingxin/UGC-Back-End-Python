from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class ProductDTO(BaseModel):
    """商品数据传输对象"""
    title: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None
    product_url: str

class ProductRequest(BaseModel):
    """商品请求模型"""
    product_url: str

class ProductResponse(BaseModel):
    """商品响应模型"""
    title: str
    price: str
    image_url: Optional[str] = None
    product_url: str

    @classmethod
    def from_dto(cls, dto: ProductDTO, product_url: str):
        """从DTO创建响应对象"""
        return cls(
            title=dto.title,
            price=dto.price,
            image_url=dto.image_url,
            product_url=product_url
        )

class ContentGenerationRequest(BaseModel):
    """
    文案生成请求对象。
    属性：
        product (ProductDTO): 商品信息。
        style (str): 文案风格。
        length (str): 文案长度。
        language (str): 文案语言。
    """
    product: ProductDTO
    style: str
    length: str
    language: str

class ContentGenerationResponse(BaseModel):
    """
    文案生成响应对象。
    属性：
        content (str): 生成的文案内容。
        product (ProductDTO): 对应的商品信息。
    """
    content: str
    product: ProductDTO

class GenerateMimicRequest(BaseModel):
    """
    模仿文案生成请求对象。
    属性：
        template (str): 模仿的模板文案。
        scene (str): 应用场景。
        length (str): 文案长度。
        product_info (Optional[ProductDTO]): 商品信息，可选。
    """
    template: str = Field(..., description="模仿的模板文案")
    scene: str = Field(..., description="应用场景")
    length: str = Field(..., description="文案长度")
    product_info: Optional[ProductDTO] = Field(None, description="商品信息（可选）")

    class Config:
        json_schema_extra = {
            "example": {
                "template": "请你生成一段关于没事的介绍",
                "scene": "travel",
                "length": "50",
                "product_info": None
            }
        }

class GenerateMimicResponse(BaseModel):
    """
    模仿文案生成响应对象。
    属性：
        content (str): 生成的模仿文案。
        word_count (int): 文案字数。
        sentiment (str): 文案情感。
        keywords (List[str]): 提取的关键词列表。
    """
    content: str
    word_count: int
    sentiment: str
    keywords: List[str]

class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    code: int = 200