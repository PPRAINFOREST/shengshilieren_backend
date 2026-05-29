"""
Pydantic schemas - 通用响应格式
"""
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel):
    """基础响应"""
    code: int = 200
    message: str = "success"


class DataResponse(ResponseBase, Generic[T]):
    """带数据的响应"""
    data: Optional[T] = None


class ListResponse(ResponseBase, Generic[T]):
    """列表响应"""
    data: List[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


class PageParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class ErrorResponse(ResponseBase):
    """错误响应"""
    code: int = 400
    message: str = "error"
    detail: Optional[str] = None


def success_response(message: str = "success", data: Any = None) -> dict:
    """成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def error_response(message: str = "error", code: int = 400, detail: str = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "detail": detail
    }
