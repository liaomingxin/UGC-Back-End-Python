from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import Product, ContentGenerationRequest
from app.models.schemas import ProductDTO, ContentGenerationRequest as ContentRequest
from decimal import Decimal

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_product(self, product: ProductDTO) -> Product:
        db_product = Product(
            title=product.title,
            price=Decimal(product.price) if product.price else Decimal('0.00'),
            image_url=product.image_url,
            product_url=product.product_url
        )
        self.session.add(db_product)
        await self.session.commit()
        await self.session.refresh(db_product)
        return db_product
    
    async def create_content_request(
        self, 
        product_id: int, 
        request: ContentRequest, 
        content: str
    ) -> ContentGenerationRequest:
        db_request = ContentGenerationRequest(
            product_id=product_id,
            style=request.style,
            length=request.length,
            language=request.language,
            content=content
        )
        self.session.add(db_request)
        await self.session.commit()
        await self.session.refresh(db_request)
        return db_request 