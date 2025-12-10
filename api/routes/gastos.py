from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.gasto import Gasto
from schemas.gasto import GastoCreate, GastoResponse, GastoUpdate
from database import get_db
from api.routes.auth import get_current_admin
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=List[GastoResponse])
def listar_gastos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    categoria: str = Query(None),
    fecha_desde: str = Query(None),
    fecha_hasta: str = Query(None),
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Listar gastos con filtros (solo admin)"""
    query = db.query(Gasto)
    
    if categoria:
        query = query.filter(Gasto.categoria == categoria)
    
    if fecha_desde:
        fd = datetime.strptime(fecha_desde, "%Y-%m-%d")
        query = query.filter(Gasto.fecha >= fd)
    
    if fecha_hasta:
        fh = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(Gasto.fecha < fh)
    
    gastos = query.order_by(Gasto.fecha.desc()).offset(skip).limit(limit).all()
    return gastos

@router.get("/{gasto_id}", response_model=GastoResponse)
def obtener_gasto(
    gasto_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtener gasto por ID"""
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return gasto

@router.post("/", response_model=GastoResponse)
def crear_gasto(
    gasto: GastoCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Crear nuevo gasto (solo admin)"""
    nuevo = Gasto(**gasto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{gasto_id}", response_model=GastoResponse)
def actualizar_gasto(
    gasto_id: int,
    datos: GastoUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar gasto (solo admin)"""
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    update_data = datos.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gasto, field, value)
    
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return gasto

@router.delete("/{gasto_id}")
def eliminar_gasto(
    gasto_id: int,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Eliminar gasto (solo admin)"""
    gasto = db.query(Gasto).filter(Gasto.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    db.delete(gasto)
    db.commit()
    return {"message": "Gasto eliminado exitosamente"}

@router.get("/categorias/lista")
def obtener_categorias_gastos(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtener categorías de gastos disponibles"""
    categorias = db.query(Gasto.categoria).distinct().all()
    return [cat[0] for cat in categorias if cat[0]]
