from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.producto import Categoria
from schemas.producto import CategoriaResponse, CategoriaCreate
from database import get_db
from api.routes.auth import get_current_admin
from typing import List

router = APIRouter()

@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Listar todas las categorías"""
    categorias = db.query(Categoria).offset(skip).limit(limit).all()
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaResponse)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Obtener categoría por ID"""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@router.post("/", response_model=CategoriaResponse)
def crear_categoria(
    categoria: CategoriaCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear nueva categoría (solo admin)"""
    if db.query(Categoria).filter(Categoria.nombre == categoria.nombre).first():
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    
    nueva = Categoria(**categoria.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{categoria_id}", response_model=CategoriaResponse)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar categoría (solo admin)"""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    categoria.nombre = datos.nombre
    categoria.descripcion = datos.descripcion
    
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria

@router.delete("/{categoria_id}")
def eliminar_categoria(
    categoria_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar categoría (solo admin)"""
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    db.delete(categoria)
    db.commit()
    return {"message": "Categoría eliminada exitosamente"}
