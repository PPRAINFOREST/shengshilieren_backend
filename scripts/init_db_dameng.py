"""
达梦数据库初始化脚本

使用方法：
    # 在 Mac 终端设置环境变量并运行
    cd ~/Desktop/harmony/backend
    
    # 方式1: 使用 docker exec
    docker exec -e DB_TYPE=dameng \
               -e DB_HOST=host.docker.internal \
               -e DB_PORT=5236 \
               -e DB_USER=FOODSAVER \
               -e DB_PASSWORD='Ywwhxxtwtyty121!' \
               -e DB_NAME=FOODSAVER \
               backend-backend \
               python scripts/init_db_dameng.py
               
    # 方式2: 进入 backend 容器后运行
    docker exec -it backend-backend bash
    DB_TYPE=dameng DB_HOST=host.docker.internal DB_PORT=5236 \
    DB_USER=FOODSAVER DB_PASSWORD='Ywwhxxtwtyty121!' DB_NAME=FOODSAVER \
    python scripts/init_db_dameng.py
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash

# 创建基类
Base = declarative_base()


class ShopType(Base):
    """店铺类型表"""
    __tablename__ = "shop_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class FoodType(Base):
    """食品类型表"""
    __tablename__ = "food_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(50))
    color = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)


class PointRule(Base):
    """积分规则表"""
    __tablename__ = "point_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_type = Column(String(50), unique=True, nullable=False)
    rule_name = Column(String(100), nullable=False)
    points = Column(Integer, nullable=False, default=0)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class Customer(Base):
    """客户用户表"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))
    points = Column(Integer, default=0)
    carbon_saved = Column(Integer, default=0)
    food_saved = Column(Integer, default=0)
    preferences = Column(String(500))
    hometown = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class Merchant(Base):
    """商家用户表"""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    store_name = Column(String(100), nullable=False)
    store_type_id = Column(Integer)
    address = Column(String(255))
    latitude = Column(Integer)
    longitude = Column(Integer)
    contact_phone = Column(String(20))
    business_hours = Column(String(100))
    business_license = Column(String(255))
    verified = Column(Boolean, default=False)
    rating = Column(Integer, default=500)
    total_orders = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class Shop(Base):
    """店铺表"""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, nullable=False, index=True)
    shop_type_id = Column(Integer)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    latitude = Column(Integer)
    longitude = Column(Integer)
    contact_phone = Column(String(20))
    business_hours = Column(String(100))
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class Food(Base):
    """食品表"""
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    shop_id = Column(Integer, nullable=False, index=True)
    food_type_id = Column(Integer)
    name = Column(String(100), nullable=False)
    original_price = Column(Integer)
    discount_price = Column(Integer)
    discount_rate = Column(Integer)
    original_expiry_date = Column(DateTime)
    discount_expiry_date = Column(DateTime)
    stock = Column(Integer, default=0)
    unit = Column(String(20), default="件")
    image_url = Column(String(500))
    description = Column(String(500))
    tags = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class FoodFlavorTag(Base):
    """食品口味标签表"""
    __tablename__ = "food_flavor_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)
    shop_id = Column(Integer, nullable=False)
    total_amount = Column(Integer, default=0)
    actual_amount = Column(Integer, default=0)
    points_discount = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    payment_method = Column(String(20))
    payment_time = Column(DateTime)
    pickup_code = Column(String(20))
    pickup_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class OrderItem(Base):
    """订单项表"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    food_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Integer)
    subtotal = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class UserScan(Base):
    """用户扫码记录表"""
    __tablename__ = "user_scans"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    shop_id = Column(Integer)
    food_name = Column(String(100))
    barcode = Column(String(100))
    original_expiry_date = Column(DateTime)
    image_url = Column(String(500))
    latitude = Column(Integer)
    longitude = Column(Integer)
    status = Column(String(20), default="pending")
    reject_reason = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)


class HunterPoint(Base):
    """用户积分记录表"""
    __tablename__ = "hunter_points"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    rule_id = Column(Integer)
    points = Column(Integer, nullable=False)
    balance = Column(Integer)
    source_type = Column(String(50))
    source_id = Column(String(50))
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)


class PointSource(Base):
    """积分来源表"""
    __tablename__ = "point_sources"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(50))
    points = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Challenge(Base):
    """挑战表"""
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    challenge_type = Column(String(50))
    target_value = Column(Integer)
    target_unit = Column(String(20))
    reward_points = Column(Integer, default=0)
    badge_id = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class UserChallenge(Base):
    """用户挑战表"""
    __tablename__ = "user_challenges"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    challenge_id = Column(Integer, nullable=False)
    current_value = Column(Integer, default=0)
    status = Column(String(20), default="ongoing")
    start_time = Column(DateTime)
    complete_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)


class Badge(Base):
    """徽章表"""
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(100))
    description = Column(String(255))
    level = Column(String(20))
    requirement = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class UserBadge(Base):
    """用户徽章表"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    badge_id = Column(Integer, nullable=False)
    earned_at = Column(DateTime, default=datetime.now)


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    merchant_id = Column(Integer, index=True)
    title = Column(String(100))
    content = Column(String(500))
    notification_type = Column(String(50))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class CustomerPreference(Base):
    """客户偏好表"""
    __tablename__ = "customer_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, unique=True, nullable=False, index=True)
    discount_threshold = Column(Integer, default=30)
    preferred_distance = Column(Integer, default=3000)
    notification_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)


