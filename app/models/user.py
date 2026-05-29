"""
认证相关模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Customer(Base):
    """客户用户表"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))
    points = Column(Integer, default=0)  # 积分
    carbon_saved = Column(Integer, default=0)  # 累计减碳(克)
    food_saved = Column(Integer, default=0)  # 累计救粮(克)
    preferences = Column(String(500))  # 偏好设置(JSON)
    hometown = Column(String(100))  # 老家位置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    orders = relationship("Order", back_populates="customer")
    scans = relationship("UserScan", back_populates="customer")
    points_records = relationship("HunterPoint", back_populates="customer")
    challenges = relationship("UserChallenge", back_populates="customer")
    badges = relationship("UserBadge", back_populates="customer")
    food_behaviors = relationship("CustomerFoodBehavior", back_populates="customer")
    category_preferences = relationship("CustomerCategoryPreference", back_populates="customer")
    recommendations = relationship("FoodRecommendation", back_populates="customer")
    preference = relationship("CustomerPreference", back_populates="customer", uselist=False)

    def __repr__(self):
        return f"<Customer {self.nickname or self.phone}>"


class Merchant(Base):
    """商家用户表"""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    store_name = Column(String(100), nullable=False)
    store_type_id = Column(Integer, index=True)
    address = Column(String(255))
    latitude = Column(Integer)  # 扩大10000000倍存储
    longitude = Column(Integer)  # 扩大10000000倍存储
    contact_phone = Column(String(20))
    business_hours = Column(String(100))
    business_license = Column(String(255))  # 营业执照URL
    verified = Column(Boolean, default=False)
    rating = Column(Integer, default=500)  # 评分，放大10倍存储
    total_orders = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    shops = relationship("Shop", back_populates="merchant")

    def __repr__(self):
        return f"<Merchant {self.store_name}>"
