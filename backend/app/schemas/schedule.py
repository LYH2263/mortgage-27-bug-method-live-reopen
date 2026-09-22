from typing import Literal
from pydantic import BaseModel, Field

Method = Literal["equal_payment", "equal_principal"]

class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    method: Method = "equal_payment"
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)

class SettingsUpdate(BaseModel):
    method: Method | None = None
