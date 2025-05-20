from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.modules.common.config.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    stock = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    creator = relationship("User", back_populates="products") 