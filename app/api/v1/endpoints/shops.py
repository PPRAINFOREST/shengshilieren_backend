"""
Shops API - 店铺相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.shop import Shop, ShopType
from app.schemas.shop import ShopResponse, ShopCreate, ShopUpdate
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/types")
async def get_shop_types(db: Session = Depends(get_db)):
    """获取店铺类型列表"""
    types = db.query(ShopType).all()
    return success_response(data=[{
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "icon": t.icon,
        "color": t.color
    } for t in types])


@router.get("/nearby")
async def get_nearby_shops(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    distance: float = Query(5.0, description="搜索半径(公里)"),
    db: Session = Depends(get_db)
):
    """获取附近店铺"""
    # 简化实现，实际应使用空间索引
    shops = db.query(Shop).filter(Shop.is_active == True).limit(20).all()
    return success_response(data=[{
        "id": s.id,
        "shop_name": s.shop_name,
        "address": s.address,
        "latitude": s.latitude / 10000000 if s.latitude else None,
        "longitude": s.longitude / 10000000 if s.longitude else None,
        "rating": s.rating / 10 if s.rating else 5.0,
        "verified": s.verified
    } for s in shops])


@router.get("/{shop_id}")
async def get_shop_detail(
    shop_id: int,
    db: Session = Depends(get_db)
):
    """获取店铺详情"""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        return error_response("店铺不存在")
    
    return success_response(data={
        "id": shop.id,
        "merchant_id": shop.merchant_id,
        "shop_name": shop.shop_name,
        "address": shop.address,
        "latitude": shop.latitude / 10000000 if shop.latitude else None,
        "longitude": shop.longitude / 10000000 if shop.longitude else None,
        "contact_phone": shop.contact_phone,
        "business_hours": shop.business_hours,
        "rating": shop.rating / 10 if shop.rating else 5.0,
        "verified": shop.verified,
        "total_orders": shop.total_orders
    })
