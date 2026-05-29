"""
Auth API - 认证相关接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import Customer, Merchant
from app.schemas.user import CustomerCreate, MerchantCreate, CustomerResponse, MerchantResponse, LoginResponse
from app.schemas.response import success_response, error_response

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """获取当前登录用户"""
    from app.core.security import decode_token
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期"
        )
    
    user_type = payload.get("type")
    user_id = payload.get("sub")
    
    if user_type == "customer":
        user = db.query(Customer).filter(Customer.id == int(user_id)).first()
    elif user_type == "merchant":
        user = db.query(Merchant).filter(Merchant.id == int(user_id)).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户类型"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    return {"user": user, "type": user_type}


@router.post("/register/customer", response_model=dict)
def register_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """客户注册"""
    # 检查手机号是否已注册
    existing = db.query(Customer).filter(
        Customer.phone == data.phone
    ).first()
    
    if existing:
        return error_response("该手机号已注册")
    
    # 创建用户
    customer = Customer(
        phone=data.phone,
        nickname=data.nickname,
        hashed_password=data.password  # 实际应该在service层加密
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return success_response(
        data=CustomerResponse.model_validate(customer).model_dump(),
        msg="注册成功"
    )


@router.post("/register/merchant", response_model=dict)
def register_merchant(
    data: MerchantCreate,
    db: Session = Depends(get_db)
):
    """商家注册"""
    # 检查手机号是否已注册
    existing = db.query(Merchant).filter(
        Merchant.phone == data.phone
    ).first()
    
    if existing:
        return error_response("该手机号已注册")
    
    # 创建商家
    merchant = Merchant(
        phone=data.phone,
        store_name=data.store_name,
        store_type_id=data.store_type_id,
        contact_phone=data.contact_phone,
        verified=False
    )
    
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    
    return success_response(
        data=MerchantResponse.model_validate(merchant).model_dump(),
        msg="注册成功，请等待审核"
    )


@router.post("/login", response_model=dict)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录（支持客户和商家）"""
    # 尝试客户登录
    customer = db.query(Customer).filter(
        Customer.phone == form_data.username
    ).first()
    
    if customer:
        # 验证密码（实际应该用 bcrypt）
        if customer.hashed_password != form_data.password:
            return error_response("密码错误")
        
        # 生成Token
        access_token = create_access_token(
            data={"sub": str(customer.id), "type": "customer"},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user_type": "customer",
                "user": CustomerResponse.model_validate(customer).model_dump()
            }
        )
    
    # 尝试商家登录
    merchant = db.query(Merchant).filter(
        Merchant.phone == form_data.username
    ).first()
    
    if merchant:
        if merchant.hashed_password != form_data.password:
            return error_response("密码错误")
        
        access_token = create_access_token(
            data={"sub": str(merchant.id), "type": "merchant"},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "user_type": "merchant",
                "user": MerchantResponse.model_validate(merchant).model_dump()
            }
        )
    
    return error_response("用户不存在")


@router.get("/me", response_model=dict)
def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """获取当前用户信息"""
    user = current_user["user"]
    user_type = current_user["type"]
    
    if user_type == "customer":
        return success_response(
            data=CustomerResponse.model_validate(user).model_dump()
        )
    else:
        return success_response(
            data=MerchantResponse.model_validate(user).model_dump()
        )
