from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DetalleVentaBase(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0)
    color_seleccionado: Optional[str] = None
    talla_seleccionada: Optional[str] = None

class DetalleVentaResponse(DetalleVentaBase):
    id: int
    precio_unitario: float
    subtotal: float
    producto_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True

class VentaCreate(BaseModel):
    detalles: List[DetalleVentaBase] = Field(..., min_items=1)

class VentaUpdate(BaseModel):
    pass

class VentaResponse(BaseModel):
    id: int
    usuario_id: Optional[int] = None
    total: float
    fecha: datetime
    detalles: List[DetalleVentaResponse]
    
    class Config:
        from_attributes = True
