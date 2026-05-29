"""
API endpoints - API接口路由
"""
from fastapi import APIRouter

# 创建路由
api_router = APIRouter()

# 动态导入和注册路由
def setup_routes():
    from app.api.v1.endpoints import auth
    from app.api.v1.endpoints import customers
    from app.api.v1.endpoints import merchants
    from app.api.v1.endpoints import shops
    from app.api.v1.endpoints import foods
    from app.api.v1.endpoints import shop_foods
    from app.api.v1.endpoints import orders
    from app.api.v1.endpoints import points
    from app.api.v1.endpoints import challenges
    from app.api.v1.endpoints import recommendations
    from app.api.v1.endpoints import notifications
    from app.api.v1.endpoints import upload
    from app.api.v1.endpoints import ai

    # 认证模块
    api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

    # 客户模块
    api_router.include_router(customers.router, prefix="/customers", tags=["客户"])

    # 商家模块
    api_router.include_router(merchants.router, prefix="/merchants", tags=["商家"])

    # 店铺模块
    api_router.include_router(shops.router, prefix="/shops", tags=["店铺"])

    # 食品模块
    api_router.include_router(foods.router, prefix="/foods", tags=["食品"])

    # 店铺食品模块
    api_router.include_router(shop_foods.router, prefix="/shop-foods", tags=["店铺食品"])

    # 订单模块
    api_router.include_router(orders.router, prefix="/orders", tags=["订单"])

    # 积分模块
    api_router.include_router(points.router, prefix="/points", tags=["积分"])

    # 挑战模块
    api_router.include_router(challenges.router, prefix="/challenges", tags=["挑战"])

    # 推荐模块
    api_router.include_router(recommendations.router, prefix="/recommendations", tags=["推荐"])

    # 通知模块
    api_router.include_router(notifications.router, prefix="/notifications", tags=["通知"])

    # 上传模块
    api_router.include_router(upload.router, prefix="/upload", tags=["上传"])

    # AI模块
    api_router.include_router(ai.router, prefix="/ai", tags=["AI服务"])

# 设置路由
setup_routes()
