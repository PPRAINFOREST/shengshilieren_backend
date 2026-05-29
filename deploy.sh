#!/bin/bash
# 剩食猎人后端部署脚本

set -e

echo "=========================================="
echo "  剩食猎人后端部署脚本"
echo "=========================================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件修改密码"
fi

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p uploads logs

# 选择 docker-compose 命令
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 解析命令参数
COMMAND=${1:-start}

case $COMMAND in
    start)
        echo "🚀 启动服务..."
        $DOCKER_COMPOSE up -d --build
        echo ""
        echo "✅ 服务启动成功！"
        echo ""
        echo "=========================================="
        echo "  服务地址"
        echo "=========================================="
        echo "  后端 API:     http://localhost:8000"
        echo "  API 文档:     http://localhost:8000/docs"
        echo "  phpMyAdmin:   http://localhost:8080"
        echo "  Redis UI:     http://localhost:8081"
        echo "=========================================="
        ;;
    stop)
        echo "🛑 停止服务..."
        $DOCKER_COMPOSE down
        echo "✅ 服务已停止"
        ;;
    restart)
        echo "🔄 重启服务..."
        $DOCKER_COMPOSE restart
        echo "✅ 服务已重启"
        ;;
    logs)
        echo "📋 查看日志..."
        $DOCKER_COMPOSE logs -f
        ;;
    status)
        echo "📊 服务状态..."
        $DOCKER_COMPOSE ps
        ;;
    clean)
        echo "🧹 清理服务和数据..."
        read -p "⚠️  这将删除所有数据，是否继续？(y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            $DOCKER_COMPOSE down -v
            rm -rf uploads/* logs/*
            echo "✅ 已清理"
        else
            echo "已取消"
        fi
        ;;
    init-db)
        echo "📊 初始化数据库..."
        $DOCKER_COMPOSE exec -T mysql mysql -uroot -p${MYSQL_ROOT_PASSWORD:-root123456} food_saver_hunter < scripts/init_database.sql
        echo "✅ 数据库初始化完成"
        ;;
    rebuild)
        echo "🔨 重新构建镜像..."
        $DOCKER_COMPOSE build --no-cache
        echo "✅ 镜像构建完成"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|logs|status|clean|init-db|rebuild}"
        echo ""
        echo "  start    - 启动服务"
        echo "  stop     - 停止服务"
        echo "  restart  - 重启服务"
        echo "  logs     - 查看日志"
        echo "  status   - 查看状态"
        echo "  clean    - 清理服务和数据"
        echo "  init-db  - 初始化数据库"
        echo "  rebuild  - 重新构建镜像"
        exit 1
        ;;
esac
