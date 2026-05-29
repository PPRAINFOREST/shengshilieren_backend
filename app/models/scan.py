"""
扫码记录相关的数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserScan(Base):
    """用户扫码记录表"""
    __tablename__ = "user_scans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, comment="客户ID")
    barcode = Column(String(50), nullable=False, comment="条形码")
    product_name = Column(String(100), comment="商品名称")
    expiry_date = Column(DateTime, comment="过期日期")
    image_url = Column(String(255), comment="上传的图片URL")
    latitude = Column(DECIMAL(10, 8), comment="扫码位置纬度")
    longitude = Column(DECIMAL(11, 8), comment="扫码位置经度")
    address = Column(String(255), comment="扫码位置地址")
    status = Column(Enum("pending", "approved", "rejected", name="scan_status_enum"),
                   default="pending", comment="审核状态")
    points_earned = Column(Integer, default=0, comment="获得的积分")
    audit_comment = Column(String(255), comment="审核备注")
    audited_at = Column(DateTime, comment="审核时间")
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    customer = relationship("Customer", back_populates="scans")


class CustomerFoodBehavior(Base):
    """用户食品行为记录表（推荐系统用）"""
    __tablename__ = "customer_food_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, comment="客户ID")
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="CASCADE"), nullable=False, comment="食品ID")
    behavior_type = Column(Enum("purchase", "scan", "browse", "favorite", "reject", name="behavior_type_enum"),
                          nullable=False, comment="行为类型")
    shop_food_id = Column(Integer, ForeignKey("shop_foods.id"), comment="店铺食品ID（购买时）")
    rating = Column(Integer, comment="购买后评分 1-5")
    context = Column(Text, comment="上下文：时间/地点/天气等JSON")
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    customer = relationship("Customer", back_populates="food_behaviors")
    food = relationship("Food", back_populates="behaviors")
    shop_food = relationship("ShopFood")
