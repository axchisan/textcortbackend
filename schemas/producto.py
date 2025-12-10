from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    categoria_id: Optional[int] = None
    destacado: bool = False
    colores: Optional[str] = None
    tallas: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    categoria_id: Optional[int] = None
    destacado: Optional[bool] = None
    colores: Optional[str] = None
    tallas: Optional[str] = None

class ProductoResponse(ProductoBase):
    id: int
    imagen: Optional[str] = None
    created_at: datetime
    categoria: Optional[CategoriaResponse] = None
    
    class Config:
        from_attributes = True
