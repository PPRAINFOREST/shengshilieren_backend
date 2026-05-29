"""
店铺和食品相关模型
"""
from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, ForeignKey,
    Index, Integer, String, Text, JSON
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ShopType(Base):
    """店铺类型表"""
    __tablename__ = "shop_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # 便利店/超市/面包店/水果店
    description = Column(String(255))
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    shops = relationship("Shop", back_populates="shop_type")

    def __repr__(self):
        return f"<ShopType {self.name}>"


class Shop(Base):
    """店铺表"""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    shop_type_id = Column(Integer, ForeignKey("shop_types.id"), nullable=False)
    shop_name = Column(String(100), nullable=False)
    address = Column(String(255))
    latitude = Column(Integer)  # 扩大10000000倍存储
    longitude = Column(Integer)  # 扩大10000000倍存储
    contact_phone = Column(String(20))
    business_hours = Column(String(100))
    verified = Column(Boolean, default=False)
    rating = Column(Integer, default=500)  # 评分，放大10倍
    total_orders = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 索引
    __table_args__ = (
        Index("idx_shop_location", "latitude", "longitude"),
        Index("idx_shop_merchant", "merchant_id"),
        Index("idx_shop_type", "shop_type_id"),
    )

    # 关系
    merchant = relationship("Merchant", back_populates="shops")
    shop_type = relationship("ShopType", back_populates="shops")
    foods = relationship("ShopFood", back_populates="shop")

    def __repr__(self):
        return f"<Shop {self.shop_name}>"


class MerchantShop(Base):
    """商家-店铺关联表（一个商家可以有多个店铺）"""
    __tablename__ = "merchant_shops"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False)
    shop_id = Column(Integer, ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    is_primary = Column(Boolean, default=False)  # 是否主店铺
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    merchant = relationship("Merchant", back_populates="merchant_shops")
    shop = relationship("Shop", back_populates="merchant_shops")


    # 关系
