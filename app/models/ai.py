"""
AI服务和扫码相关模型
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIServiceLog(Base):
    """AI服务调用日志"""
    __tablename__ = "ai_service_logs"

    id = Column(Integer, primary_key=True, index=True)
    service_type = Column(
        Enum("shelf_analysis", "barcode_recognition", "food_classify", name="ai_service_type_enum"),
        nullable=False
    )
    request_data = Column(Text)  # 请求数据(JSON)
    response_data = Column(Text)  # 响应数据(JSON)
    status = Column(
        Enum("pending", "success", "failed", name="ai_log_status_enum"),
        default="pending"
    )
    error_message = Column(Text)
    duration_ms = Column(Integer)  # 耗时(毫秒)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AIServiceLog {self.service_type}: {self.status}>"


class ScanAudit(Base):
    """扫码审核表"""
    __tablename__ = "scan_audits"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("user_scans.id"), nullable=False)
    audit_type = Column(
        Enum("ai", "manual", name="audit_type_enum"),
        default="ai"
    )
    result = Column(
        Enum("approved", "rejected", name="audit_result_enum"),
        nullable=False
    )
    verified_food_id = Column(Integer, ForeignKey("foods.id"))  # 识别到的食品ID
    shelf_positions = Column(Text)  # AI识别的货架位置(JSON)
    reject_reason = Column(String(255))  # 拒绝原因
    audited_at = Column(DateTime)

    # 关系
    scan = relationship("UserScan")
    verified_food = relationship("Food")

    def __repr__(self):
        return f"<ScanAudit {self.scan_id}: {self.result}>"
