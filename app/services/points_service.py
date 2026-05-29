"""
积分服务 - 积分增删改查
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.points import HunterPoint, PointSource
from app.models.user import Customer


def add_points(
    db: Session,
    customer_id: int,
    amount: int,
    source: str,
    source_id: Optional[int] = None,
    description: str = ""
) -> HunterPoint:
    """
    增加积分
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        amount: 积分数量
        source: 来源 (scan/purchase/challenge/badge/invite)
        source_id: 来源ID
        description: 描述
    
    Returns:
        HunterPoint: 积分记录
    """
    # 获取客户当前积分
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("客户不存在")
    
    # 计算变动后余额
    new_balance = customer.points + amount
    
    # 创建积分记录
    point_record = HunterPoint(
        customer_id=customer_id,
        point_type=PointSource.EARN,
        amount=amount,
        source=source,
        source_id=source_id,
        description=description,
        balance_after=new_balance
    )
    db.add(point_record)
    
    # 更新客户积分
    customer.points = new_balance
    db.commit()
    db.refresh(point_record)
    
    return point_record


def deduct_points(
    db: Session,
    customer_id: int,
    amount: int,
    source: str,
    source_id: Optional[int] = None,
    description: str = ""
) -> HunterPoint:
    """
    扣除积分
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        amount: 积分数量
        source: 来源
        source_id: 来源ID
        description: 描述
    
    Returns:
        HunterPoint: 积分记录
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("客户不存在")
    
    if customer.points < amount:
        raise ValueError("积分不足")
    
    new_balance = customer.points - amount
    
    point_record = HunterPoint(
        customer_id=customer_id,
        point_type=PointSource.DEDUCT,
        amount=-amount,
        source=source,
        source_id=source_id,
        description=description,
        balance_after=new_balance
    )
    db.add(point_record)
    
    customer.points = new_balance
    db.commit()
    db.refresh(point_record)
    
    return point_record


def get_point_history(
    db: Session,
    customer_id: int,
    page: int = 1,
    page_size: int = 20,
    point_type: Optional[str] = None
) -> tuple[List[HunterPoint], int]:
    """
    获取积分历史
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        page: 页码
        page_size: 每页数量
        point_type: 积分类型过滤
    
    Returns:
        (记录列表, 总数)
    """
    query = db.query(HunterPoint).filter(HunterPoint.customer_id == customer_id)
    
    if point_type:
        query = query.filter(HunterPoint.point_type == point_type)
    
    total = query.count()
    records = query.order_by(desc(HunterPoint.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    return records, total


def get_point_balance(db: Session, customer_id: int) -> dict:
    """
    获取积分余额和统计
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
    
    Returns:
        dict: 积分余额和统计信息
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("客户不存在")
    
    # 获取今日积分
    today = datetime.now().date()
    today_points = db.query(HunterPoint).filter(
        HunterPoint.customer_id == customer_id,
        HunterPoint.created_at >= today
    ).all()
    
    today_earned = sum(p.amount for p in today_points if p.point_type == PointSource.EARN)
    today_spent = sum(abs(p.amount) for p in today_points if p.point_type == PointSource.DEDUCT)
    
    return {
        "balance": customer.points,
        "today_earned": today_earned,
        "today_spent": today_spent,
        "carbon_saved": float(customer.carbon_saved),
        "food_saved": float(customer.food_saved)
    }
