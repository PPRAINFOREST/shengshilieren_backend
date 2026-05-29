"""
积分系统相关的数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class HunterPoint(Base):
    """积分变动记录表"""
    __tablename__ = "hunter_points"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, comment="客户ID")
    point_type = Column(Enum("earn", "spend", "reward", "refund", name="point_type_enum"),
                       nullable=False, comment="类型：earn获得/spend消耗/reward奖励/refund退还")
    amount = Column(Integer, nullable=False, comment="变动数量")
    source = Column(String(50), comment="来源：scan/audit/challenge/exchange/order")
    source_id = Column(Integer, comment="关联ID（扫码ID/挑战ID/订单ID等）")
    description = Column(String(255), comment="描述")
    created_at = Column(DateTime, server_default=func.now())

    # 关联
    customer = relationship("Customer", back_populates="points_records")


class PointSource(Base):
    """积分来源配置表"""
    __tablename__ = "point_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_key = Column(String(50), unique=True, nullable=False, comment="来源标识")
    source_name = Column(String(50), nullable=False, comment="来源名称")
    base_points = Column(Integer, nullable=False, comment="基础积分")
    description = Column(Text, comment="说明")
    is_active = Column(String(10), default="active", comment="状态")
    created_at = Column(DateTime, server_default=func.now())


class PointRule(Base):
    """积分规则配置表"""
    __tablename__ = "point_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_type = Column(String(50), nullable=False, comment="规则类型")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    points = Column(Integer, nullable=False, comment="积分值")
    daily_limit = Column(Integer, comment="每日限制")
    description = Column(String(255), comment="说明")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
