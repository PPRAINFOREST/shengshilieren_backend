# 剩食猎人 - 后端服务

临期食品信息共享平台后端 API 服务。

## 技术栈

- **框架**: FastAPI + SQLAlchemy ORM
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **认证**: JWT Token
- **部署**: Docker + Docker Compose

---

## 快速开始（Docker 部署）

### 前提条件

- [Docker](https://docs.docker.com/get-docker/) 已安装
- [Docker Compose](https://docs.docker.com/compose/install/) 已安装

### 启动服务（完整版）

```bash
# 启动所有服务（MySQL + Redis + 后端API）
docker-compose up -d --build

# 启动数据库管理工具（phpMyAdmin + Redis Commander）
docker-compose --profile tools up -d

# 初始化数据库（首次部署时）
docker-compose exec -e DATABASE_URL="mysql+pymysql://root:${MYSQL_ROOT_PASSWORD}@mysql:3306/food_saver_hunter" backend python scripts/init_db.py
```

> **说明**：phpMyAdmin 和 Redis Commander 使用 `profiles` 配置，默认不启动。如需管理数据库或缓存，需要单独运行上面的 `--profile tools` 命令。

### 访问服务

| 服务 | 地址 |
|------|------|
| API | http://localhost:8000 |
| Swagger 文档 | http://localhost:8000/docs |
| phpMyAdmin (数据库管理) | http://localhost:8082 |
| Redis Commander (缓存管理) | http://localhost:8081 |

---

## 配置说明

### 环境变量

编辑 `.env` 文件：

```bash
# 数据库
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=food_saver_hunter

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT 密钥（修改为随机字符串）
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务
API_HOST=0.0.0.0
API_PORT=8000

# 阿里云 OSS（可选，用于图片上传）
OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
OSS_BUCKET=
OSS_REGION=
```

---

## 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 进入后端容器
docker-compose exec backend bash

# 重新构建后端
docker-compose up -d --build backend
```

---

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core/                # 核心模块
│   │   ├── config.py       # 全局配置
│   │   ├── database.py     # 数据库连接
│   │   ├── redis.py        # Redis 连接
│   │   └── security.py     # JWT 认证工具
│   ├── models/              # 数据模型 (25张表)
│   ├── schemas/             # Pydantic 模型
│   ├── api/v1/endpoints/   # API 路由
│   └── services/            # 业务逻辑
├── scripts/
│   └── init_database.sql    # 数据库建表脚本
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

---

## API 路由

| 前缀 | 说明 |
|------|------|
| `/api/v1/auth` | 认证相关 |
| `/api/v1/customers` | 客户相关 |
| `/api/v1/merchants` | 商家相关 |
| `/api/v1/shops` | 店铺相关 |
| `/api/v1/foods` | 食品相关 |
| `/api/v1/orders` | 订单相关 |
| `/api/v1/points` | 积分相关 |
| `/api/v1/challenges` | 挑战相关 |
| `/api/v1/notifications` | 通知相关 |
| `/api/v1/upload` | 文件上传 |
| `/api/v1/health` | 健康检查 |

---

## 数据库表设计

### 用户体系
| 表名 | 说明 |
|------|------|
| customers | 客户信息 |
| merchants | 商家信息 |

### 食品与店铺
| 表名 | 说明 |
|------|------|
| foods | 食品基础信息 |
| shops | 店铺信息 |
| shop_foods | 店铺食品关联 |

### 交易与行为
| 表名 | 说明 |
|------|------|
| orders | 订单 |
| user_scans | 用户扫码记录 |

### 积分与挑战
| 表名 | 说明 |
|------|------|
| hunter_points | 猎人积分 |
| challenges | 挑战活动 |
| badges | 徽章 |

---

## 本地开发

如果需要本地修改代码：

```bash
# 修改代码后重新构建
docker-compose up -d --build backend

# 查看实时日志
docker-compose logs -f backend
```

---

## 更新代码

```bash
cd shengshilieren_backend
git pull origin main
docker-compose up -d --build backend
```
