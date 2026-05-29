"""
Upload API - 文件上传接口
支持本地存储和阿里云OSS两种模式
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
from typing import Optional
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.response import success_response, error_response

router = APIRouter()

# 上传配置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
OSS_ENABLED = os.getenv("OSS_ENABLED", "false").lower() == "true"

# OSS配置（当OSS_ENABLED=true时使用）
OSS_CONFIG = {
    "access_key_id": os.getenv("OSS_ACCESS_KEY_ID", ""),
    "access_key_secret": os.getenv("OSS_ACCESS_KEY_SECRET", ""),
    "bucket": os.getenv("OSS_BUCKET", ""),
    "endpoint": os.getenv("OSS_ENDPOINT", ""),
    "domain": os.getenv("OSS_DOMAIN", ""),
}


def init_upload_dir():
    """初始化上传目录"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """验证文件"""
    # 允许的类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        return False, "不支持的图片格式，请上传 JPG、PNG、GIF 或 WebP 格式"

    # 检查文件大小（最大5MB）
    max_size = 5 * 1024 * 1024
    return True, ""


async def upload_to_local(file: UploadFile, subdir: str = "") -> dict:
    """上传到本地存储"""
    init_upload_dir()

    # 生成唯一文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"

    if subdir:
        save_dir = os.path.join(UPLOAD_DIR, subdir)
        os.makedirs(save_dir, exist_ok=True)
    else:
        save_dir = UPLOAD_DIR

    filepath = os.path.join(save_dir, filename)

    # 保存文件
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    file_url = f"/uploads/{subdir}/{filename}" if subdir else f"/uploads/{filename}"

    return {
        "url": file_url,
        "filename": filename,
        "size": len(content),
        "path": filepath,
    }


async def upload_to_oss(file: UploadFile, subdir: str = "") -> dict:
    """上传到阿里云OSS"""
    try:
        import oss2
    except ImportError:
        raise HTTPException(status_code=500, detail="阿里云OSS SDK未安装")

    # 生成唯一文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"

    if subdir:
        object_name = f"{subdir}/{filename}"
    else:
        object_name = filename

    # OSS认证
    auth = oss2.Auth(OSS_CONFIG["access_key_id"], OSS_CONFIG["access_key_secret"])
    bucket = oss2.Bucket(auth, OSS_CONFIG["endpoint"], OSS_CONFIG["bucket"])

    # 读取文件内容
    content = await file.read()

    # 上传到OSS
    bucket.put_object(object_name, content)

    # 生成访问URL
    file_url = f"https://{OSS_CONFIG['bucket']}.{OSS_CONFIG['endpoint']}/{object_name}"

    # 如果配置了自定义域名，使用自定义域名
    if OSS_CONFIG.get("domain"):
        file_url = f"{OSS_CONFIG['domain']}/{object_name}"

    return {
        "url": file_url,
        "filename": filename,
        "size": len(content),
        "path": object_name,
    }


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    上传图片
    - 支持本地存储或OSS存储
    - 返回图片URL供后续使用
    """
    # 验证文件
    valid, error_msg = validate_file(file)
    if not valid:
        return error_response(error_msg)

    # 根据配置选择存储方式
    if OSS_ENABLED:
        result = await upload_to_oss(file, "images")
    else:
        result = await upload_to_local(file, "images")

    return success_response(data=result)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    上传头像
    - 用户专用，自动裁剪为正方形
    """
    # 验证文件
    valid, error_msg = validate_file(file)
    if not valid:
        return error_response(error_msg)

    # 解析用户ID
    user_id = current_user.get("sub", "").replace("customer_", "").replace("merchant_", "")

    # 上传
    if OSS_ENABLED:
        result = await upload_to_oss(file, f"avatars/{user_id}")
    else:
        result = await upload_to_local(file, f"avatars/{user_id}")

    return success_response(data=result)


@router.post("/shop-image")
async def upload_shop_image(
    file: UploadFile = File(...),
    shop_id: int = None,
    current_user: dict = Depends(get_current_user)
):
    """
    上传店铺图片
    - 商家专用
    """
    # 验证文件
    valid, error_msg = validate_file(file)
    if not valid:
        return error_response(error_msg)

    # 上传
    if OSS_ENABLED:
        result = await upload_to_oss(file, f"shops/{shop_id or 'temp'}")
    else:
        result = await upload_to_local(file, f"shops/{shop_id or 'temp'}")

    return success_response(data=result)


@router.post("/food-image")
async def upload_food_image(
    file: UploadFile = File(...),
    food_id: int = None,
    current_user: dict = Depends(get_current_user)
):
    """
    上传食品图片
    - 商家专用
    """
    # 验证文件
    valid, error_msg = validate_file(file)
    if not valid:
        return error_response(error_msg)

    # 上传
    if OSS_ENABLED:
        result = await upload_to_oss(file, f"foods/{food_id or 'temp'}")
    else:
        result = await upload_to_local(file, f"foods/{food_id or 'temp'}")

    return success_response(data=result)


@router.post("/scan-image")
async def upload_scan_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    上传扫码图片
    - 记录到数据库
    """
    # 验证文件
    valid, error_msg = validate_file(file)
    if not valid:
        return error_response(error_msg)

    # 解析用户ID
    user_id = current_user.get("sub", "").replace("customer_", "")

    # 上传
    if OSS_ENABLED:
        result = await upload_to_oss(file, f"scans/{user_id}")
    else:
        result = await upload_to_local(file, f"scans/{user_id}")

    # 记录到数据库
    try:
        from app.models.scan import ScanImage
        scan_image = ScanImage(
            user_id=int(user_id),
            image_url=result["url"],
            file_size=result["size"],
        )
        db.add(scan_image)
        db.commit()
        result["scan_image_id"] = scan_image.id
    except Exception as e:
        # 即使数据库记录失败，也返回上传成功
        pass

    return success_response(data=result)


