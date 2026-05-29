"""
通知相关模型
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)  # 用户ID
    user_type = Column(
        Enum("customer", "merchant", name="notification_user_type_enum"),
        nullable=False
    )
    notification_type = Column(
        Enum(
            "point_change",      # 积分变动
            "challenge_update",  # 挑战更新
            "badge_unlock",      # 徽章解锁
            "order_status",      # 订单状态
            "new_nearby",       # 附近新食品
            "system",           # 系统通知
            name="notification_type_enum"
        ),
        nullable=False
    )
    title = Column(String(100), nullable=False)
    content = Column(Text)
    data = Column(Text)  # JSON: 跳转参数等
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    # 索引
    __table_args__ = (
        Index("idx_notification_user", "user_id", "user_type"),
        Index("idx_notification_read", "is_read"),
        Index("idx_notification_created", "created_at"),
    )

    def __repr__(self):
        return f"<Notification {self.user_id}: {self.title}>"


class UserDevice(Base):
    """用户设备表（用于推送）"""
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False)
    user_type = Column(
        Enum("customer", "merchant", name="device_user_type_enum"),
        nullable=False
    )
    device_type = Column(
        Enum("ios", "android", "harmonyos", name="device_type_enum"),
        nullable=False
    )
    device_token = Column(String(255), nullable=False)  # 推送Token
    is_active = Column(Boolean, default=True)
    last_active_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

    # 索引
    __table_args__ = (
        Index("idx_device_user", "user_id", "user_type"),
        Index("idx_device_token", "device_token"),
    )

    def __repr__(self):
        return f"<UserDevice {self.device_type}: {self.user_id}>"
