"""
Recommendations API - 推荐相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.recommendation import FoodRecommendation, RecommendationFeedback
from app.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/foods")
async def get_personalized_recommendations(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取个性化推荐"""
    # 获取推荐列表
    recommendations = db.query(FoodRecommendation).filter(
        FoodRecommendation.customer_id == current_user["id"],
        FoodRecommendation.is_shown == True
    ).order_by(desc(FoodRecommendation.recommendation_score)).limit(limit).all()
    
    return success_response(data=[{
        "id": r.id,
        "shop_food_id": r.shop_food_id,
        "score": float(r.recommendation_score) if r.recommendation_score else 0,
        "reason": r.reason,
        "scenario": r.scenario
    } for r in recommendations])


@router.post("/feedback")
async def submit_feedback(
    shop_food_id: int,
    feedback_type: str = Query(..., pattern="^(click|purchase|ignore|hide)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """提交推荐反馈"""
    feedback = RecommendationFeedback(
        customer_id=current_user["id"],
        shop_food_id=shop_food_id,
        feedback_type=feedback_type
    )
    db.add(feedback)
    db.commit()
    
    return success_response(message="反馈已记录")


@router.get("/preferences")
async def get_preferences(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取用户偏好设置"""
    from app.models.preference import CustomerPreference
    
    prefs = db.query(CustomerPreference).filter(
        CustomerPreference.customer_id == current_user["id"]
    ).all()
    
    return success_response(data=[{
        "id": p.id,
        "category": p.category,
        "preference_score": float(p.preference_score) if p.preference_score else 0
    } for p in prefs])
