"""
Date utilities - 日期时间相关工具
"""
from datetime import datetime, timedelta
from typing import List


def calculate_risk_level(expiry_date: datetime, avg_expiry_days: int = 7) -> str:
    """
    根据到期日期计算风险等级
    
    Args:
        expiry_date: 到期日期
        avg_expiry_days: 平均保质期天数（用于参考）
    
    Returns:
        risk_level: 'low', 'medium', 'high', 'critical'
    """
    now = datetime.now()
    days_remaining = (expiry_date - now).days
    
    if days_remaining < 0:
        return "expired"
    elif days_remaining == 0:
        return "critical"
    elif days_remaining <= 1:
        return "high"
    elif days_remaining <= 3:
        return "medium"
    else:
        return "low"


def get_expiry_warning_message(days_remaining: int) -> str:
    """根据剩余天数返回警告消息"""
    if days_remaining < 0:
        return "已过期"
    elif days_remaining == 0:
        return "今天过期，请尽快食用！"
    elif days_remaining == 1:
        return "明天过期"
    elif days_remaining <= 3:
        return f"还剩{days_remaining}天"
    else:
        return f"还剩{days_remaining}天"


def get_time_slot() -> str:
    """
    获取当前时间段
    
    Returns:
        'morning': 早餐 (6:00-10:00)
        'noon': 午餐 (10:00-14:00)
        'afternoon': 下午 (14:00-18:00)
        'evening': 晚餐 (18:00-22:00)
        'night': 宵夜 (22:00-06:00)
    """
    hour = datetime.now().hour
    
    if 6 <= hour < 10:
        return "morning"
    elif 10 <= hour < 14:
        return "noon"
    elif 14 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"


def get_week_start_end() -> tuple:
    """获取本周一和周日的日期"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return (
        week_start.replace(hour=0, minute=0, second=0, microsecond=0),
        week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
    )


def get_date_range(days: int) -> List[datetime]:
    """获取最近N天的日期列表"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return [today - timedelta(days=i) for i in range(days)]


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间为字符串"""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析字符串为日期时间"""
    return datetime.strptime(date_str, format_str)
