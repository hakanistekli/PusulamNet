from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
try:
    from app.database import get_db
except ModuleNotFoundError:
    try:
        from database import get_db
    except ModuleNotFoundError:
        from database import get_db
try:
    from app.services.demo_data_service import DemoDataService
except ModuleNotFoundError:
    try:
        from services.demo_data_service import DemoDataService
    except ModuleNotFoundError:
        from demo_data_service import DemoDataService

try:
    from app.models import User
except ModuleNotFoundError:
    from models import User

try:
    from app.services.auth_service import get_current_user
except ModuleNotFoundError:
    from services.auth_service import get_current_user

router = APIRouter(prefix="/api/demo", tags=["Demo Verisi"])

@router.post("/clear")
def clear_all_exams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Veritabanındaki tüm deneme sınavı kayıtlarını siler ve temizler.
    """
    result = DemoDataService.clear_all_practice_exams(db, current_user.id)
    return result

