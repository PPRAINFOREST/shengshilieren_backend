"""
Points API - 积分相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.services.points_service import get_point_history, get_point_balance
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/balance")
async def get_balance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取积分余额"""
    try:
        balance = get_point_balance(db, current_user["id"])
        return success_response(data=balance)
    except ValueError as e:
        return error_response(str(e))


@router.get("/history")
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    point_type: Optional[str] = Query(None, description="类型过滤"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取积分历史"""
    records, total = get_point_history(
        db, current_user["id"], page, page_size, point_type
    )
    
    return success_response(data={
        "records": [{
            "id": r.id,
            "point_type": r.point_type,
            "amount": r.amount,
            "source": r.source,
            "description": r.description,
            "balance_after": r.balance_after,
            "created_at": r.created_at.isoformat()
        } for r in records],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.get("/rules")
async def get_point_rules(db: Session = Depends(get_db)):
    """获取积分规则"""
    from app.models.points import PointRule
    
    rules = db.query(PointRule).filter(PointRule.is_active == True).all()
    
    return success_response(data=[{
        "id": r.id,
        "rule_type": r.rule_type,
        "rule_name": r.rule_name,
        "points": r.points,
        "daily_limit": r.daily_limit,
        "description": r.description
    } for r in rules])
