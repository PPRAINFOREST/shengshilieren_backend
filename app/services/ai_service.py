"""
AI 服务 - 货架分析、食品验证等 AI 功能
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
import json

from app.models.ai import AIServiceLog, ScanAudit


def log_ai_request(
    db: Session,
    analysis_type: str,
    request_data: dict,
    response_data: Optional[dict] = None,
    status: str = "pending",
    error_message: Optional[str] = None,
    processing_time_ms: Optional[int] = None
) -> AIServiceLog:
    """
    记录 AI 请求日志
    
    Args:
        db: 数据库会话
        analysis_type: 分析类型 (shelf/scan/food)
        request_data: 请求数据
        response_data: 响应数据
        status: 状态
        error_message: 错误信息
        processing_time_ms: 处理时间(毫秒)
    
    Returns:
        AIServiceLog: AI 日志记录
    """
    log = AIServiceLog(
        analysis_type=analysis_type,
        request_data=json.dumps(request_data),
        response_data=json.dumps(response_data) if response_data else None,
        status=status,
        error_message=error_message,
        processing_time_ms=processing_time_ms
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log


def update_ai_log(
    db: Session,
    log_id: int,
    response_data: dict,
    status: str = "success",
    error_message: Optional[str] = None,
    processing_time_ms: Optional[int] = None
) -> AIServiceLog:
    """
    更新 AI 日志
    
    Args:
        db: 数据库会话
        log_id: 日志ID
        response_data: 响应数据
        status: 状态
        error_message: 错误信息
        processing_time_ms: 处理时间(毫秒)
    
    Returns:
        AIServiceLog: 更新后的日志记录
    """
    log = db.query(AIServiceLog).filter(AIServiceLog.id == log_id).first()
    if not log:
        raise ValueError("AI 日志不存在")
    
    log.response_data = json.dumps(response_data)
    log.status = status
    log.error_message = error_message
    if processing_time_ms:
        log.processing_time_ms = processing_time_ms
    
    db.commit()
    db.refresh(log)
    
    return log


def create_scan_audit(
    db: Session,
    scan_id: int,
    audit_result: str,
    reviewer_id: Optional[int] = None,
    audit_notes: Optional[str] = None
) -> ScanAudit:
    """
    创建扫码审核记录
    
    Args:
        db: 数据库会话
        scan_id: 扫码记录ID
        audit_result: 审核结果 (approved/rejected)
        reviewer_id: 审核员ID
        audit_notes: 审核备注
    
    Returns:
        ScanAudit: 审核记录
    """
    audit = ScanAudit(
        scan_id=scan_id,
        audit_result=audit_result,
        reviewer_id=reviewer_id,
        audit_notes=audit_notes
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    
    return audit


def validate_food_expiry(
    db: Session,
    barcode: str,
    product_name: str,
    expiry_date: Optional[str] = None
) -> dict:
    """
    验证食品保质期
    
    Args:
        db: 数据库会话
        barcode: 条形码
        product_name: 产品名称
        expiry_date: 到期日期
    
    Returns:
        dict: 验证结果
    """
    # 实际项目中，这里会调用百度 AI 等服务进行验证
    # 这里简化处理，返回模拟结果
    
    from app.models.food import Food
    
    # 检查是否已知食品
    food = db.query(Food).filter(Food.barcode == barcode).first()
    
    if food:
        result = {
            "is_valid": True,
            "food_id": food.id,
            "food_name": food.name,
            "brand": food.brand,
            "avg_expiry_days": food.avg_expiry_days,
            "confidence": 0.95,
            "warning": None
        }
    else:
        # 新发现的食品
        result = {
            "is_valid": True,
            "food_id": None,
            "food_name": product_name,
            "brand": None,
            "avg_expiry_days": 7,  # 默认 7 天
            "confidence": 0.5,
            "warning": "新品录入，请等待审核"
        }
    
    # 检查日期合理性
    if expiry_date:
        from datetime import datetime, date
        try:
            exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
            today = date.today()
            days_until_expiry = (exp_date - today).days
            
            if days_until_expiry < 0:
                result["warning"] = "食品已过期"
                result["is_valid"] = False
            elif days_until_expiry <= 1:
                result["warning"] = "食品即将到期(1天内)"
            elif days_until_expiry <= 3:
                result["warning"] = "食品临近保质期(3天内)"
        except ValueError:
            result["warning"] = "日期格式无效"
    
    return result


def analyze_shelf_image(
    db: Session,
    shop_id: int,
    image_url: str,
    location_lat: Optional[float] = None,
    location_lng: Optional[float] = None
) -> dict:
    """
    分析货架图片，识别临期食品
    
    Args:
        db: 数据库会话
        shop_id: 店铺ID
        image_url: 图片URL
        location_lat: 纬度
        location_lng: 经度
    
    Returns:
        dict: 分析结果
    """
    # 实际项目中，这里会调用百度 AI 等服务进行图像识别
    # 这里简化处理，返回模拟结果
    
    result = {
        "success": True,
        "detected_foods": [],
        "confidence": 0.85,
        "message": "图片分析完成"
    }
    
    # 模拟检测到的食品
    # 实际项目中会返回识别到的食品列表
    
    return result


def get_ai_service_stats(db: Session, analysis_type: Optional[str] = None) -> dict:
    """
    获取 AI 服务统计
    
    Args:
        db: 数据库会话
        analysis_type: 分析类型过滤
    
    Returns:
        dict: 统计数据
    """
    from sqlalchemy import func
    
    query = db.query(AIServiceLog)
    
    if analysis_type:
        query = query.filter(AIServiceLog.analysis_type == analysis_type)
    
    total = query.count()
    success = query.filter(AIServiceLog.status == "success").count()
    failed = query.filter(AIServiceLog.status == "failed").count()
    
    # 计算平均处理时间
    avg_time = db.query(func.avg(AIServiceLog.processing_time_ms)).filter(
        AIServiceLog.processing_time_ms.isnot(None)
    ).scalar()
    
    return {
        "total_requests": total,
        "success_count": success,
        "failed_count": failed,
        "success_rate": round(success / total * 100, 2) if total > 0 else 0,
        "avg_processing_time_ms": round(avg_time, 2) if avg_time else 0
    }


def recognize_barcode(barcode_image_url: str) -> dict:
    """
    识别条形码
    
    Args:
        barcode_image_url: 条形码图片URL
    
    Returns:
        dict: 识别结果
    """
    # 实际项目中，这里会调用百度 AI 等服务进行条形码识别
    # 这里简化处理，返回模拟结果
    
    # 模拟返回的条形码
    result = {
        "success": True,
        "barcode": "6901234567890",  # 模拟条形码
        "barcode_type": "EAN-13",
        "confidence": 0.98
    }
    
    return result


def audit_scan(
    db: Session,
    scan_id: int,
    audit_result: str,
    audit_notes: Optional[str] = None
) -> dict:
    """
    审核扫码记录
    
    Args:
        db: 数据库会话
        scan_id: 扫码记录ID
        audit_result: 审核结果 (approved/rejected)
        audit_notes: 审核备注
    
    Returns:
        dict: 审核结果
    """
    from app.models.scan import UserScan
    
    scan = db.query(UserScan).filter(UserScan.id == scan_id).first()
    if not scan:
        raise ValueError("扫码记录不存在")
    
    scan.status = audit_result
    if audit_notes:
        scan.rejection_reason = audit_notes
    scan.audited_at = datetime.now()
    
    # 如果审核通过，发放积分
    if audit_result == "approved":
        scan.points_earned = 20  # 审核通过奖励 20 积分
        
        # 更新客户积分
        from app.models.user import Customer
        customer = db.query(Customer).filter(Customer.id == scan.customer_id).first()
        if customer:
            customer.points += scan.points_earned
    
    db.commit()
    
    return {
        "success": True,
        "scan_id": scan_id,
        "audit_result": audit_result,
        "points_earned": scan.points_earned if audit_result == "approved" else 0
    }


def recommend_price(
    original_price: int,
    expiry_days: int,
    category: str = "general"
) -> dict:
    """
    推荐折扣价格
    
    Args:
        original_price: 原价(分)
        expiry_days: 剩余保质期(天)
        category: 类别
    
    Returns:
        dict: 推荐价格
    """
    # 根据剩余保质期计算折扣
    if expiry_days <= 1:
        discount_rate = 0.2  # 1折
        discount_type = "critical"
    elif expiry_days <= 3:
        discount_rate = 0.3  # 3折
        discount_type = "high"
    elif expiry_days <= 7:
        discount_rate = 0.5  # 5折
        discount_type = "medium"
    else:
        discount_rate = 0.7  # 7折
        discount_type = "low"
    
    # 根据类别调整
    if category == "bread":
        discount_rate = max(0.1, discount_rate - 0.1)
    elif category == "dairy":
        discount_rate = max(0.2, discount_rate - 0.1)
    
    recommended_price = int(original_price * discount_rate)
    
    return {
        "original_price": original_price,
        "recommended_price": recommended_price,
        "discount_rate": discount_rate,
        "discount_type": discount_type,
        "savings": original_price - recommended_price
    }
