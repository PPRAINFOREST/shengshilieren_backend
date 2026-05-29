"""
挑战服务 - 挑战参与和完成检查
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.challenge import Challenge, UserChallenge, Badge, UserBadge, ChallengeStatus
from app.models.user import Customer
from app.services.points_service import add_points


def join_challenge(db: Session, customer_id: int, challenge_id: int) -> UserChallenge:
    """
    参与挑战
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        challenge_id: 挑战ID
    
    Returns:
        UserChallenge: 用户挑战记录
    """
    # 检查挑战是否存在且在进行中
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise ValueError("挑战不存在")
    
    if challenge.status != ChallengeStatus.ACTIVE.value:
        raise ValueError("挑战已结束")
    
    # 检查是否已参与
    existing = db.query(UserChallenge).filter(
        UserChallenge.customer_id == customer_id,
        UserChallenge.challenge_id == challenge_id
    ).first()
    
    if existing:
        raise ValueError("已经参与过此挑战")
    
    # 创建参与记录
    user_challenge = UserChallenge(
        challenge_id=challenge_id,
        customer_id=customer_id,
        current=0
    )
    db.add(user_challenge)
    db.commit()
    db.refresh(user_challenge)
    
    return user_challenge


def update_challenge_progress(
    db: Session,
    customer_id: int,
    challenge_type: str,
    increment: int
) -> Optional[UserChallenge]:
    """
    更新挑战进度
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        challenge_type: 挑战类型
        increment: 增量值
    
    Returns:
        完成的挑战列表
    """
    # 获取用户进行中的挑战
    user_challenges = db.query(UserChallenge).join(Challenge).filter(
        UserChallenge.customer_id == customer_id,
        Challenge.challenge_type == challenge_type,
        UserChallenge.completed_at.is_(None)
    ).all()
    
    completed_challenges = []
    
    for uc in user_challenges:
        uc.current += increment
        
        # 检查是否完成
        if uc.current >= uc.challenge.target:
            completed = check_challenge_completion(db, uc)
            if completed:
                completed_challenges.append(completed)
    
    db.commit()
    return completed_challenges


def check_challenge_completion(
    db: Session,
    user_challenge: UserChallenge
) -> Optional[UserChallenge]:
    """
    检查并处理挑战完成
    
    Args:
        db: 数据库会话
        user_challenge: 用户挑战记录
    
    Returns:
        完成后的用户挑战记录
    """
    if user_challenge.current >= user_challenge.challenge.target:
        user_challenge.completed_at = datetime.now()
        
        # 发放积分奖励
        challenge = user_challenge.challenge
        add_points(
            db=db,
            customer_id=user_challenge.customer_id,
            amount=challenge.reward_points,
            source="challenge",
            source_id=challenge.id,
            description=f"完成挑战: {challenge.name}"
        )
        
        # 发放徽章
        if challenge.badge_id:
            grant_badge(db, user_challenge.customer_id, challenge.badge_id)
        
        db.commit()
        db.refresh(user_challenge)
        
        return user_challenge
    
    return None


def grant_badge(db: Session, customer_id: int, badge_id: int) -> UserBadge:
    """
    授予徽章
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        badge_id: 徽章ID
    
    Returns:
        UserBadge: 用户徽章记录
    """
    # 检查是否已有此徽章
    existing = db.query(UserBadge).filter(
        UserBadge.customer_id == customer_id,
        UserBadge.badge_id == badge_id
    ).first()
    
    if existing:
        return existing
    
    # 授予徽章
    user_badge = UserBadge(
        customer_id=customer_id,
        badge_id=badge_id
    )
    db.add(user_badge)
    db.commit()
    db.refresh(user_badge)
    
    return user_badge


def get_challenge_list(
    db: Session,
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> tuple[List[dict], int]:
    """
    获取挑战列表
    
    Args:
        db: 数据库会话
        customer_id: 客户ID（可选，用于标记已参与的挑战）
        status: 状态过滤
        page: 页码
        page_size: 每页数量
    
    Returns:
        (挑战列表, 总数)
    """
    query = db.query(Challenge)
    
    if status:
        query = query.filter(Challenge.status == status)
    
    total = query.count()
    challenges = query.order_by(desc(Challenge.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    # 获取用户参与的挑战
    joined_ids = set()
    if customer_id:
        joined = db.query(UserChallenge.challenge_id).filter(
            UserChallenge.customer_id == customer_id
        ).all()
        joined_ids = {j[0] for j in joined}
    
    result = []
    for c in challenges:
        item = {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "challenge_type": c.challenge_type,
            "target": c.target,
            "unit": c.unit,
            "reward_points": c.reward_points,
            "status": c.status,
            "start_date": c.start_date,
            "end_date": c.end_date,
            "is_joined": c.id in joined_ids
        }
        result.append(item)
    
    return result, total


def get_user_challenges(
    db: Session,
    customer_id: int,
    status: Optional[str] = None
) -> List[dict]:
    """
    获取用户的挑战列表
    
    Args:
        db: 数据库会话
        customer_id: 客户ID
        status: 状态过滤 (active/completed)
    
    Returns:
        用户挑战列表
    """
    query = db.query(UserChallenge).filter(UserChallenge.customer_id == customer_id)
    
    if status == "active":
        query = query.filter(UserChallenge.completed_at.is_(None))
    elif status == "completed":
        query = query.filter(UserChallenge.completed_at.isnot(None))
    
    user_challenges = query.all()
    
    result = []
    for uc in user_challenges:
        c = uc.challenge
        result.append({
            "id": uc.id,
            "challenge_id": c.id,
            "name": c.name,
            "description": c.description,
            "challenge_type": c.challenge_type,
            "target": c.target,
            "unit": c.unit,
            "reward_points": c.reward_points,
            "current": uc.current,
            "progress": min(100, int(uc.current / c.target * 100)) if c.target > 0 else 0,
            "started_at": uc.started_at,
            "completed_at": uc.completed_at,
            "is_completed": uc.completed_at is not None
        })
    
    return result
