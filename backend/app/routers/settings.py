from fastapi import APIRouter
from app.schemas.schedule import SettingsUpdate
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/settings")
def settings():
    with MortgageService() as s: return s.settings()
@router.put("/settings")
def put_settings(body: SettingsUpdate):
    with MortgageService() as s: return s.update_settings(body.model_dump(exclude_none=True))
