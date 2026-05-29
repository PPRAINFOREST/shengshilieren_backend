"""
Notifications API - 通知相关接口
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.notification import Notification
from app.schemas.response import success_response

router = APIRouter()


@router.get("/")
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_read: bool = Query(None, description="是否已读"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取通知列表"""
    query = db.query(Notification).filter(
        Notification.customer_id == current_user["id"]
    )
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    total = query.count()
    notifications = query.order_by(desc(Notification.created_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return success_response(data={
        "notifications": [{
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        } for n in notifications],
        "total": total,
        "page": page,
        "page_size": page_size
    })


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """标记通知为已读"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.customer_id == current_user["id"]
    ).first()
    
    if notification:
        notification.is_read = True
        db.commit()
    
    return success_response(message="已标记为已读")


@router.put("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """标记所有通知为已读"""
    db.query(Notification).filter(
        Notification.customer_id == current_user["id"],
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    return success_response(message="全部已读")
