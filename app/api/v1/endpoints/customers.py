"""
Customers API - 客户相关接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import Customer
from app.schemas.user import CustomerResponse, CustomerUpdate
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/me")
async def get_customer_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取当前客户信息"""
    customer = db.query(Customer).filter(Customer.id == current_user["id"]).first()
    if not customer:
        return error_response("客户不存在")
    
    return success_response(data={
        "id": customer.id,
        "phone": customer.phone,
        "nickname": customer.nickname,
        "avatar": customer.avatar,
        "points": customer.points,
        "carbon_saved": float(customer.carbon_saved or 0),
        "food_saved": float(customer.food_saved or 0),
        "total_orders": customer.total_orders
    })


@router.put("/me")
async def update_customer_info(
    update_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新客户信息"""
    customer = db.query(Customer).filter(Customer.id == current_user["id"]).first()
    if not customer:
        return error_response("客户不存在")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(customer, key, value)
    
    db.commit()
    db.refresh(customer)
    
    return success_response(message="更新成功")
