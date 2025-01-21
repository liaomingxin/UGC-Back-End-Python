from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, Text, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(2048), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    image_url = Column(Text)
    product_url = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    content_requests = relationship("ContentGenerationRequest", back_populates="product")

class ContentGenerationRequest(Base):
    __tablename__ = 'content_generation_requests'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    style = Column(String(100), nullable=False)
    length = Column(String(50), nullable=False)
    language = Column(String(50), nullable=False)
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    product = relationship("Product", back_populates="content_requests") 