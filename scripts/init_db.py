"""
初始化数据库脚本

使用方法：
    python scripts/init_db.py
"""
import sys
import os
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, SessionLocal
from app.models.user import Customer, Merchant
from app.models.shop import Shop, ShopType
from app.models.food import Food, FoodType, ShopFood
from app.models.order import Order
from app.models.scan import UserScan
from app.models.points import HunterPoint, PointSource, PointRule
from app.models.challenge import Challenge, UserChallenge, Badge, UserBadge
from app.models.notification import Notification
from app.models.preference import (
    CustomerPreference,
    CustomerCategoryPreference,
    CustomerManualPreference
)
from app.models.recommendation import (
    FoodRecommendation,
    RecommendationFeedback,
    CustomerFlavorPreference
)
from app.models.food import FoodFlavorTag
from app.core.security import get_password_hash


def init_database():
    """初始化数据库"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def insert_sample_data():
    """插入示例数据"""
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
            latitude=39.9088,
            longitude=116.3974,
            verified=True,
            rating=4.8
        )
        db.add(merchant)
        db.flush()
        print(f"✓ 插入商家: {merchant.store_name}")
        
        # ========== 测试店铺 ==========
        shop = Shop(
            merchant_id=merchant.id,
            shop_type_id=1,
            shop_name="健康生活便利店(国贸店)",
            address="北京市朝阳区建国路88号",
            latitude=39.9088,
            longitude=116.3974,
            verified=True,
            rating=4.8
        )
        db.add(shop)
        db.flush()
        print(f"✓ 插入店铺: {shop.shop_name}")
        
        # ========== 测试食品 ==========
        foods_data = [
            ("6901234567890", "全麦吐司面包", 1, "麦多面包坊", 500, 9.9),
            ("6901234567891", "鲜牛奶 250ml", 2, "伊利", 250, 6.5),
            ("6901234567892", "有机生菜 300g", 3, "田园牧歌", 300, 5.8),
            ("6901234567893", "新鲜草莓 200g", 4, "红颜草莓", 200, 12.8),
            ("6901234567894", "鸡胸肉 250g", 5, "正大食品", 250, 15.9),
        ]
        foods = []
        for barcode, name, type_id, brand, weight, price in foods_data:
            food = Food(
                barcode=barcode,
                name=name,
                food_type_id=type_id,
                brand=brand,
                default_weight=f"{weight}g"
            )
            db.add(food)
            foods.append(food)
        db.flush()
        print(f"✓ 插入 {len(foods)} 种食品")
        
        # ========== 店铺食品 ==========
        shop_foods = []
        for i, food in enumerate(foods):
            original_price = int(food.default_weight.replace("g", "")) * 0.02
            discount_price = original_price * 0.6  # 6折
            shop_food = ShopFood(
                shop_id=shop.id,
                food_id=food.id,
                shelf_position=f"A{1+i}-2",
                quantity=random.randint(5, 20),
                original_price=original_price,
                discount_price=discount_price,
                discount_type="clearance",
                expiry_date=datetime.now().date() + timedelta(days=random.randint(1, 5)),
                risk_level=random.choice(["low", "medium", "high"]),
                status="active"
            )
            db.add(shop_food)
            shop_foods.append(shop_food)
        db.flush()
        print(f"✓ 插入 {len(shop_foods)} 条店铺食品")
        
        # ========== 测试客户 ==========
        customer = Customer(
            phone="13900139001",
            password_hash=get_password_hash("123456"),
            nickname="环保达人",
            points=100,
            carbon_saved=5.5,
            food_saved=3.2
        )
        db.add(customer)
        db.flush()
        print(f"✓ 插入客户: {customer.nickname}")
        
        # ========== 挑战数据 ==========
        challenges = [
            Challenge(
                id=1,
                name="救粮新手",
                description="累计救粮1kg",
                challenge_type="food",
                target=1.0,
                unit="kg",
                reward_points=50,
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=30),
                status="active"
            ),
            Challenge(
                id=2,
                name="环保达人",
                description="累计减碳5kg",
                challenge_type="carbon",
                target=5.0,
                unit="kg",
                reward_points=200,
                start_date=datetime.now().date(),
                end_date=datetime.now().date() + timedelta(days=60),
                status="active"
            ),
        ]
        db.add_all(challenges)
        db.flush()
        print(f"✓ 插入 {len(challenges)} 个挑战")
        
        # ========== 徽章 ==========
        badges = [
            Badge(id=1, name="初次救粮", icon="badge_1", description="第一次购买临期食品", reward_points=10),
            Badge(id=2, name="环保新手", icon="badge_2", description="累计减碳1kg", reward_points=20),
            Badge(id=3, name="救粮达人", icon="badge_3", description="累计救粮10kg", reward_points=50),
        ]
        db.add_all(badges)
        db.flush()
        print(f"✓ 插入 {len(badges)} 个徽章")
        
        # ========== 测试订单 ==========
        order = Order(
            customer_id=customer.id,
            shop_food_id=shop_foods[0].id,
            quantity=2,
            total_price=float(shop_foods[0].discount_price) * 2,
            status="completed"
        )
        db.add(order)
        print(f"✓ 插入测试订单")
        
        db.commit()
        print("\n✅ 示例数据插入完成！")
        print(f"   测试商家: 13800138001 / 123456")
        print(f"   测试客户: 13900139001 / 123456")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 插入数据失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
    insert_sample_data()
