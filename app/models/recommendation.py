"""
推荐系统相关模型
用于存储推荐结果和反馈
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, DECIMAL, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class FoodRecommendation(Base):
    """预计算推荐结果表"""
    __tablename__ = "food_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    shop_food_id = Column(Integer, nullable=False, index=True)
    
    # 推荐分
    recommendation_score = Column(DECIMAL(5, 3), comment="推荐分数")
    
    # 分项得分
    category_match_score = Column(DECIMAL(5, 3), default=0, comment="类型匹配分")
    distance_score = Column(DECIMAL(5, 3), default=0, comment="距离分")
    risk_score = Column(DECIMAL(5, 3), default=0, comment="风险适配分")
    discount_score = Column(DECIMAL(5, 3), default=0, comment="折扣分")
    
    # 推荐理由
    reason = Column(String(200), comment="推荐理由")
    
    # 推荐场景
    scenario = Column(String(20), default="personal", 
                    comment="场景: personal(个性化)/nearby(附近)/hot(热销)/new(新品)")
    
    # 状态
    is_shown = Column(Boolean, default=True, comment="是否展示")
    expires_at = Column(DateTime, comment="过期时间")
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 索引
    __table_args__ = (
        Index('idx_customer_score', 'customer_id', 'recommendation_score'),
        Index('idx_expires', 'expires_at'),
    )
    
    # 关联
    customer = relationship("Customer", back_populates="recommendations")

    def __repr__(self):
        return f"<FoodRecommendation customer={self.customer_id} shop_food={self.shop_food_id} score={self.recommendation_score}>"


class RecommendationFeedback(Base):
    """推荐反馈表"""
    __tablename__ = "recommendation_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    shop_food_id = Column(Integer, nullable=False, index=True)
    
    # 反馈类型
    feedback_type = Column(String(20), nullable=False,
                         comment="类型: click(点击)/purchase(购买)/ignore(忽略)/hide(隐藏)")
    
    # 推荐时的分数
    recommendation_score = Column(DECIMAL(5, 3), comment="推荐时的分数")
    
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<RecommendationFeedback {self.feedback_type}>"


class CustomerFlavorPreference(Base):
    """用户口味偏好表"""
    __tablename__ = "customer_flavor_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    flavor_tag = Column(String(20), nullable=False)
    
    # 偏好级别
    preference_level = Column(String(20), default="neutral",
                            comment="级别: like(喜欢)/neutral(中性)/dislike(厌恶)")
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 复合唯一索引
    __table_args__ = (
        Index('idx_customer_flavor', 'customer_id', 'flavor_tag', unique=True),
    )

    def __repr__(self):
        return f"<CustomerFlavorPreference customer={self.customer_id} {self.flavor_tag}={self.preference_level}>"
