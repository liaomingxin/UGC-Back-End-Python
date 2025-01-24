import sys
sys.path.append("..")  # 将上层目录添加到sys.path

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from app.models.schemas import (
    ProductDTO,
    ContentGenerationRequest,
    ContentGenerationResponse,
    GenerateMimicRequest,
    GenerateMimicResponse,
    ApiResponse,
    ProductRequest,
    ProductResponse
)
from app.core.ai_service import AIService
from app.utils.logger import setup_logger
from app.core.database import get_db
from app.repositories.product_repository import ProductRepository
from app.core.crawler_factory import CrawlerFactory
import time

# 初始化日志记录器
logger = setup_logger()
# 初始化路由器
router = APIRouter(prefix="/content")

# 初始化服务实例
ai_service = AIService()

@router.post("/crawl", response_model=ProductResponse)
async def crawl_product(
    request: ProductRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    爬取商品信息。

    参数：
        request (ProductRequest): 包含商品 URL 的请求对象。
        db (AsyncSession): 数据库会话。

    返回：
        ProductResponse: 包含商品信息的响应对象。
    """
    try:
        logger.info(f"Crawling product data from URL: {request.product_url}")
        start_time = time.time()
        
        # 使用工厂获取对应的爬虫
        crawler = CrawlerFactory.get_crawler(request.product_url)
        product_dto = crawler.crawl(request.product_url)
        logger.info(f"Crawled product data: {product_dto}")
        
        # 创建响应
        response = ProductResponse.from_dto(product_dto, request.product_url)
        end_time = time.time()
        logger.info(f"------------Crawled product in {end_time - start_time} seconds------------ \n")
        
        # 在当前数据库会话中保存
        repo = ProductRepository(db)
        try:
            await repo.create_product(product_dto)
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
        
        return response

    except Exception as e:
        logger.error(f"Error crawling product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    生成营销文案。

    参数：
        request (ContentGenerationRequest): 包含文案生成所需的产品和选项信息。
        db (AsyncSession): 数据库会话。

    返回：
        ContentGenerationResponse: 包含生成的文案和产品信息。
    """
    try:
        # 记录请求参数
        logger.info(f"Style: {request.style}")
        logger.info(f"Length: {request.length}")
        logger.info(f"Language: {request.language}")

        # 生成内容
        content = await ai_service.generate_content(
            request.product,
            request.style,
            request.length,
            request.language
        )

        # 保存到数据库
        repo = ProductRepository(db)
        product = await repo.create_product(request.product)
        
        # 这里是问题所在
        # request.dict() 返回字典，但后续代码还在尝试访问 .style 属性
        content_request = await repo.create_content_request(product.id, request, content)

        return ContentGenerationResponse(
            content=content,
            product=request.product
        )

    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return ApiResponse(
            success=False,
            code=500,
            error=str(e)
        )

@router.post("/generate-mimic", response_model=ApiResponse)
async def generate_mimic_content(request: GenerateMimicRequest):
    try:
        # 验证模板
        if not request.template:
            logger.warning("Template validation failed: Template is empty")
            return ApiResponse(
                success=False,
                code=400,
                error="Template is required"
            )

        if len(request.template) < 10:
            logger.warning("Template validation failed: Template too short")
            return ApiResponse(
                success=False,
                code=400,
                error="Template too short",
            )

        logger.info("Generating mimic content")
        response = await ai_service.generate_mimic_content(request)
        # 成功响应
        return ApiResponse(
            success=True,
            code=200,
            data=dict(response)
        )
        
    except Exception as e:
        logger.error(f"Error generating mimic content: {str(e)}", exc_info=True)
        return ApiResponse(
            success=False,
            code=500,
            error="Internal server error",
        )

@router.get("/health")
async def health_check():
    """
    健康检查接口。

    返回：
        dict: 服务状态。
    """
    return {"status": "healthy"}

logger.info(f"ApiResponse class: {ApiResponse}")
logger.info(f"ApiResponse methods: {dir(ApiResponse)}")