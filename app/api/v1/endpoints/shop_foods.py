"""
ShopFoods API - 店铺食品相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.shop import Shop
from app.models.food import ShopFood
from app.schemas.shop import ShopFoodCreate, ShopFoodResponse
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/nearby")
async def get_nearby_foods(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    distance: float = Query(5.0, description="搜索半径(公里)"),
    food_type_id: Optional[int] = Query(None, description="食品类型ID"),
    db: Session = Depends(get_db)
):
    """获取附近的临期食品"""
    # 简化实现
    query = db.query(ShopFood).filter(
        ShopFood.status == "active",
        ShopFood.quantity > 0
    )
    
    if food_type_id:
        query = query.join(ShopFood.food).filter(ShopFood.food_id == food_type_id)
    
    foods = query.limit(50).all()
    
    return success_response(data=[{
        "id": f.id,
        "shop_id": f.shop_id,
        "food_id": f.food_id,
        "food_name": f.food.name if f.food else None,
        "original_price": f.original_price,
        "discount_price": f.discount_price,
        "discount_type": f.discount_type,
        "risk_level": f.risk_level,
        "expiry_date": f.expiry_date.isoformat() if f.expiry_date else None
    } for f in foods])


@router.get("/{food_id}")
async def get_shop_food_detail(
    food_id: int,
    db: Session = Depends(get_db)
):
    """获取店铺食品详情"""
    food = db.query(ShopFood).filter(ShopFood.id == food_id).first()
    if not food:
        return error_response("商品不存在")
    
    return success_response(data={
        "id": food.id,
        "shop_id": food.shop_id,
        "food_id": food.food_id,
        "food_name": food.food.name if food.food else None,
        "shelf_position": food.shelf_position,
        "quantity": food.quantity,
        "original_price": food.original_price,
        "discount_price": food.discount_price,
        "discount_type": food.discount_type,
        "risk_level": food.risk_level,
        "status": food.status,
        "expiry_date": food.expiry_date.isoformat() if food.expiry_date else None
    })
