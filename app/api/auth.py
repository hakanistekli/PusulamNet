from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
try:
    from app.database import get_db
except ModuleNotFoundError:
    try:
        from database import get_db
    except ModuleNotFoundError:
        from database import get_db
try:
    from app.models import User
except ModuleNotFoundError:
    try:
        from models import User
    except ModuleNotFoundError:
        from models import User
try:
    from app.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
except ModuleNotFoundError:
    try:
        from schemas import UserRegister, UserLogin, TokenResponse, UserResponse
    except ModuleNotFoundError:
        from schemas import UserRegister, UserLogin, TokenResponse, UserResponse
try:
    from app.services.auth_service import AuthService, get_current_user
except ModuleNotFoundError:
    try:
        from services.auth_service import AuthService, get_current_user
    except ModuleNotFoundError:
        from auth_service import AuthService, get_current_user
try:
    from app.services.demo_data_service import DemoDataService
except ModuleNotFoundError:
    try:
        from services.demo_data_service import DemoDataService
    except ModuleNotFoundError:
        from demo_data_service import DemoDataService

router = APIRouter(prefix="/api/auth", tags=["Kimlik Doğrulama"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    """
    Yeni öğrenci kaydı oluşturur ve hazır sınav türlerini ilklendirir.
    """
    email_clean = data.email.strip().lower()
    existing_user = db.query(User).filter_by(email=email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi ile zaten bir hesap oluşturulmuş."
        )

    hashed_pw = AuthService.hash_password(data.password)
    user = User(
        name=data.name.strip(),
        email=email_clean,
        hashed_password=hashed_pw
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Yeni kayıt olan öğrenci için hazır sınav türlerini (YKS-TYT, YKS-AYT, LGS, KPSS, TUS, DUS) ilklendir
    DemoDataService.create_predefined_exam_types(db, user)

    # JWT Token üret
    token = AuthService.create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }

@router.post("/login", response_model=TokenResponse)
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    """
    Öğrenci girişi yapar ve JWT erişim jetonu döndürür.
    """
    email_clean = data.email.strip().lower()
    user = db.query(User).filter_by(email=email_clean).first()
    if not user or not AuthService.verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz e-posta adresi veya şifre."
        )

    token = AuthService.create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Oturum açmış olan öğrencinin profil bilgilerini getirir.
    """
    return current_user
