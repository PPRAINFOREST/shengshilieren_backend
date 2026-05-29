"""
Pydantic schemas - 店铺和食品相关
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============ Shop (店铺) ============

class ShopBase(BaseModel):
    """店铺基础字段"""
    shop_name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ShopCreate(ShopBase):
    """创建店铺"""
    merchant_id: int
    shop_type_id: int


class ShopUpdate(BaseModel):
    """更新店铺"""
    shop_name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_hours: Optional[str] = None


class ShopResponse(ShopBase):
    """店铺响应"""
    id: int
    merchant_id: int
    shop_type_id: int
    verified: bool = False
    rating: float = 5.0
    business_hours: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Food (标准食品) ============

class FoodBase(BaseModel):
    """标准食品基础字段"""
    barcode: Optional[str] = None
    name: str
    brand: Optional[str] = None
    default_weight: Optional[str] = None
    image_url: Optional[str] = None


class FoodCreate(FoodBase):
    """创建标准食品"""
    food_type_id: int


class FoodResponse(FoodBase):
    """食品响应"""
    id: int
    food_type_id: int
    avg_expiry_days: int = 7
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ ShopFood (店铺食品) ============

class ShopFoodBase(BaseModel):
    """店铺食品基础字段"""
    shelf_position: Optional[str] = None
    quantity: int = 0
    original_price: int  # 分为单位
    discount_price: int  # 分为单位


class ShopFoodCreate(ShopFoodBase):
    """创建店铺食品"""
    shop_id: int
    food_id: int
    discount_type: str = Field(..., pattern="^(mystery_box|clearance|time_limit)$")
    expiry_date: Optional[datetime] = None


class ShopFoodUpdate(BaseModel):
    """更新店铺食品"""
    quantity: Optional[int] = None
    discount_price: Optional[int] = None
    shelf_position: Optional[str] = None
    status: Optional[str] = None


class ShopFoodResponse(ShopFoodBase):
    """店铺食品响应"""
    id: int
    shop_id: int
    food_id: int
    discount_type: str
    expiry_date: Optional[datetime] = None
    risk_level: str = "low"
    status: str = "draft"
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    # 扩展字段(关联数据)
    food_name: Optional[str] = None
    food_type_name: Optional[str] = None
    food_type_color: Optional[str] = None
    shop_name: Optional[str] = None
    distance_km: Optional[float] = None  # 距离(公里)

    class Config:
        from_attributes = True


# ============ ShopType (店铺类型) ============

class ShopTypeResponse(BaseModel):
    """店铺类型响应"""
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: str = "#1890FF"

    class Config:
        from_attributes = True


# ============ FoodType (食品类型) ============

class FoodTypeResponse(BaseModel):
    """食品类型响应"""
    id: int
    name: str
    icon: Optional[str] = None
    color: str = "#52C41A"

    class Config:
        from_attributes = True


# ============ Nearby Search (附近搜索) ============

class NearbySearchParams(BaseModel):
    """附近搜索参数"""
    lat: float = Field(..., description="纬度")
    lng: float = Field(..., description="经度")
    distance: float = Field(5.0, description="搜索半径(公里)")
    food_type_id: Optional[int] = None
    risk_level: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None


# NearbyFoodsParams 是 NearbySearchParams 的别名
NearbyFoodsParams = NearbySearchParams
