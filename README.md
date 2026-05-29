# 剩食猎人 - 后端服务

临期食品信息共享平台后端 API 服务。

## 技术栈

- **框架**: FastAPI + SQLAlchemy ORM
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **认证**: JWT Token
- **Python**: 3.11+

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/                # 核心模块
│   │   ├── config.py        # 全局配置
│   │   ├── database.py      # 数据库连接
│   │   ├── redis.py         # Redis 连接
│   │   └── security.py      # JWT 认证工具
│   ├── models/              # 数据模型 (25张表)
│   │   ├── __init__.py
│   │   ├── user.py          # 用户相关 (Customer, Merchant)
│   │   ├── food.py          # 食品相关 (Food, FoodType)
│   │   ├── shop.py          # 店铺相关 (Shop, ShopType)
│   │   ├── order.py         # 订单相关 (Order, OrderItem)
│   │   ├── scan.py          # 扫码记录 (UserScan)
│   │   ├── points.py        # 积分系统 (HunterPoint, PointRule)
│   │   ├── challenge.py     # 挑战系统 (Challenge, Badge)
│   │   ├── notification.py  # 通知系统
│   │   ├── recommendation.py # 推荐系统
│   │   ├── ai.py            # AI 识别
│   │   └── preference.py    # 用户偏好
│   ├── schemas/             # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── shop.py
│   │   ├── food.py
│   │   ├── order.py
│   │   ├── points.py
│   │   ├── challenge.py
│   │   └── response.py      # 统一响应格式
│   ├── api/                 # API 路由
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py          # 认证接口
│   │       │   ├── customers.py     # 客户接口
│   │       │   ├── merchants.py      # 商家接口
│   │       │   ├── shops.py         # 店铺接口
│   │       │   ├── foods.py         # 食品接口
│   │       │   ├── shop_foods.py    # 店铺食品接口
│   │       │   ├── orders.py        # 订单接口
│   │       │   ├── points.py        # 积分接口
│   │       │   ├── challenges.py    # 挑战接口
│   │       │   ├── recommendations.py # 推荐接口
│   │       │   ├── notifications.py # 通知接口
│   │       │   ├── upload.py        # 文件上传
│   │       │   └── ai.py            # AI 接口
│   │       └── router.py
│   └── services/            # 业务逻辑
│       ├── __init__.py
│       ├── auth_service.py
│       ├── order_service.py
│       ├── points_service.py
│       ├── challenge_service.py
│       └── ai_service.py
├── scripts/
│   ├── init_database.sql    # 数据库建表脚本
│   └── init_db.py           # Python 初始化脚本
├── requirements.txt
└── README.md
```

## 数据库表设计

### 用户体系
| 表名 | 说明 |
|------|------|
| customers | 客户信息 |
| merchants | 商家信息 |
| flavor_tags | 口味标签 |
| customer_flavor_preferences | 客户口味偏好 |
| customer_manual_preferences | 客户手动偏好设置 |

### 食品与店铺
| 表名 | 说明 |
|------|------|
| foods | 食品基础信息 |
| food_types | 食品类型 |
| shop_types | 店铺类型 |
| shops | 店铺信息 |
| shop_foods | 店铺食品关联 |
| food_flavor_tags | 食品口味标签 |

### 交易与行为
| 表名 | 说明 |
|------|------|
| orders | 订单 |
| order_items | 订单项 |
| user_scans | 用户扫码记录 |
| scan_images | 扫码图片 |
| customer_food_behaviors | 客户食品行为 |
| customer_category_preferences | 客户分类偏好 |

### 积分系统
| 表名 | 说明 |
|------|------|
| hunter_points | 猎人积分 |
| point_rules | 积分规则 |
| point_transactions | 积分变动记录 |

### 挑战系统
| 表名 | 说明 |
|------|------|
| challenges | 挑战活动 |
| user_challenges | 用户挑战进度 |
| badges | 徽章 |
| user_badges | 用户徽章 |

### 其他
| 表名 | 说明 |
|------|------|
| notifications | 通知 |
| food_recommendations | 食品推荐 |
| recommendation_feedback | 推荐反馈 |
| shelf_analysis | 保质期分析记录 |
| ai_audit_records | AI 审核记录 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

修改 `app/core/config.py` 中的数据库连接配置：

```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "food_saver_hunter"
```

### 3. 初始化数据库

```bash
mysql -u root -p < scripts/init_database.sql
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. API 文档

启动后访问: http://localhost:8000/docs

## API 路由

| 前缀 | 说明 |
|------|------|
| `/api/v1/auth` | 认证相关 |
| `/api/v1/customers` | 客户相关 |
| `/api/v1/merchants` | 商家相关 |
| `/api/v1/shops` | 店铺相关 |
| `/api/v1/foods` | 食品相关 |
| `/api/v1/shop-foods` | 店铺食品 |
| `/api/v1/orders` | 订单相关 |
| `/api/v1/points` | 积分相关 |
| `/api/v1/challenges` | 挑战相关 |
| `/api/v1/recommendations` | 推荐相关 |
| `/api/v1/notifications` | 通知相关 |
| `/api/v1/upload` | 文件上传 |
| `/api/v1/ai` | AI 接口 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MYSQL_HOST` | 数据库地址 | localhost |
| `MYSQL_PORT` | 数据库端口 | 3306 |
| `MYSQL_USER` | 数据库用户 | root |
| `MYSQL_PASSWORD` | 数据库密码 | - |
| `MYSQL_DATABASE` | 数据库名 | food_saver_hunter |
| `REDIS_HOST` | Redis 地址 | localhost |
| `REDIS_PORT` | Redis 端口 | 6379 |
| `SECRET_KEY` | JWT 密钥 | - |
| `ALGORITHM` | JWT 算法 | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间 | 1440 |
