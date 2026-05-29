"""
Foods API - 食品相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.food import Food, FoodType
from app.schemas.shop import FoodResponse
from app.schemas.response import success_response

router = APIRouter()


@router.get("/types")
async def get_food_types(db: Session = Depends(get_db)):
    """获取食品类型列表"""
    types = db.query(FoodType).all()
    return success_response(data=[{
        "id": t.id,
        "name": t.name,
        "icon": t.icon,
        "color": t.color
    } for t in types])


@router.get("/barcode/{barcode}")
async def get_food_by_barcode(
    barcode: str,
    db: Session = Depends(get_db)
):
    """通过条形码获取食品信息"""
    food = db.query(Food).filter(Food.barcode == barcode).first()
    if not food:
        return success_response(data=None)
    
    return success_response(data={
        "id": food.id,
        "barcode": food.barcode,
        "name": food.name,
        "brand": food.brand,
        "food_type_id": food.food_type_id,
        "avg_expiry_days": food.avg_expiry_days,
        "image_url": food.image_url
    })


@router.get("/{food_id}")
async def get_food_detail(
    food_id: int,
    db: Session = Depends(get_db)
):
    """获取食品详情"""
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        return success_response(data=None)
    
    return success_response(data={
        "id": food.id,
        "barcode": food.barcode,
        "name": food.name,
        "brand": food.brand,
        "default_weight": food.default_weight,
        "food_type_id": food.food_type_id,
        "avg_expiry_days": food.avg_expiry_days,
        "image_url": food.image_url
    })
