from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GastoCreate(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=255)
    monto: float = Field(..., gt=0)
    categoria: Optional[str] = None

class GastoUpdate(BaseModel):
    descripcion: Optional[str] = None
    monto: Optional[float] = None
    categoria: Optional[str] = None

class GastoResponse(GastoCreate):
    id: int
    fecha: datetime
    
    class Config:
        from_attributes = True
