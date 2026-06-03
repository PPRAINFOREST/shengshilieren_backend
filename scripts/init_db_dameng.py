#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
达梦数据库初始化脚本
用于初始化剩食猎人项目的达梦数据库
"""

import os
import sys
import datetime
from hashlib import sha256

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, Date, Index, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from passlib.context import CryptContext
from app.core.config import settings

Base = declarative_base()

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """密码哈希"""
    return pwd_context.hash(password)


# ============ 表模型定义 ============

class Merchant(Base):
    """商家表"""
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    store_name = Column(String(100), nullable=False)
    store_type_id = Column(Integer)
    address = Column(String(255))
    latitude = Column(Integer)
    longitude = Column(Integer)
    verified = Column(Integer, default=0)  # 达梦兼容：0/1 代替布尔
    verification_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)


class ShopType(Base):
    """店铺类型表"""
    __tablename__ = "shop_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))
    icon = Column(String(50))
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)


class Shop(Base):
    """店铺表"""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    shop_type_id = Column(Integer, ForeignKey("shop_types.id"), nullable=False)
    name = Column(String(100), nullable=False)  # 店铺名称
    address = Column(String(255))
    latitude = Column(Integer)
    longitude = Column(Integer)
    contact_phone = Column(String(20))
    business_hours = Column(String(100))
    description = Column(String(500))
    is_active = Column(Integer, default=1)  # 达梦兼容：0/1 代替布尔
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)


class FoodType(Base):
    """食品类型表"""
    __tablename__ = "food_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(50))
    color = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.now)


class Food(Base):
    """食品表"""
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    food_type_id = Column(Integer, ForeignKey("food_types.id"), nullable=False)
    name = Column(String(100), nullable=False)
    original_price = Column(Integer, nullable=False)  # 价格单位：分
    discount_price = Column(Integer)
    discount_rate = Column(Integer, default=0)
    original_expiry_date = Column(DateTime)
    discount_expiry_date = Column(DateTime)
    stock = Column(Integer, default=0)
    unit = Column(String(20), default="件")
    image_url = Column(String(500))
    description = Column(String(500))
    tags = Column(String(255))
    is_active = Column(Integer, default=1)  # 达梦兼容
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)


class Customer(Base):
    """客户表"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50))
    avatar_url = Column(String(500))
    points = Column(Integer, default=0)
    carbon_saved = Column(Integer, default=0)  # 单位：克
    food_saved = Column(Integer, default=0)   # 单位：克
    level = Column(String(20), default="bronze")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)


class PointRule(Base):
    """积分规则表"""
    __tablename__ = "point_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_type = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False)
    description = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)


class WasteReport(Base):
    """食品浪费报告表"""
    __tablename__ = "waste_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    food_type_id = Column(Integer, ForeignKey("food_types.id"))
    food_name = Column(String(100))
    quantity = Column(Integer, default=0)
    unit = Column(String(20))
    waste_type = Column(String(20))  # expired/damaged/unsold
    photo_url = Column(String(500))
    description = Column(String(500))
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)


class FavoriteMerchant(Base):
    """商家收藏表"""
    __tablename__ = "favorite_merchants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class UserAchievement(Base):
    """用户成就表"""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    achievement_type = Column(String(50), nullable=False)
    achievement_name = Column(String(100))
    description = Column(String(255))
    earned_at = Column(DateTime, default=datetime.datetime.now)


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), index=True)
    title = Column(String(100))
    content = Column(String(500))
    notification_type = Column(String(50))
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now)


class VerificationClaim(Base):
    """核销claim表"""
    __tablename__ = "verification_claims"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_code = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending/used/expired/cancelled
    created_at = Column(DateTime, default=datetime.datetime.now)
    used_at = Column(DateTime)
    expires_at = Column(DateTime)


def drop_all_tables(engine):
    """删除所有表 - 简化为空函数"""
    # 达梦表删除通过外部 disql 命令执行
    print("✓ 跳过删除旧表（需要手动删除或重建数据库）")


