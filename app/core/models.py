from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, manager, staff
    permission = Column(String, nullable=False)

    # Relationships
    companies = relationship("UserCompany", back_populates="user")

class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, index=True)  # tax_code
    code = Column(String, unique=True, index=True, nullable=False)
    logo = Column(String)
    images = Column(String)
    name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)

    # Relationships
    users = relationship("UserCompany", back_populates="company")
    products = relationship("Product", back_populates="company")

class UserCompany(Base):
    __tablename__ = "user_companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="companies")
    company = relationship("Company", back_populates="users")

class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    thumbnail = Column(String)
    images = Column(String)
    name = Column(String, nullable=False)
    description = Column(String)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="products") 