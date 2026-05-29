"""
挑战和成就相关模型
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class ChallengeStatus(str, PyEnum):
    """挑战状态枚举"""
    ACTIVE = "active"      # 进行中
    COMPLETED = "completed" # 已完成
    EXPIRED = "expired"    # 已过期


class ChallengeType(str, PyEnum):
    """挑战类型枚举"""
    FOOD_RESCUE = "food_rescue"    # 救粮
    CARBON_REDUCE = "carbon_reduce"  # 减碳
    STREAK = "streak"            # 连续
    SOCIAL = "social"            # 社交


class Challenge(Base):
    """挑战表"""
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    challenge_type = Column(
        Enum("food_rescue", "carbon_reduce", "streak", "social", name="challenge_type_enum"),
        nullable=False
    )  # 救粮/减碳/连续/社交
    target = Column(Integer, nullable=False)  # 目标值
    unit = Column(String(20), nullable=False)  # 单位：kg/次数/天
    reward_points = Column(Integer, nullable=False)  # 完成奖励积分
    badge_id = Column(Integer, ForeignKey("badges.id"))  # 完成后获得的徽章
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(
        Enum("active", "completed", "expired", name="challenge_status_enum"),
        default="active"
    )
    icon = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    participants = relationship("UserChallenge", back_populates="challenge")
    badge = relationship("Badge")

    def __repr__(self):
        return f"<Challenge {self.name}>"


class UserChallenge(Base):
    """用户挑战参与表"""
    __tablename__ = "user_challenges"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    current = Column(Integer, default=0)  # 当前进度
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)

    # 索引
    __table_args__ = (
        Index("idx_user_challenge_unique", "challenge_id", "customer_id", unique=True),
    )

    # 关系
    challenge = relationship("Challenge", back_populates="participants")
    customer = relationship("Customer", back_populates="challenges")

    def __repr__(self):
        return f"<UserChallenge {self.customer_id} in {self.challenge_id}>"


class Badge(Base):
    """成就徽章表"""
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))
    icon = Column(String(50))
    badge_type = Column(
        Enum("food_rescue", "carbon_reduce", "streak", "special", name="badge_type_enum"),
        nullable=False
    )
    unlock_condition = Column(Text)  # 解锁条件描述
    reward_points = Column(Integer, default=0)  # 奖励积分
    rarity = Column(Enum("common", "rare", "epic", "legendary", name="badge_rarity_enum"), default="common")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # 关系
    users = relationship("UserBadge", back_populates="badge")
    challenges = relationship("Challenge")

    def __repr__(self):
        return f"<Badge {self.name}>"


class UserBadge(Base):
    """用户徽章表"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.now)

    # 关系
    customer = relationship("Customer", back_populates="badges")
    badge = relationship("Badge", back_populates="users")

    def __repr__(self):
        return f"<UserBadge {self.customer_id} - {self.badge_id}>"
