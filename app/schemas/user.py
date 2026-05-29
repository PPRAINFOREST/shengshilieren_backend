"""
Pydantic schemas - 用户相关
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============ Customer (客户) ============

class CustomerBase(BaseModel):
    """客户基础字段"""
    phone: str = Field(..., min_length=11, max_length=11)
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class CustomerCreate(CustomerBase):
    """创建客户"""
    password: str = Field(..., min_length=6)
    hometown: Optional[str] = None


class CustomerUpdate(BaseModel):
    """更新客户"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    hometown: Optional[str] = None


class CustomerResponse(CustomerBase):
    """客户响应"""
    id: int
    points: int = 0
    carbon_saved: float = 0.0
    food_saved: float = 0.0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Merchant (商家) ============

class MerchantBase(BaseModel):
    """商家基础字段"""
    phone: str = Field(..., min_length=11, max_length=11)


class MerchantCreate(MerchantBase):
    """创建商家"""
    password: str = Field(..., min_length=6)


class MerchantUpdate(BaseModel):
    """更新商家"""
    store_name: Optional[str] = None
    contact_phone: Optional[str] = None
    business_hours: Optional[str] = None


class MerchantResponse(MerchantBase):
    """商家响应"""
    id: int
    store_name: str
    store_type_id: int
    verified: bool = False
    rating: float = 5.0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Auth (认证) ============

class LoginRequest(BaseModel):
    """登录请求"""
    phone: str
    password: str
    user_type: str = Field(..., pattern="^(customer|merchant)$")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str


class TokenPayload(BaseModel):
    """Token载荷"""
    sub: str  # 用户ID
    user_type: str  # customer 或 merchant
    exp: int  # 过期时间
