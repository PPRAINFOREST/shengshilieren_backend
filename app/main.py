# FastAPI 应用入口
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.redis import init_redis, close_redis

# 创建应用
app = FastAPI(
    title="剩食猎人 API",
    description="临期食品信息共享与互助平台后端服务",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 启动事件
@app.on_event("startup")
async def startup_event():
    """服务启动时的初始化"""
    # 初始化 Redis (可选，失败不影响服务)
    try:
        await init_redis()
    except Exception as e:
        print(f"Redis 连接失败，服务将以无缓存模式运行: {e}")
    # 这里可以添加其他初始化操作


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时的清理"""
    await close_redis()
    engine.dispose()


# 注册 API 路由
app.include_router(
    api_router,
    prefix="/api/v1",
)


# 健康检查接口
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return {
        "message": "剩食猎人 API",
        "docs": "/docs",
        "version": "1.0.0"
    }
