"""
Merchants API - 商家相关接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import Merchant
from app.schemas.user import MerchantResponse, MerchantUpdate
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/me")
async def get_merchant_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取当前商家信息"""
    merchant = db.query(Merchant).filter(Merchant.id == current_user["id"]).first()
    if not merchant:
        return error_response("商家不存在")
    
    return success_response(data={
        "id": merchant.id,
        "phone": merchant.phone,
        "store_name": merchant.store_name,
        "store_type_id": merchant.store_type_id,
        "address": merchant.address,
        "verified": merchant.verified,
        "rating": merchant.rating / 10 if merchant.rating else 5.0,
        "total_orders": merchant.total_orders
    })


@router.put("/me")
async def update_merchant_info(
    update_data: MerchantUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新商家信息"""
    merchant = db.query(Merchant).filter(Merchant.id == current_user["id"]).first()
    if not merchant:
        return error_response("商家不存在")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(merchant, key, value)
    
    db.commit()
    db.refresh(merchant)
    
    return success_response(message="更新成功")