class CustomerCategoryPreference(Base):
    """客户分类偏好表"""
    __tablename__ = "customer_category_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    food_type_id = Column(Integer, nullable=False, index=True)
    weight = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.now)


class CustomerManualPreference(Base):
    """客户手动偏好表"""
    __tablename__ = "customer_manual_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    preference_type = Column(String(20))
    preference_value = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


class FoodRecommendation(Base):
    """食品推荐表"""
    __tablename__ = "food_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    food_id = Column(Integer, nullable=False)
    score = Column(Integer)
    reason = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)


class RecommendationFeedback(Base):
    """推荐反馈表"""
    __tablename__ = "recommendation_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    feedback_type = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)


class CustomerFlavorPreference(Base):
    """客户口味偏好表"""
    __tablename__ = "customer_flavor_preferences"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    flavor_tag_id = Column(Integer, nullable=False, index=True)
    weight = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.now)


def init_database():
    """初始化数据库表"""
    # 创建引擎
    engine = create_engine(
        settings.DATABASE_URL_COMPUTED,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成！")
    
    return engine


def insert_sample_data():
    """插入示例数据"""
    engine = create_engine(
        settings.DATABASE_URL_COMPUTED,
        pool_pre_ping=True,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("正在插入示例数据...")
        
        # ========== 店铺类型 ==========
        shop_types = [
            ShopType(id=1, name="便利店", icon="store", description="24小时便利店"),
            ShopType(id=2, name="超市", icon="supermarket", description="大型超市"),
            ShopType(id=3, name="面包店", icon="bakery", description="烘焙面包店"),
            ShopType(id=4, name="水果店", icon="fruit", description="新鲜水果店"),
            ShopType(id=5, name="奶茶店", icon="tea", description="饮品店"),
        ]
        db.add_all(shop_types)
        db.flush()
        print(f"✓ 插入 {len(shop_types)} 条店铺类型")
        
        # ========== 食品类型 ==========
        food_types = [
            FoodType(id=1, name="面包", icon="bread", color="#FFE4B5"),
            FoodType(id=2, name="乳制品", icon="milk", color="#87CEEB"),
            FoodType(id=3, name="蔬菜", icon="vegetable", color="#90EE90"),
            FoodType(id=4, name="水果", icon="fruit", color="#FFB6C1"),
            FoodType(id=5, name="肉类", icon="meat", color="#F5DEB3"),
            FoodType(id=6, name="饮料", icon="beverage", color="#E6E6FA"),
            FoodType(id=7, name="零食", icon="snack", color="#FFDAB9"),
            FoodType(id=8, name="熟食", icon="cooked", color="#DDA0DD"),
        ]
        db.add_all(food_types)
        db.flush()
        print(f"✓ 插入 {len(food_types)} 条食品类型")
        
        # ========== 积分规则 ==========
        point_rules = [
            PointRule(id=1, rule_type="scan", rule_name="扫码发现", points=30, description="上传未标注的临期食品"),
            PointRule(id=2, rule_type="purchase", rule_name="购买商品", points=10, description="每购买一次商品"),
            PointRule(id=3, rule_type="challenge_complete", rule_name="完成挑战", points=100, description="完成一个环保挑战"),
            PointRule(id=4, rule_type="audit_approved", rule_name="审核通过", points=20, description="扫码记录审核通过"),
            PointRule(id=5, rule_type="share", rule_name="分享商品", points=5, description="分享商品给好友"),
        ]
        db.add_all(point_rules)
        db.flush()
        print(f"✓ 插入 {len(point_rules)} 条积分规则")
        
        # ========== 测试商家 ==========
        merchant = Merchant(
            phone="13800138001",
            password_hash=get_password_hash("123456"),
            store_name="健康生活便利店",
            store_type_id=1,
            address="北京市朝阳区建国路88号",
            latitude=398908,
            longitude=1163974,
            verified=True,
        )
        db.add(merchant)
        db.flush()
        print("✓ 插入测试商家")
        
        # ========== 测试店铺 ==========
        shop = Shop(
            merchant_id=merchant.id,
            shop_type_id=1,
            name="健康生活便利店-国贸店",
            address="北京市朝阳区建国路88号",
            latitude=398908,
            longitude=1163974,
            contact_phone="13800138001",
            business_hours="24小时",
            is_active=True,
        )
        db.add(shop)
        db.flush()
        print("✓ 插入测试店铺")
        
        # ========== 测试食品 ==========
        foods = [
            Food(
                shop_id=shop.id,
                food_type_id=1,
                name="原味法式面包",
                original_price=1500,
                discount_price=750,
                discount_rate=50,
                original_expiry_date=datetime.now(),
                discount_expiry_date=datetime.now(),
                stock=10,
                unit="个",
                tags="面包,烘焙",
            ),
            Food(
                shop_id=shop.id,
                food_type_id=2,
                name="新鲜纯牛奶",
                original_price=800,
                discount_price=400,
                discount_rate=50,
                original_expiry_date=datetime.now(),
                discount_expiry_date=datetime.now(),
                stock=20,
                unit="盒",
                tags="牛奶,乳制品",
            ),
            Food(
                shop_id=shop.id,
                food_type_id=6,
                name="柠檬茶饮料",
                original_price=600,
                discount_price=300,
                discount_rate=50,
                original_expiry_date=datetime.now(),
                discount_expiry_date=datetime.now(),
                stock=15,
                unit="瓶",
                tags="饮料,茶饮",
            ),
        ]
        db.add_all(foods)
        db.flush()
        print(f"✓ 插入 {len(foods)} 条测试食品")
        
        # ========== 测试客户 ==========
        customer = Customer(
            phone="13900139001",
            password_hash=get_password_hash("123456"),
            nickname="环保达人",
            points=500,
            carbon_saved=1000,
            food_saved=2000,
        )
        db.add(customer)
        db.flush()
        print("✓ 插入测试客户")
        
        # ========== 徽章 ==========
        badges = [
            Badge(id=1, name="新人入门", icon="badge_newbie", description="完成首次扫码", level="bronze"),
            Badge(id=2, name="环保先锋", icon="badge_pioneer", description="累计减碳1kg", level="silver"),
            Badge(id=3, name="剩食猎人", icon="badge_hunter", description="累计救粮5kg", level="gold"),
        ]
        db.add_all(badges)
        db.flush()
        print(f"✓ 插入 {len(badges)} 条徽章")
        
        # ========== 挑战 ==========
        challenges = [
            Challenge(
                id=1,
                title="一周环保挑战",
                description="一周内完成10次扫码",
                challenge_type="scan",
                target_value=10,
                target_unit="次",
                reward_points=100,
                badge_id=1,
                is_active=True,
            ),
            Challenge(
                id=2,
                title="减碳达人",
                description="累计减碳5kg",
                challenge_type="carbon",
                target_value=5000,
                target_unit="克",
                reward_points=200,
                badge_id=2,
                is_active=True,
            ),
        ]
        db.add_all(challenges)
        db.flush()
        print(f"✓ 插入 {len(challenges)} 条挑战")
        
        # ========== 客户偏好 ==========
        preference = CustomerPreference(
            customer_id=customer.id,
            discount_threshold=30,
            preferred_distance=3000,
            notification_enabled=True,
        )
        db.add(preference)
        print("✓ 插入客户偏好设置")
        
        db.commit()
        print("\n✅ 所有示例数据插入完成！")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 插入数据失败: {e}")
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 50)
    print("达梦数据库初始化脚本")
    print("=" * 50)
    print(f"数据库类型: {settings.DB_TYPE}")
    print(f"主机: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"数据库: {settings.DB_NAME}")
    print(f"用户: {settings.DB_USER}")
    print("=" * 50)
    
    # 创建表
    init_database()
    
    # 插入示例数据
    insert_sample_data()
    
    print("\n✅ 达梦数据库初始化完成！")


if __name__ == "__main__":
    main()
