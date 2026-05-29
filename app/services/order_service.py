"""
订单服务 - 订单创建和状态更新
"""
from datetime import datetime
from typing import Optional
import random
import string

from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus
from app.models.food import ShopFood
from app.models.user import Customer


def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"FSH{timestamp}{random_str}"


def generate_pickup_code() -> str:
    """生成取货码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def create_order_logic(
    db: Session,
    customer_id: int,
    shop_food_id: int,
    quantity: int = 1
) -> Order:
    """
    创建订单逻辑
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        shop_food_id: 店铺食品ID
        quantity: 数量
    
    Returns:
        Order: 创建的订单
    """
    # 检查客户是否存在
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("客户不存在")
    
    # 检查店铺食品是否存在且有库存
    shop_food = db.query(ShopFood).filter(ShopFood.id == shop_food_id).first()
    if not shop_food:
        raise ValueError("商品不存在")
    
    if shop_food.status != "active":
        raise ValueError("商品未上架")
    
    if shop_food.quantity < quantity:
        raise ValueError("库存不足")
    
    # 计算总价
    total_price = shop_food.discount_price * quantity
    
    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        customer_id=customer_id,
        shop_food_id=shop_food_id,
        quantity=quantity,
        total_price=total_price,
        status=OrderStatus.PENDING,
        pickup_code=generate_pickup_code()
    )
    db.add(order)
    
    # 扣减库存
    shop_food.quantity -= quantity
    if shop_food.quantity == 0:
        shop_food.status = "sold_out"
    
    db.commit()
    db.refresh(order)
    
    return order


def update_order_status_logic(
    db: Session,
    order_id: int,
    new_status: str,
    cancellation_reason: Optional[str] = None
) -> Order:
    """
    更新订单状态逻辑
    
    Args:
        db: 数据库会话
        order_id: 订单ID
        new_status: 新状态
        cancellation_reason: 取消原因
    
    Returns:
        Order: 更新后的订单
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError("订单不存在")
    
    current_status = order.status
    
    # 状态转换验证
    valid_transitions = {
        OrderStatus.PENDING.value: [OrderStatus.PAID.value, OrderStatus.CANCELLED.value],
        OrderStatus.PAID.value: [OrderStatus.COMPLETED.value, OrderStatus.CANCELLED.value],
        OrderStatus.COMPLETED.value: [],
        OrderStatus.CANCELLED.value: [OrderStatus.REFUNDED.value],
        OrderStatus.REFUNDED.value: []
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise ValueError(f"不允许的状态转换: {current_status} -> {new_status}")
    
    # 更新状态
    order.status = new_status
    
    # 处理时间戳
    now = datetime.now()
    if new_status == OrderStatus.PAID.value:
        order.paid_at = now
    elif new_status == OrderStatus.COMPLETED.value:
        order.completed_at = now
        # 更新客户统计
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if customer:
            customer.total_orders += 1
            # 更新店铺订单数
            shop_food = db.query(ShopFood).filter(ShopFood.id == order.shop_food_id).first()
            if shop_food:
                from app.models.shop import Shop
                shop = db.query(Shop).filter(Shop.id == shop_food.shop_id).first()
                if shop:
                    shop.total_orders += 1
    elif new_status == OrderStatus.CANCELLED.value:
        order.cancelled_at = now
        order.cancellation_reason = cancellation_reason
        # 恢复库存
        shop_food = db.query(ShopFood).filter(ShopFood.id == order.shop_food_id).first()
        if shop_food:
            shop_food.quantity += order.quantity
            if shop_food.status == "sold_out":
                shop_food.status = "active"
    
    db.commit()
    db.refresh(order)
    
    return order
