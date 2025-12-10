from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.usuario import Usuario
from schemas.usuario import UsuarioResponse, UsuarioUpdate, UsuarioCreate
from database import get_db
from api.routes.auth import get_current_user, get_current_admin
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Listar todos los usuarios (solo admin)"""
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener usuario por ID"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/me", response_model=UsuarioResponse)
def actualizar_perfil(
    datos: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar perfil del usuario actual"""
    update_data = datos.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password" and value:
            current_user.set_password(value)
        else:
            setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar usuario (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = datos.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password" and value:
            usuario.set_password(value)
        else:
            setattr(usuario, field, value)
    
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{usuario_id}")
def eliminar_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar usuario (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}

@router.post("/{usuario_id}/toggle-admin")
def toggle_admin(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cambiar estado de administrador (solo admin)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.is_admin = not usuario.is_admin
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
