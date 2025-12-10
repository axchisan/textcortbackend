from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from models.producto import Producto, Categoria
from schemas.producto import ProductoResponse, ProductoCreate, ProductoUpdate, CategoriaResponse
from database import get_db
from api.routes.auth import get_current_user, get_current_admin
from typing import List
import os
from config import settings

router = APIRouter()

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    destacado: bool = Query(None),
    categoria_id: int = Query(None),
    buscar: str = Query(""),
    db: Session = Depends(get_db)
):
    """Listar productos con filtros opcionales"""
    query = db.query(Producto)
    
    if destacado is not None:
        query = query.filter(Producto.destacado == destacado)
    
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)
    
    if buscar:
        query = query.filter(Producto.nombre.ilike(f"%{buscar}%"))
    
    productos = query.offset(skip).limit(limit).all()
    return productos

@router.get("/destacados", response_model=List[ProductoResponse])
def obtener_productos_destacados(
    limit: int = Query(8, le=50),
    db: Session = Depends(get_db)
):
    """Obtener productos destacados"""
    productos = db.query(Producto).filter(Producto.destacado == True).limit(limit).all()
    return productos

@router.get("/recientes", response_model=List[ProductoResponse])
def obtener_productos_recientes(
    limit: int = Query(8, le=50),
    db: Session = Depends(get_db)
):
    """Obtener productos recientes"""
    productos = db.query(Producto).order_by(Producto.created_at.desc()).limit(limit).all()
    return productos

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtener producto por ID"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@router.post("/", response_model=ProductoResponse)
def crear_producto(
    producto: ProductoCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear nuevo producto (solo admin)"""
    colores_str = producto.colores if isinstance(producto.colores, str) else ",".join(producto.colores) if producto.colores else None
    tallas_str = producto.tallas if isinstance(producto.tallas, str) else ",".join(producto.tallas) if producto.tallas else None
    
    nuevo = Producto(
        **producto.dict(exclude={"colores", "tallas"}),
        colores=colores_str,
        tallas=tallas_str
    )
    
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int,
    datos: ProductoUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar producto (solo admin)"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    update_data = datos.dict(exclude_unset=True)
    
    if "colores" in update_data and update_data["colores"]:
        update_data["colores"] = update_data["colores"] if isinstance(update_data["colores"], str) else ",".join(update_data["colores"])
    if "tallas" in update_data and update_data["tallas"]:
        update_data["tallas"] = update_data["tallas"] if isinstance(update_data["tallas"], str) else ",".join(update_data["tallas"])
    
    for field, value in update_data.items():
        setattr(producto, field, value)
    
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/{producto_id}")
def eliminar_producto(
    producto_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar producto (solo admin)"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(producto)
    db.commit()
    return {"message": "Producto eliminado exitosamente"}

@router.post("/{producto_id}/stock")
def actualizar_stock(
    producto_id: int,
    cantidad: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar stock del producto (solo admin)"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.stock = max(0, producto.stock + cantidad)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return {"stock": producto.stock}

@router.post("/{producto_id}/destacar")
def toggle_destacado(
    producto_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Marcar/desmarcar producto como destacado (solo admin)"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.destacado = not producto.destacado
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return {"destacado": producto.destacado}
