"""
Pydantic schemas - 订单相关
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """创建订单"""
    customer_id: int
    shop_food_id: int
    quantity: int = Field(1, ge=1)


class OrderUpdate(BaseModel):
    """更新订单"""
    status: Optional[str] = Field(None, pattern="^(pending|paid|completed|cancelled)$")


class OrderResponse(BaseModel):
    """订单响应"""
    id: int
    customer_id: int
    shop_food_id: int
    quantity: int
    total_price: int  # 分为单位
    status: str
    pickup_code: Optional[str] = None
    created_at: Optional[datetime] = None

    # 扩展字段
    food_name: Optional[str] = None
    food_image: Optional[str] = None
    shop_name: Optional[str] = None
    shop_address: Optional[str] = None

    class Config:
        from_attributes = True


class OrderListParams(BaseModel):
    """订单列表参数"""
    customer_id: Optional[int] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class OrderDetailResponse(OrderResponse):
    """订单详情响应"""
    paid_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    # 额外信息
    shop_phone: Optional[str] = None
    shop_latitude: Optional[int] = None
    shop_longitude: Optional[int] = None
    discount_type: Optional[str] = None
    expiry_date: Optional[datetime] = None


class OrderListResponse(BaseModel):
    """订单列表响应"""
    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int
