"""
Pydantic schemas - 扫码、积分、挑战相关
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============ UserScan (扫码记录) ============

class ScanCreate(BaseModel):
    """创建扫码记录"""
    barcode: str
    product_name: Optional[str] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ScanResponse(BaseModel):
    """扫码记录响应"""
    id: int
    customer_id: int
    barcode: str
    product_name: Optional[str] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    points_earned: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ HunterPoint (积分记录) ============

class PointRecordResponse(BaseModel):
    """积分记录响应"""
    id: int
    customer_id: int
    type: str  # earn/spend/reward/refund
    amount: int
    source: str
    source_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PointBalanceResponse(BaseModel):
    """积分余额响应"""
    customer_id: int
    balance: int
    total_earned: int
    total_spent: int


# ============ Challenge (挑战) ============

class ChallengeResponse(BaseModel):
    """挑战响应"""
    id: int
    name: str
    description: Optional[str] = None
    target: float
    unit: str
    reward_points: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserChallengeResponse(BaseModel):
    """用户挑战响应"""
    id: int
    challenge_id: int
    customer_id: int
    current: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 扩展字段
    challenge_name: Optional[str] = None
    challenge_description: Optional[str] = None
    target: Optional[float] = None
    unit: Optional[str] = None
    reward_points: Optional[int] = None
    progress_percent: Optional[float] = None

    class Config:
        from_attributes = True


# ============ Badge (成就徽章) ============

class BadgeResponse(BaseModel):
    """徽章响应"""
    id: int
    name: str
    description: Optional[str] = None
    icon: str
    reward_points: int = 0
    unlock_condition: Optional[str] = None

    class Config:
        from_attributes = True


class UserBadgeResponse(BaseModel):
    """用户徽章响应"""
    id: int
    customer_id: int
    badge_id: int
    unlocked_at: Optional[datetime] = None

    # 扩展字段
    badge_name: Optional[str] = None
    badge_icon: Optional[str] = None
    badge_description: Optional[str] = None

    class Config:
        from_attributes = True


# ============ Leaderboard (排行榜) ============

class LeaderboardEntry(BaseModel):
    """排行榜条目"""
    rank: int
    customer_id: int
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    score: float
    unit: str
