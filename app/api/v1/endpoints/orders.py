"""
Orders API - 订单相关接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import random
import string

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.order import Order, OrderStatus
from app.models.user import Customer
from app.models.shop import Shop
from app.models.food import ShopFood
from app.models.points import HunterPoint
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderDetailResponse, OrderListResponse
)
from app.schemas.response import success_response, error_response
from app.services.points_service import add_points, deduct_points
from app.services.order_service import create_order_logic, update_order_status_logic

router = APIRouter()


def generate_pickup_code() -> str:
    """生成6位取货码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@router.post("", response_model=dict)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建订单"""
    # 验证用户类型
    if current_user["type"] != "customer":
        return error_response("只有客户才能下单")
    
    customer = current_user["user"]
    
    # 获取店铺食品
    shop_food = db.query(ShopFood).filter(
        ShopFood.id == data.shop_food_id
    ).first()
    
    if not shop_food:
        return error_response("商品不存在")
    
    if shop_food.status != "active":
        return error_response("商品已下架")
    
    if shop_food.quantity < data.quantity:
        return error_response("库存不足")
    
    if shop_food.expiry_date < datetime.now():
        return error_response("商品已过期")
    
    # 创建订单
    total_price = shop_food.discount_price * data.quantity
    pickup_code = generate_pickup_code()
    
    order = Order(
        customer_id=customer.id,
        shop_food_id=shop_food.id,
        quantity=data.quantity,
        total_price=total_price,
        pickup_code=pickup_code,
        status=OrderStatus.PENDING
    )
    
    db.add(order)
    
    # 扣减库存
    shop_food.quantity -= data.quantity
    if shop_food.quantity == 0:
        shop_food.status = "sold_out"
    
    db.commit()
    db.refresh(order)
    
    return success_response(
        data={
            "order_id": order.id,
            "pickup_code": order.pickup_code,
            "total_price": order.total_price
        },
        msg="下单成功"
    )


@router.get("/my", response_model=dict)
def get_my_orders(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取我的订单列表"""
    if current_user["type"] != "customer":
        return error_response("只有客户才能查看订单")
    
    customer = current_user["user"]
    
    query = db.query(Order).filter(Order.customer_id == customer.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "orders": [
                {
                    "id": o.id,
                    "pickup_code": o.pickup_code,
                    "quantity": o.quantity,
                    "total_price": o.total_price,
                    "status": o.status,
                    "created_at": o.created_at.isoformat() if o.created_at else None
                }
                for o in orders
            ]
        }
    )


@router.get("/{order_id}", response_model=dict)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return error_response("订单不存在")
    
    # 验证权限
    if current_user["type"] == "customer" and order.customer_id != current_user["user"].id:
        return error_response("无权限查看此订单")
    
    if current_user["type"] == "merchant":
        # 商家只能查看自己店铺的订单
        shop_food = db.query(ShopFood).filter(
            ShopFood.id == order.shop_food_id
        ).first()
        if shop_food:
            shop = db.query(Shop).filter(Shop.id == shop_food.shop_id).first()
            if shop.merchant_id != current_user["user"].id:
                return error_response("无权限查看此订单")
    
    # 获取详细信息
    shop_food = db.query(ShopFood).filter(ShopFood.id == order.shop_food_id).first()
    
    return success_response(
        data={
            "id": order.id,
            "pickup_code": order.pickup_code,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "food": {
                "name": shop_food.food.name if shop_food else None,
                "image_url": shop_food.food.image_url if shop_food else None
            } if shop_food else None
        }
    )


@router.post("/{order_id}/complete", response_model=dict)
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """确认收货/完成订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return error_response("订单不存在")
    
    if order.status != OrderStatus.PAID:
        return error_response("订单状态不正确")
    
    # 更新状态
    order.status = OrderStatus.COMPLETED
    
    # 给客户加积分
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if customer:
        points = add_points(
            db=db,
            customer_id=customer.id,
            amount=10,  # 购买奖励10积分
            source="purchase",
            description="购买临期食品奖励"
        )
    
    db.commit()
    
    return success_response(msg="订单已完成")


@router.post("/{order_id}/cancel", response_model=dict)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """取消订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return error_response("订单不存在")
    
    if order.status != OrderStatus.PENDING:
        return error_response("只能取消待支付订单")
    
    # 验证权限
    if current_user["type"] == "customer" and order.customer_id != current_user["user"].id:
        return error_response("无权限取消此订单")
    
    # 更新状态
    order.status = OrderStatus.CANCELLED
    
    # 恢复库存
    shop_food = db.query(ShopFood).filter(ShopFood.id == order.shop_food_id).first()
    if shop_food:
        shop_food.quantity += order.quantity
        if shop_food.status == "sold_out":
            shop_food.status = "active"
    
    db.commit()
    
    return success_response(msg="订单已取消")
