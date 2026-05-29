"""
用户偏好相关模型
用于存储用户的手动偏好设置和口味偏好
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, DECIMAL, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class CustomerPreference(Base):
    """用户手动偏好设置表"""
    __tablename__ = "customer_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # 喜欢的店铺类型（JSON数组）
    favorite_shop_types = Column(String(200), comment="喜欢的店铺类型ID列表")
    
    # 喜欢的食品类型（JSON数组）
    favorite_food_types = Column(String(200), comment="喜欢的食品类型ID列表")
    
    # 喜欢的口味（JSON数组）
    favorite_flavors = Column(String(200), comment="喜欢的口味标签")
    
    # 厌恶的食材（JSON数组）
    disliked_ingredients = Column(String(500), comment="厌恶的食材")
    
    # 价格偏好
    price_range_min = Column(DECIMAL(10, 2), comment="最低价格(元)")
    price_range_max = Column(DECIMAL(10, 2), comment="最高价格(元)")
    
    # 风险偏好
    risk_preference = Column(String(20), default="normal",
                           comment="风险偏好: safe/normal/adventurous")
    
    # 过敏原（JSON数组）
    allergens = Column(String(500), comment="过敏原")
    
    # 是否开启个性化推荐
    enable_recommendation = Column(Boolean, default=True)
    
    # 是否公开环保数据
    public_environment_data = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    customer = relationship("Customer", back_populates="preference")


class CustomerCategoryPreference(Base):
    """用户类别偏好表"""
    __tablename__ = "customer_category_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    food_type_id = Column(Integer, nullable=False, index=True)
    
    # 偏好分数
    preference_score = Column(DECIMAL(5, 3), default=0, comment="计算后的偏好分")
    
    # 行为统计
    purchase_count = Column(Integer, default=0, comment="购买次数")
    total_spend = Column(DECIMAL(10, 2), default=0, comment="总消费(元)")
    avg_rating = Column(DECIMAL(2, 1), default=5.0, comment="平均评分")
    
    # 口味标签（JSON数组）
    flavor_tags = Column(String(200), comment="口味标签列表")
    
    # 时间偏好（JSON数组）
    preferred_time_slots = Column(String(100), comment="偏好时间段")
    
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联
    customer = relationship("Customer", back_populates="category_preferences")

    def __repr__(self):
        return f"<CustomerCategoryPreference customer={self.customer_id} type={self.food_type_id} score={self.preference_score}>"


class CustomerManualPreference(Base):
    """用户手动偏好表"""
    __tablename__ = "customer_manual_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    
    # 喜欢的类型（JSON数组）
    favorite_types = Column(String(200), comment="喜欢的类型ID列表")
    
    # 喜欢的口味（JSON数组）
    favorite_flavors = Column(String(200), comment="喜欢的口味列表")
    
    # 厌恶的食材（JSON数组）
    disliked_ingredients = Column(String(500), comment="厌恶的食材列表")
    
    # 价格偏好
    price_range_min = Column(DECIMAL(10, 2), comment="最低价格(元)")
    price_range_max = Column(DECIMAL(10, 2), comment="最高价格(元)")
    
    # 风险偏好
    risk_preference = Column(String(20), default="normal",
                           comment="风险偏好: safe/normal/adventurous")
    
    # 过敏原（JSON数组）
    allergens = Column(String(500), comment="过敏原列表")
    
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<CustomerManualPreference customer={self.customer_id}>"