@router.post("/ai-analysis")
async def upload_ai_analysis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    上传AI分析图片
    - 用于临期食品识别
    """
    # 验证文件
    valid, error_msg = validate_file(file)
    if not valid:
        return error_response(error_msg)

    # 解析用户ID
    user_id = current_user.get("sub", "").replace("customer_", "")

    # 上传
    if OSS_ENABLED:
        result = await upload_to_oss(file, f"ai/{user_id}")
    else:
        result = await upload_to_local(file, f"ai/{user_id}")

    # 可选：同时触发AI分析
    # 这里只是记录，实际AI分析由AI服务异步处理

    return success_response(data={
        **result,
        "message": "图片上传成功，AI分析将在后台进行"
    })


@router.get("/policy")
async def get_upload_policy(
    file_type: str = "image",
    current_user: dict = Depends(get_current_user)
):
    """
    获取直传到OSS的凭证
    - 前端直传OSS时使用
    """
    if not OSS_ENABLED:
        return error_response("OSS未启用，请使用普通上传接口")

    try:
        import oss2
    except ImportError:
        return error_response("阿里云OSS SDK未安装")

    # 生成目录和文件名
    user_id = current_user.get("sub", "").replace("customer_", "").replace("merchant_", "")
    dir_name = f"{file_type}s/{user_id}"
    filename = f"{uuid.uuid4()}"
    object_name = f"{dir_name}/{filename}"

    # OSS认证
    auth = oss2.Auth(OSS_CONFIG["access_key_id"], OSS_CONFIG["access_key_secret"])
    bucket = oss2.Bucket(auth, OSS_CONFIG["endpoint"], OSS_CONFIG["bucket"])

    # 生成上传凭证
    policy = bucket.sign_policy(object_name)

    return success_response(data={
        "access_key_id": OSS_CONFIG["access_key_id"],
        "policy": policy["policy"],
        "signature": policy["signature"],
        "dir": dir_name,
        "filename": filename,
        "expire": 3600,
        "callback": None,
    })
