"""
Pydantic schemas - 统一导出
"""
from .response import DataResponse, ListResponse, PageParams, ErrorResponse
from .user import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    MerchantCreate,
    MerchantUpdate,
    MerchantResponse,
    LoginRequest,
    LoginResponse,
    TokenPayload,
)
from .shop import (
    ShopTypeResponse,
    FoodTypeResponse,
    FoodResponse,
    ShopFoodCreate,
    ShopFoodResponse,
    NearbyFoodsParams,
)
from .order import OrderCreate, OrderUpdate, OrderResponse, OrderListParams
from .points import (
    ScanCreate,
    ScanResponse,
    PointRecordResponse,
    PointBalanceResponse,
    ChallengeResponse,
    UserChallengeResponse,
    BadgeResponse,
    UserBadgeResponse,
    LeaderboardEntry,
)
from .recommendation import (
    PreferenceUpdate,
    FlavorPreferenceUpdate,
    FoodBehaviorCreate,
    FoodBehaviorResponse,
    AIValidateRequest,
    AIValidateResponse,
    AIShelfPosition,
    AIAuditRequest,
    AIAuditResponse,
    NotificationResponse,
    CustomerStatsResponse,
)

__all__ = [
    # Response
    "DataResponse",
    "ListResponse",
    "PageParams",
    "ErrorResponse",
    # User
    "CustomerRegister",
    "CustomerLogin",
    "CustomerResponse",
    "MerchantRegister",
    "MerchantLogin",
    "MerchantResponse",
    "TokenPayload",
    # Shop
    "ShopTypeResponse",
    "FoodTypeResponse",
    "FoodResponse",
    "ShopFoodCreate",
    "ShopFoodResponse",
    "NearbyFoodsParams",
    # Order
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderListParams",
    # Points
    "ScanCreate",
    "ScanResponse",
    "PointRecordResponse",
    "PointBalanceResponse",
    "ChallengeResponse",
    "UserChallengeResponse",
    "BadgeResponse",
    "UserBadgeResponse",
    "LeaderboardEntry",
    # Recommendation
    "PreferenceUpdate",
    "FlavorPreferenceUpdate",
    "FoodBehaviorCreate",
    "FoodBehaviorResponse",
    "AIValidateRequest",
    "AIValidateResponse",
    "AIShelfPosition",
    "AIAuditRequest",
    "AIAuditResponse",
    "NotificationResponse",
    "CustomerStatsResponse",
]
