import asyncio
from decimal import Decimal
from app.core.database import AsyncSessionLocal
from app.models.schemas import ProductDTO, ContentGenerationRequest
from app.repositories.product_repository import ProductRepository
from app.utils.logger import setup_logger

logger = setup_logger()

async def test_database_operations():
    """测试数据库操作"""
    async with AsyncSessionLocal() as session:
        repo = ProductRepository(session)
        
        # 1. 测试创建商品
        logger.info("Testing product creation...")
        test_product = ProductDTO(
            title="测试商品",
            price="99.99",
            image_url="https://example.com/image.jpg",
            product_url="https://example.com/product"
        )
        
        db_product = await repo.create_product(test_product)
        logger.info(f"Created product with ID: {db_product.id}")
        
        # 2. 测试创建文案生成请求
        logger.info("Testing content generation request creation...")
        test_request = ContentGenerationRequest(
            product=test_product,
            style="搞笑",
            length="短",
            language="zh"
        )
        
        db_request = await repo.create_content_request(
            product_id=db_product.id,
            request=test_request,
            content="这是一个测试文案内容"
        )
        logger.info(f"Created content request with ID: {db_request.id}")
        
        # 3. 测试查询商品
        logger.info("Testing product query...")
        products = await repo.get_products()
        for product in products:
            logger.info(f"Found product: {product.title} (ID: {product.id})")
            
            # 4. 测试查询关联的文案请求
            content_requests = await repo.get_content_requests(product.id)
            for req in content_requests:
                logger.info(f"  - Content request: {req.style} (ID: {req.id})")
                logger.info(f"    Content: {req.content}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_database_operations()) 