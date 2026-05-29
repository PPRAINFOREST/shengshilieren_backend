"""
Challenges API - 挑战相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.challenge import Challenge, UserChallenge, Badge, UserBadge, ChallengeStatus
from app.models.user import Customer
from app.schemas.response import success_response, error_response
from app.services.challenge_service import join_challenge, check_challenge_completion

router = APIRouter()


@router.get("", response_model=dict)
def get_challenges(
    status: Optional[str] = Query(None, description="挑战状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取挑战列表"""
    query = db.query(Challenge)
    
    if status:
        query = query.filter(Challenge.status == status)
    else:
        query = query.filter(Challenge.status == ChallengeStatus.ACTIVE)
    
    total = query.count()
    challenges = query.order_by(desc(Challenge.start_date)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "challenges": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "target": c.target,
                    "unit": c.unit,
                    "reward_points": c.reward_points,
                    "start_date": c.start_date.isoformat() if c.start_date else None,
                    "end_date": c.end_date.isoformat() if c.end_date else None,
                    "status": c.status
                }
                for c in challenges
            ]
        }
    )


@router.get("/my", response_model=dict)
def get_my_challenges(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取我参与的挑战"""
    if current_user["type"] != "customer":
        return error_response("只有客户才能参与挑战")
    
    customer = current_user["user"]
    
    query = db.query(UserChallenge).filter(
        UserChallenge.customer_id == customer.id
    )
    
    if status:
        query = query.filter(UserChallenge.status == status)
    
    participations = query.all()
    
    result = []
    for p in participations:
        challenge = db.query(Challenge).filter(
            Challenge.id == p.challenge_id
        ).first()
        
        if challenge:
            result.append({
                "id": p.id,
                "challenge_id": challenge.id,
                "name": challenge.name,
                "description": challenge.description,
                "target": challenge.target,
                "current": p.current,
                "unit": challenge.unit,
                "progress": round(p.current / challenge.target * 100, 1) if challenge.target else 0,
                "reward_points": challenge.reward_points,
                "started_at": p.started_at.isoformat() if p.started_at else None,
                "completed_at": p.completed_at.isoformat() if p.completed_at else None,
                "status": p.status
            })
    
    return success_response(data=result)


@router.post("/{challenge_id}/join", response_model=dict)
def join_challenge_api(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """参与挑战"""
    if current_user["type"] != "customer":
        return error_response("只有客户才能参与挑战")
    
    customer = current_user["user"]
    
    # 检查挑战是否存在
    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id
    ).first()
    
    if not challenge:
        return error_response("挑战不存在")
    
    if challenge.status != ChallengeStatus.ACTIVE:
        return error_response("挑战已结束")
    
    # 检查是否已参与
    existing = db.query(UserChallenge).filter(
        UserChallenge.challenge_id == challenge_id,
        UserChallenge.customer_id == customer.id
    ).first()
    
    if existing:
        return error_response("您已参与此挑战")
    
    # 加入挑战
    result = join_challenge(db, customer.id, challenge_id)
    
    return success_response(
        data=result,
        msg="参与成功"
    )


@router.get("/badges", response_model=dict)
def get_badges(db: Session = Depends(get_db)):
    """获取所有成就徽章"""
    badges = db.query(Badge).all()
    
    return success_response(
        data=[
            {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "reward_points": b.reward_points,
                "unlock_condition": b.unlock_condition
            }
            for b in badges
        ]
    )


@router.get("/my/badges", response_model=dict)
def get_my_badges(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取我的徽章"""
    if current_user["type"] != "customer":
        return error_response("只有客户才能查看徽章")
    
    customer = current_user["user"]
    
    # 获取已解锁的徽章
    user_badges = db.query(UserBadge).filter(
        UserBadge.customer_id == customer.id
    ).all()
    
    unlocked = []
    for ub in user_badges:
        badge = db.query(Badge).filter(Badge.id == ub.badge_id).first()
        if badge:
            unlocked.append({
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "reward_points": badge.reward_points,
                "unlocked_at": ub.unlocked_at.isoformat() if ub.unlocked_at else None
            })
    
    # 获取所有徽章
    all_badges = db.query(Badge).all()
    
    # 标记已解锁
    unlocked_ids = {ub.badge_id for ub in user_badges}
    all_badges_data = []
    for b in all_badges:
        all_badges_data.append({
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "icon": b.icon,
            "reward_points": b.reward_points,
            "unlock_condition": b.unlock_condition,
            "is_unlocked": b.id in unlocked_ids
        })
    
    return success_response(
        data={
            "unlocked": unlocked,
            "total": len(all_badges_data),
            "all_badges": all_badges_data
        }
    )


@router.get("/leaderboard", response_model=dict)
def get_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取环保排行榜"""
    customers = db.query(Customer).order_by(
        desc(Customer.carbon_saved)
    ).limit(limit).all()
    
    return success_response(
        data=[
            {
                "rank": i + 1,
                "customer_id": c.id,
                "nickname": c.nickname,
                "avatar": c.avatar,
                "carbon_saved": c.carbon_saved,
                "food_saved": c.food_saved
            }
            for i, c in enumerate(customers)
        ]
    )
