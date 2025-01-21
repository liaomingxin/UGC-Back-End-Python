from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
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
from app.core.crawler import ProductCrawler
from app.core.ai_service import AIService
from app.utils.logger import setup_logger
from app.core.database import get_db
from app.repositories.product_repository import ProductRepository

# 初始化日志记录器
logger = setup_logger()
# 初始化路由器
router = APIRouter(prefix="/content")

# 初始化服务实例
crawler = ProductCrawler()
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
        logger.info(f"Crawling product data from URL: {request.productUrl}")
        product_dto = await crawler.crawl_product_data(request.productUrl)

        # 保存到数据库
        repo = ProductRepository(db)
        await repo.create_product(product_dto)

        response = ProductResponse.from_dto(product_dto, request.productUrl)
        return response

    except Exception as e:
        logger.error(f"Error crawling product: {str(e)}")
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
        logger.info(f"Generating content for product: {request.product.title}")
        content = await ai_service.generate_content(
            request.product,
            request.style,
            request.length,
            request.language
        )

        # 保存商品和生成请求到数据库
        repo = ProductRepository(db)
        product = await repo.create_product(request.product)
        await repo.create_content_request(product.id, request.dict(), content)

        return ContentGenerationResponse(
            content=content,
            product=request.product
        )
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-mimic", response_model=ApiResponse)
async def generate_mimic_content(
    request: GenerateMimicRequest
):
    """
    生成模仿文案。

    参数：
        request (GenerateMimicRequest): 包含模板和其他生成参数的信息。

    返回：
        ApiResponse: 包含成功或错误信息的响应。
    """
    try:
        # 输入验证
        if not request.template or not request.template.strip():
            logger.warning("Template validation failed: Empty template")
            return ApiResponse.error(
                code=400,
                message="Invalid template",
                details="Template cannot be empty"
            )

        if len(request.template) < 10:
            logger.warning("Template validation failed: Template too short")
            return ApiResponse.error(
                code=400,
                message="Template too short",
                details="Template must be at least 10 characters"
            )

        logger.info("Generating mimic content")
        response = await ai_service.generate_mimic_content(request)
        return ApiResponse.success(data=response.dict())
    except Exception as e:
        logger.error(f"Error generating mimic content: {str(e)}")
        return ApiResponse.error(
            code=500,
            message="Internal server error",
            details=f"Error generating mimic content: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    健康检查接口。

    返回：
        dict: 服务状态。
    """
    return {"status": "healthy"}