"""
数据库模型
"""
from app.models.user import Customer, Merchant
from app.models.shop import Shop, ShopType
from app.models.food import Food, FoodType, ShopFood, FoodFlavorTag
from app.models.order import Order
from app.models.scan import UserScan, CustomerFoodBehavior
from app.models.points import HunterPoint, PointSource, PointRule
from app.models.challenge import Challenge, UserChallenge, Badge, UserBadge
from app.models.notification import Notification
from app.models.ai import AIServiceLog, ScanAudit
from app.models.preference import (
    CustomerPreference,
    CustomerCategoryPreference,
    CustomerManualPreference
)
from app.models.recommendation import (
    FoodRecommendation,
    RecommendationFeedback,
    CustomerFlavorPreference
)

# 所有模型的列表，用于创建表
__all__ = [
    # 用户
    "Customer",
    "Merchant",
    # 店铺
    "Shop",
    "ShopType",
    # 食品
    "Food",
    "FoodType",
    "ShopFood",
    # 订单
    "Order",
    # 扫码
    "UserScan",
    "CustomerFoodBehavior",
    # 积分
    "HunterPoint",
    "PointSource",
    "PointRule",
    # 挑战
    "Challenge",
    "UserChallenge",
    "Badge",
    "UserBadge",
    # 通知
    "Notification",
    # AI
    "AIServiceLog",
    "ScanAudit",
    # 偏好
    "CustomerPreference",
    "CustomerCategoryPreference",
    "CustomerManualPreference",
    # 推荐
    "FoodRecommendation",
    "RecommendationFeedback",
    "FoodFlavorTag",
    "CustomerFlavorPreference",
]
