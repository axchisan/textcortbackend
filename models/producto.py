from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from typing import List

class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(Text)
    
    productos = relationship("Producto", back_populates="categoria", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }

class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(Text)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    imagen = Column(String(255))
    colores = Column(String(500))
    tallas = Column(String(500))
    destacado = Column(Boolean, default=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    categoria = relationship("Categoria", back_populates="productos")
    detalles = relationship("DetalleVenta", back_populates="producto")
    
    def get_colores(self) -> List[str]:
        if self.colores:
            return [color.strip() for color in self.colores.split(',')]
        return []
    
    def get_tallas(self) -> List[str]:
        if self.tallas:
            return [talla.strip() for talla in self.tallas.split(',')]
        return []
    
    def to_dict(self, include_relationships=False):
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "stock": self.stock,
            "imagen": self.imagen,
            "colores": self.get_colores(),
            "tallas": self.get_tallas(),
            "destacado": self.destacado,
            "categoria_id": self.categoria_id,
            "created_at": self.created_at
        }
        if include_relationships and self.categoria:
            data["categoria"] = self.categoria.to_dict()
        return data