def reset_sequences(engine):
    """重置所有序列"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # 删除并重建常用序列
        sequences = [
            "MERCHANTS_SEQ",
            "SHOP_TYPES_SEQ", 
            "SHOPS_SEQ",
            "FOOD_TYPES_SEQ",
            "FOODS_SEQ",
            "CUSTOMERS_SEQ",
            "POINT_RULES_SEQ",
            "WASTE_REPORTS_SEQ",
            "FAVORITE_MERCHANTS_SEQ",
            "USER_ACHIEVEMENTS_SEQ",
            "NOTIFICATIONS_SEQ",
            "VERIFICATION_CLAIMS_SEQ",
        ]
        
        for seq in sequences:
            try:
                conn.execute(text(f'DROP SEQUENCE "{seq}" CASCADE'))
            except:
                pass
        
        for seq in sequences:
            try:
                conn.execute(text(f'CREATE SEQUENCE "{seq}" START WITH 1 INCREMENT BY 1 NOMAXVALUE NOCYCLE'))
            except:
                pass
        
        conn.commit()
    
    print("✓ 序列已重置")


def init_database(engine):
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成")


def insert_sample_data(engine):
    """插入示例数据"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("正在插入示例数据...")
        
        # ========== 店铺类型 ==========
        shop_types = [
            ShopType(name="便利店", description="24小时便利店", icon="store", sort_order=0),
            ShopType(name="超市", description="大型超市", icon="supermarket", sort_order=1),
            ShopType(name="面包店", description="烘焙面包店", icon="bakery", sort_order=2),
            ShopType(name="水果店", description="新鲜水果店", icon="fruit", sort_order=3),
            ShopType(name="奶茶店", description="饮品店", icon="tea", sort_order=4),
        ]
        db.add_all(shop_types)
        db.flush()
        print(f"✓ 插入 {len(shop_types)} 条店铺类型")
        
        # ========== 食品类型 ==========
        food_types = [
            FoodType(name="面包", icon="bread", color="#FFE4B5"),
            FoodType(name="乳制品", icon="milk", color="#87CEEB"),
            FoodType(name="蔬菜", icon="vegetable", color="#90EE90"),
            FoodType(name="水果", icon="fruit", color="#FFB6C1"),
            FoodType(name="肉类", icon="meat", color="#F5DEB3"),
            FoodType(name="饮料", icon="beverage", color="#E6E6FA"),
            FoodType(name="零食", icon="snack", color="#FFDAB9"),
            FoodType(name="熟食", icon="cooked", color="#DDA0DD"),
        ]
        db.add_all(food_types)
        db.flush()
        print(f"✓ 插入 {len(food_types)} 条食品类型")
        
        # ========== 积分规则 ==========
        point_rules = [
            PointRule(rule_type="scan", rule_name="扫码发现", points=30, description="上传未标注的临期食品"),
            PointRule(rule_type="purchase", rule_name="购买商品", points=10, description="每购买一次商品"),
            PointRule(rule_type="challenge_complete", rule_name="完成挑战", points=100, description="完成一个环保挑战"),
            PointRule(rule_type="audit_approved", rule_name="审核通过", points=20, description="扫码记录审核通过"),
            PointRule(rule_type="share", rule_name="分享商品", points=5, description="分享商品给好友"),
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
            verified=1,
        )
        db.add(merchant)
        db.flush()
        print(f"✓ 插入测试商家 (ID: {merchant.id})")
        
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
            is_active=1,
        )
        db.add(shop)
        db.flush()
        print(f"✓ 插入测试店铺 (ID: {shop.id})")
        
        # ========== 测试食品 ==========
        foods = [
            Food(
                shop_id=shop.id,
                food_type_id=1,
                name="原味法式面包",
                original_price=1500,
                discount_price=750,
                discount_rate=50,
                original_expiry_date=datetime.datetime.now(),
                discount_expiry_date=datetime.datetime.now(),
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
                original_expiry_date=datetime.datetime.now(),
                discount_expiry_date=datetime.datetime.now(),
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
                original_expiry_date=datetime.datetime.now(),
                discount_expiry_date=datetime.datetime.now(),
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
        print(f"✓ 插入测试客户 (ID: {customer.id})")
        
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
    
    # 创建引擎
    engine = create_engine(
        settings.DATABASE_URL_COMPUTED,
        pool_pre_ping=True,
        poolclass=NullPool,
        echo=False,
    )
    
    # 删除旧表
    drop_all_tables(engine)
    
    # 重置序列
    reset_sequences(engine)
    
    # 创建新表
    init_database(engine)
    
    # 插入示例数据
    insert_sample_data(engine)
    
    print("\n✅ 达梦数据库初始化完成！")
    print("\n测试账号:")
    print("  商家: 13800138001 / 123456")
    print("  客户: 13900139001 / 123456")


if __name__ == "__main__":
    main()
