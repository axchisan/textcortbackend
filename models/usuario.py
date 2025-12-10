from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    ventas = relationship("Venta", back_populates="usuario", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Hash password using werkzeug (same method as Flask)"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash using werkzeug (same method as Flask)"""
        try:
            return check_password_hash(self.password_hash, password)
        except Exception:
            return False
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at
        }
