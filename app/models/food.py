# app/models/food.py - 食品相关数据模型
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, DECIMAL, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class FoodTypeEnum(str, enum.Enum):
    """食品类型枚举"""
    BAKERY = "bakery"          # 面包糕点
    DAIRY = "dairy"            # 乳制品
    VEGETABLE = "vegetable"    # 蔬菜
    FRUIT = "fruit"            # 水果
    MEAT = "meat"              # 肉类
    BEVERAGE = "beverage"      # 饮料
    SNACK = "snack"            # 零食


class RiskLevelEnum(str, enum.Enum):
    """风险等级枚举"""
    LOW = "low"           # 3天以上
    MEDIUM = "medium"     # 1-3天
    HIGH = "high"         # 24小时内
    CRITICAL = "critical" # 即将过期


class DiscountTypeEnum(str, enum.Enum):
    """折扣类型枚举"""
    MYSTERY_BOX = "mystery_box"  # 盲盒
    CLEARANCE = "clearance"       # 折扣清仓
    TIME_LIMIT = "time_limit"     # 限时折扣


class ShopFoodStatusEnum(str, enum.Enum):
    """店铺食品状态枚举"""
    DRAFT = "draft"         # 草稿
    ACTIVE = "active"       # 在售
    SOLD_OUT = "sold_out"   # 售罄
    EXPIRED = "expired"     # 已过期


class FoodType(Base):
    """食品类型表"""
    __tablename__ = "food_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="类型名称")
    icon = Column(String(50), comment="图标")
    color = Column(String(20), comment="地图标注颜色")
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    foods = relationship("Food", back_populates="food_type")


class Food(Base):
    """标准食品表"""
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(50), unique=True, comment="条形码")
    name = Column(String(100), nullable=False, comment="食品名称")
    food_type_id = Column(Integer, ForeignKey("food_types.id"), comment="食品类型")
    brand = Column(String(100), comment="品牌")
    default_weight = Column(String(50), comment="默认规格")
    image_url = Column(String(255), comment="图片URL")
    avg_expiry_days = Column(Integer, default=7, comment="平均保质期天数")
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    food_type = relationship("FoodType", back_populates="foods")
    shop_foods = relationship("ShopFood", back_populates="food")
    flavor_tags = relationship("FoodFlavorTag", back_populates="food")


class FoodFlavorTag(Base):
    """食品口味标签表"""
    __tablename__ = "food_flavor_tags"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False)
    flavor_tag = Column(String(20), nullable=False, comment="口味标签")
    intensity = Column(Integer, default=5, comment="强度1-10")

    # 关联
    food = relationship("Food", back_populates="flavor_tags")


class ShopFood(Base):
    """店铺食品表"""
    __tablename__ = "shop_foods"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False, comment="食品ID")
    shelf_position = Column(String(50), comment="货架位置")
    quantity = Column(Integer, default=0, comment="库存数量")
    original_price = Column(DECIMAL(10, 2), comment="原价(分)")
    discount_price = Column(DECIMAL(10, 2), nullable=False, comment="折扣价(分)")
    discount_type = Column(String(20), comment="折扣类型")
    expiry_date = Column(DateTime, comment="到期日期")
    risk_level = Column(String(20), default="low", comment="风险等级")
    status = Column(String(20), default="active", comment="状态")
    published_at = Column(DateTime, comment="发布时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联
    shop = relationship("Shop", back_populates="shop_foods")
    food = relationship("Food", back_populates="shop_foods")
    orders = relationship("Order", back_populates="shop_food")
