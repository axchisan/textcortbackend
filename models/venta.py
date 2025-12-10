from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Venta(Base):
    __tablename__ = "ventas"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, server_default=func.now())
    
    usuario = relationship("Usuario", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    
    def to_dict(self, include_detalles=True):
        data = {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "total": round(self.total, 2),
            "fecha": self.fecha
        }
        if include_detalles:
            data["detalles"] = [d.to_dict() for d in self.detalles]
        return data

class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"
    
    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    color_seleccionado = Column(String(50))
    talla_seleccionada = Column(String(20))
    
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles")
    
    def to_dict(self):
        return {
            "id": self.id,
            "venta_id": self.venta_id,
            "producto_id": self.producto_id,
            "producto_nombre": self.producto.nombre if self.producto else None,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "subtotal": round(self.subtotal, 2),
            "color_seleccionado": self.color_seleccionado,
            "talla_seleccionada": self.talla_seleccionada
        }
