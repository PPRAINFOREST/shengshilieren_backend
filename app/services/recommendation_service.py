"""
推荐服务 - 个性化推荐相关业务逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math

from app.models.recommendation import (
    CustomerFoodBehavior, BehaviorType, CustomerCategoryPreference,
    FoodRecommendation, RecommendationFeedback, FoodFlavorTag,
    CustomerFlavorPreference
)
from app.models.shop import ShopFood, Shop, FoodType
from app.models.food import Food
from app.models.user import Customer
from app.utils.location import calculate_distance


# 行为权重配置
BEHAVIOR_WEIGHTS = {
    BehaviorType.PURCHASE: 1.0,
    BehaviorType.FAVORITE: 0.8,
    BehaviorType.BROWSE: 0.3,
    BehaviorType.SCAN: 0.5,
    BehaviorType.REJECT: -0.5
}

# 推荐分数权重
SCORE_WEIGHTS = {
    "category_match": 0.50,   # 类型匹配分
    "distance": 0.20,         # 距离分
    "risk": 0.15,             # 风险适配分
    "discount": 0.15           # 折扣分
}


def record_behavior(
    db: Session,
    customer_id: int,
    food_id: int,
    behavior_type: BehaviorType,
    shop_food_id: Optional[int] = None,
    rating: Optional[int] = None
) -> CustomerFoodBehavior:
    """记录用户行为"""
    behavior = CustomerFoodBehavior(
        customer_id=customer_id,
        food_id=food_id,
        behavior_type=behavior_type,
        shop_food_id=shop_food_id,
        rating=rating
    )
    db.add(behavior)
    db.commit()
    db.refresh(behavior)
    return behavior


def calculate_preference_score(
    db: Session,
    customer_id: int
) -> Dict[int, float]:
    """
    计算用户对各食品类型的偏好分数
    
    返回: {food_type_id: score}
    """
    # 获取用户所有购买行为
    behaviors = db.query(CustomerFoodBehavior).filter(
        CustomerFoodBehavior.customer_id == customer_id,
        CustomerFoodBehavior.behavior_type.in_([
            BehaviorType.PURCHASE,
            BehaviorType.FAVORITE,
            BehaviorType.SCAN
        ])
    ).all()
    
    # 按食品类型聚合
    type_scores = {}
    for b in behaviors:
        food = db.query(Food).filter(Food.id == b.food_id).first()
        if not food:
            continue
        
        food_type_id = food.food_type_id
        weight = BEHAVIOR_WEIGHTS.get(b.behavior_type, 0)
        
        # 评分加权
        score = weight * 10
        if b.rating:
            score += b.rating * 2
        
        if food_type_id not in type_scores:
            type_scores[food_type_id] = []
        type_scores[food_type_id].append(score)
    
    # 计算每个类型的平均分
    preferences = {}
    for type_id, scores in type_scores.items():
        preferences[type_id] = sum(scores) / len(scores)
    
    # 归一化到 0-100
    if preferences:
        max_score = max(preferences.values())
        min_score = min(preferences.values())
        range_score = max_score - min_score if max_score != min_score else 1
        
        for type_id in preferences:
            preferences[type_id] = (
                (preferences[type_id] - min_score) / range_score * 100
            )
    
    return preferences


def generate_recommendations(
    db: Session,
    customer_id: int,
    lat: float,
    lng: float,
    limit: int = 20
) -> List[Dict]:
    """
    生成个性化推荐列表
    
    混合推荐算法：
    1. 用户偏好匹配
    2. 地理位置
    3. 风险适配
    4. 折扣力度
    """
    # 获取用户偏好
    preferences = calculate_preference_score(db, customer_id)
    
    # 获取用户手动偏好设置
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    # 获取所有在售商品
    shop_foods = db.query(ShopFood).filter(
        ShopFood.status == "active",
        ShopFood.quantity > 0,
        ShopFood.expiry_date > datetime.now()
    ).all()
    
    recommendations = []
    
    for sf in shop_foods:
        # 获取食品信息
        food = db.query(Food).filter(Food.id == sf.food_id).first()
        if not food:
            continue
        
        # 获取店铺信息
        shop = db.query(Shop).filter(Shop.id == sf.shop_id).first()
        if not shop or not shop.verified:
            continue
        
        # 计算距离
        distance = calculate_distance(lat, lng, shop.latitude, shop.longitude)
        if distance > 5:  # 超过5公里跳过
            continue
        
        # 1. 类型匹配分 (0-100)
        category_score = preferences.get(food.food_type_id, 30)
        
        # 2. 距离分 (0-100，越近越高)
        distance_score = max(0, 100 - distance * 20)
        
        # 3. 风险适配分
        # 如果用户没有设置风险偏好，默认中等
        risk_preference = getattr(customer, 'risk_preference', 'normal') if customer else 'normal'
        risk_map = {'safe': 0, 'medium': 50, 'high': 80, 'critical': 100}
        target_risk = risk_map.get(risk_preference, 50)
        
        risk_level_map = {'low': 20, 'medium': 50, 'high': 80, 'critical': 100}
        food_risk = risk_level_map.get(sf.risk_level, 50)
        risk_score = 100 - abs(target_risk - food_risk)
        
        # 4. 折扣分 (0-100，折扣越大越高)
        if sf.original_price > 0:
            discount_rate = (sf.original_price - sf.discount_price) / sf.original_price
            discount_score = discount_rate * 100
        else:
            discount_score = 50
        
        # 综合分数
        total_score = (
            category_score * SCORE_WEIGHTS["category_match"] +
            distance_score * SCORE_WEIGHTS["distance"] +
            risk_score * SCORE_WEIGHTS["risk"] +
            discount_score * SCORE_WEIGHTS["discount"]
        )
        
        # 生成推荐理由
        reasons = []
        if food.food_type_id in preferences and preferences[food.food_type_id] > 60:
            food_type = db.query(FoodType).filter(FoodType.id == food.food_type_id).first()
            if food_type:
                reasons.append(f"根据您偏好的{food_type.name}")
        if distance < 1:
            reasons.append("距离很近")
        if discount_rate > 0.5:
            reasons.append(f"限时折扣{int(discount_rate*100)}%")
        
        recommendations.append({
            "shop_food_id": sf.id,
            "food_name": food.name,
            "food_type_name": food.food_type.name if food.food_type else None,
            "food_type_color": food.food_type.color if food.food_type else None,
            "shop_name": shop.shop_name,
            "address": shop.address,
            "distance": round(distance, 2),
            "original_price": sf.original_price,
            "discount_price": sf.discount_price,
            "discount_rate": round(discount_rate * 100, 1),
            "risk_level": sf.risk_level,
            "expiry_date": sf.expiry_date.isoformat() if sf.expiry_date else None,
            "category_match_score": round(category_score, 1),
            "distance_score": round(distance_score, 1),
            "recommendation_score": round(total_score, 1),
            "reason": "，".join(reasons) if reasons else "为你推荐"
        })
    
    # 按推荐分数排序
    recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    
    return recommendations[:limit]


def get_cold_start_recommendations(
    db: Session,
    lat: float,
    lng: float,
    limit: int = 20
) -> List[Dict]:
    """
    冷启动推荐 - 新用户基于热门推荐
    """
    # 查询热门食品（基于订单量和评分）
    from app.models.order import Order
    
    hot_foods = db.query(
        ShopFood,
        func.count(Order.id).label("order_count"),
        func.avg(Order.total_price).label("avg_price")
    ).join(
        Order, Order.shop_food_id == ShopFood.id
    ).filter(
        ShopFood.status == "active",
        ShopFood.quantity > 0
    ).group_by(
        ShopFood.id
    ).order_by(
        desc("order_count")
    ).limit(100).all()
    
    recommendations = []
    
    for sf, order_count, avg_price in hot_foods:
        food = db.query(Food).filter(Food.id == sf.food_id).first()
        shop = db.query(Shop).filter(Shop.id == sf.shop_id).first()
        
        if not food or not shop or not shop.verified:
            continue
        
        distance = calculate_distance(lat, lng, shop.latitude, shop.longitude)
        if distance > 5:
            continue
        
        recommendations.append({
            "shop_food_id": sf.id,
            "food_name": food.name,
            "food_type_name": food.food_type.name if food.food_type else None,
            "shop_name": shop.shop_name,
            "distance": round(distance, 2),
            "discount_price": sf.discount_price,
            "popularity_score": order_count,
            "reason": "热门推荐"
        })
    
    # 按距离和热度综合排序
    recommendations.sort(key=lambda x: (x["distance"], -x["popularity_score"]))
    
    return recommendations[:limit]


def record_feedback(
    db: Session,
    customer_id: int,
    shop_food_id: int,
    feedback_type: str
) -> RecommendationFeedback:
    """记录用户对推荐的反馈"""
    feedback = RecommendationFeedback(
        customer_id=customer_id,
        shop_food_id=shop_food_id,
        feedback_type=feedback_type
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
