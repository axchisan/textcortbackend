from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Gasto(Base):
    __tablename__ = "gastos"
    
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String(100))
    fecha = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "descripcion": self.descripcion,
            "monto": round(self.monto, 2),
            "categoria": self.categoria,
            "fecha": self.fecha
        }
