"""
AI API - AI服务相关接口
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.response import success_response, error_response
from app.services.ai_service import (
    analyze_shelf_image,
    recognize_barcode,
    audit_scan,
    recommend_price
)

router = APIRouter()


@router.post("/validate-shelf", response_model=dict)
async def validate_shelf_image(
    image_url: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    分析货架图片，生成货架位置与编号
    
    商家上传货架布局图，AI识别并生成货架编号
    """
    if current_user["type"] != "merchant":
        return error_response("只有商家才能使用此功能")
    
    try:
        result = await analyze_shelf_image(image_url)
        return success_response(
            data=result,
            msg="货架分析完成"
        )
    except Exception as e:
        return error_response(f"货架分析失败: {str(e)}")


@router.post("/recognize-barcode", response_model=dict)
async def recognize_barcode_api(
    image_url: str,
    db: Session = Depends(get_db)
):
    """
    识别条形码，获取商品信息
    
    用户扫码时调用，返回商品基本信息
    """
    try:
        result = await recognize_barcode(image_url)
        return success_response(
            data=result,
            msg="识别成功"
        )
    except Exception as e:
        return error_response(f"识别失败: {str(e)}")


@router.post("/audit-scan", response_model=dict)
async def audit_scan_api(
    image_url: str,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    审核用户扫码上传
    
    AI审核用户发现的临期商品，判定是否通过
    """
    if current_user["type"] != "customer":
        return error_response("只有客户才能提交扫码审核")
    
    customer = current_user["user"]
    
    try:
        result = await audit_scan(
            customer_id=customer.id,
            image_url=image_url,
            latitude=latitude,
            longitude=longitude
        )
        
        return success_response(
            data=result,
            msg="审核完成"
        )
    except Exception as e:
        return error_response(f"审核失败: {str(e)}")


@router.post("/recommend-price", response_model=dict)
async def recommend_price_api(
    original_price: float,
    expiry_hours: int,
    risk_level: str = "medium"
):
    """
    智能定价推荐
    
    根据剩余保质期和风险等级，推荐折扣价格
    """
    try:
        recommended_price = await recommend_price(
            original_price=original_price,
            expiry_hours=expiry_hours,
            risk_level=risk_level
        )
        
        return success_response(
            data={
                "original_price": original_price,
                "recommended_price": recommended_price,
                "discount_rate": round((1 - recommended_price / original_price) * 100, 1)
            },
            msg="定价推荐成功"
        )
    except Exception as e:
        return error_response(f"定价推荐失败: {str(e)}")
