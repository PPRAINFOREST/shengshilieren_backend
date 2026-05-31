# -*- coding: utf-8 -*-
"""
安全工具模块
包含密码加密、Token验证等功能
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
import hashlib
import secrets

from app.core.config import settings


def get_password_hash(password: str) -> str:
    """
    获取密码哈希值 (使用 PBKDF2-SHA256)
    """
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    """
    try:
        if '$' not in hashed_password:
            return False
        salt, stored_hash = hashed_password.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(hash_obj.hex(), stored_hash)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌

    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量

    Returns:
        str: JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码访问令牌

    Args:
        token: JWT token

    Returns:
        Optional[dict]: 解码后的数据，失败返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_verification_code(length: int = 6) -> str:
    """
    生成验证码

    Args:
        length: 验证码长度

    Returns:
        str: 验证码
    """
    import random

    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def generate_pickup_code(length: int = 6) -> str:
    """
    生成取货码

    Args:
        length: 取货码长度

    Returns:
        str: 取货码（大写字母和数字）
    """
    import random
    import string

    characters = string.ascii_uppercase + string.digits
    return "".join([random.choice(characters) for _ in range(length)])
