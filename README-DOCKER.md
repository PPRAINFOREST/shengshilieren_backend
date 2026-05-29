# 剩食猎人后端 - Docker 部署指南

## 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+（或 Docker Desktop）

### 2. 一键部署

```bash
# 进入后端目录
cd backend

# 启动服务
chmod +x deploy.sh
./deploy.sh start
```

### 3. 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| 后端 API | http://localhost:8000 | 主要 API 服务 |
| API 文档 | http://localhost:8000/docs | Swagger 文档 |
| phpMyAdmin | http://localhost:8080 | MySQL 管理界面 |
| Redis UI | http://localhost:8081 | Redis 管理界面 |

---

## 详细命令

### 启动服务

```bash
# 方式1：使用脚本
./deploy.sh start

# 方式2：直接使用 docker compose
docker compose up -d --build
```

### 停止服务

```bash
./deploy.sh stop
# 或
docker compose down
```

### 查看日志

```bash
./deploy.sh logs
# 或
docker compose logs -f backend
```

### 初始化数据库

```bash
./deploy.sh init-db
# 或
docker compose exec -T mysql mysql -uroot -p${MYSQL_ROOT_PASSWORD} food_saver_hunter < scripts/init_database.sql
```

---

## 配置说明

### 环境变量

复制 `.env.example` 为 `.env` 并修改：

```bash
cp .env.example .env
```

主要配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | root123456 |
| `SECRET_KEY` | JWT 密钥 | 请修改 |
| `OSS_ENABLED` | 是否启用 OSS | false |
| `REDIS_PASSWORD` | Redis 密码 | 空 |

### OSS 配置（可选）

如需使用阿里云 OSS：

1. 修改 `.env`：

```env
OSS_ENABLED=true
OSS_ACCESS_KEY_ID=你的AccessKey
OSS_ACCESS_KEY_SECRET=你的AccessKeySecret
OSS_BUCKET=你的Bucket名称
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
```

2. 上传文件将从本地存储切换到 OSS

---

## 服务架构

```
┌─────────────────────────────────────────────────────────┐
│                    Docker 网络                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐      ┌─────────────┐                   │
│  │   Backend   │ ──── │    MySQL    │                   │
│  │  (FastAPI)  │      │   (数据)    │                   │
│  │   :8000    │      │    :3306    │                   │
│  └─────────────┘      └─────────────┘                   │
│         │                      │                         │
│         │                      │                         │
│         ▼                      ▼                         │
│  ┌─────────────┐                                      │
│  │    Redis    │                                      │
│  │   (缓存)    │                                      │
│  │    :6379    │                                      │
│  └─────────────┘                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 数据持久化

数据存储在 Docker volumes 中：

| Volume | 说明 |
|--------|------|
| `mysql_data` | MySQL 数据文件 |
| `redis_data` | Redis 持久化文件 |

清理数据：

```bash
./deploy.sh clean
```

---

## 开发模式

如需修改代码后重新构建：

```bash
# 重新构建并启动
./deploy.sh rebuild

# 或仅重启后端
docker compose restart backend
```

---

## 常见问题

### Q: 端口被占用？

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 改为 8001
```

### Q: 数据库连接失败？

1. 检查 MySQL 是否健康：`docker compose ps`
2. 查看日志：`docker compose logs mysql`
3. 等待 MySQL 完全启动（约30秒）

### Q: Redis 连接失败？

Redis 依赖较少，通常启动后即可连接。如有问题：

```bash
docker compose logs redis
```

---

## 生产部署建议

⚠️ **以下内容仅适用于生产环境**

1. **修改默认密码**
   ```bash
   # 在 .env 中设置强密码
   MYSQL_ROOT_PASSWORD=your-strong-password
   SECRET_KEY=your-very-long-secret-key
   ```

2. **启用 HTTPS**
   - 使用 Nginx/Caddy 反向代理
   - 配置 SSL 证书

3. **限制端口访问**
   - 只开放 8000（API）和 80/443（Web）
   - phpMyAdmin 和 Redis UI 不对外暴露

4. **定期备份**
   ```bash
   # 备份 MySQL
   docker compose exec mysql mysqldump -uroot -p food_saver_hunter > backup.sql
   
   # 备份 Redis
   docker compose exec redis redis-cli SAVE
   ```

---

## 卸载

```bash
# 停止并删除容器
./deploy.sh stop

# 删除数据卷（可选）
docker volume rm backend_mysql_data backend_redis_data

# 删除镜像
docker rmi backend-backend
```
