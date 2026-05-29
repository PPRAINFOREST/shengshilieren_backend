"""
订单和交易相关模型
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderStatus(str, PyEnum):
    """订单状态枚举"""
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    COMPLETED = "completed" # 已完成
    CANCELLED = "cancelled" # 已取消
    REFUNDED = "refunded"   # 已退款


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False)  # 订单号
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    shop_food_id = Column(Integer, ForeignKey("shop_foods.id"), nullable=False)
    quantity = Column(Integer, default=1)
    total_price = Column(Integer)  # 总价(分)
    status = Column(
        Enum("pending", "paid", "completed", "cancelled", name="order_status_enum"),
        default="pending"
    )
    pickup_code = Column(String(10))  # 取货码
    paid_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 索引
    __table_args__ = (
        Index("idx_order_customer", "customer_id"),
        Index("idx_order_status", "status"),
        Index("idx_order_created", "created_at"),
    )

    # 关系
    customer = relationship("Customer", back_populates="orders")
    shop_food = relationship("ShopFood", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.order_no}>"
