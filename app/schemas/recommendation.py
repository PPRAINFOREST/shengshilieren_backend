"""
Pydantic schemas - 推荐系统、AI服务相关
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============ Recommendation (推荐) ============

class PreferenceUpdate(BaseModel):
    """更新用户偏好"""
    favorite_types: Optional[List[int]] = None
    favorite_flavors: Optional[List[str]] = None
    disliked_ingredients: Optional[List[str]] = None
    price_range_min: Optional[int] = None
    price_range_max: Optional[int] = None
    risk_preference: str = Field("normal", pattern="^(safe|normal|adventurous)$")


class FlavorPreferenceUpdate(BaseModel):
    """更新口味偏好"""
    flavor_tag: str
    preference_level: str = Field(..., pattern="^(like|neutral|dislike)$")


class FoodBehaviorCreate(BaseModel):
    """记录食品行为"""
    food_id: int
    behavior_type: str = Field(..., pattern="^(purchase|scan|browse|favorite|reject)$")
    shop_food_id: Optional[int] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class FoodBehaviorResponse(BaseModel):
    """食品行为响应"""
    id: int
    customer_id: int
    food_id: int
    behavior_type: str
    rating: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ AI Service (AI服务) ============

class AIValidateRequest(BaseModel):
    """AI验证货架请求"""
    image_url: str
    shop_id: int


class AIShelfPosition(BaseModel):
    """AI识别出的货架位置"""
    shelf_id: str
    row: int
    column: int
    confidence: float = Field(..., ge=0, le=1)
    description: Optional[str] = None


class AIValidateResponse(BaseModel):
    """AI验证响应"""
    success: bool
    positions: List[AIShelfPosition]
    message: Optional[str] = None


class AIAuditRequest(BaseModel):
    """AI审核扫码请求"""
    image_url: str
    barcode: str


class AIAuditResponse(BaseModel):
    """AI审核响应"""
    success: bool
    product_name: Optional[str] = None
    brand: Optional[str] = None
    expiry_date: Optional[str] = None
    risk_level: Optional[str] = None
    suggestion: Optional[str] = None
    points_estimate: int = 0


# ============ Notification (通知) ============

class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    customer_id: int
    title: str
    content: str
    type: str
    is_read: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ Statistics (统计数据) ============

class CustomerStatsResponse(BaseModel):
    """客户统计数据"""
    customer_id: int
    total_orders: int
    total_points: int
    carbon_saved: float  # kg
    food_saved: float    # kg
    challenges_completed: int
    badges_earned: int
    scans_submitted: int
