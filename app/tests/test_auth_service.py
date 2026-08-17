import pytest
from fastapi import HTTPException
try:
    from app.services.auth_service import AuthService, get_current_user
except ModuleNotFoundError:
    try:
        from services.auth_service import AuthService, get_current_user
    except ModuleNotFoundError:
        from auth_service import AuthService, get_current_user

def test_password_hashing_and_verification():
    password = "secret_password_123"
    hashed = AuthService.hash_password(password)
    
    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrong_password", hashed) is False

def test_jwt_token_generation_and_decoding():
    user_id = 42
    token = AuthService.create_access_token(data={"sub": str(user_id)})
    
    assert isinstance(token, str)
    decoded = AuthService.decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"


def test_missing_token_is_rejected():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=None, db=None)

    assert exc_info.value.status_code == 401
