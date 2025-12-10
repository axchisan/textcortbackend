from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.venta import Venta, DetalleVenta
from models.producto import Producto
from models.usuario import Usuario
from schemas.venta import VentaCreate, VentaResponse, VentaUpdate, DetalleVentaBase
from database import get_db
from api.routes.auth import get_current_user, get_current_admin
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=List[VentaResponse])
def listar_ventas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    fecha_desde: str = Query(None),
    fecha_hasta: str = Query(None),
    usuario_id: int = Query(None),
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Listar todas las ventas (solo admin)"""
    query = db.query(Venta)
    
    if usuario_id:
        query = query.filter(Venta.usuario_id == usuario_id)
    
    if fecha_desde:
        fd = datetime.strptime(fecha_desde, "%Y-%m-%d")
        query = query.filter(Venta.fecha >= fd)
    
    if fecha_hasta:
        fh = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(Venta.fecha < fh)
    
    ventas = query.order_by(Venta.fecha.desc()).offset(skip).limit(limit).all()
    return ventas

@router.get("/mis-ventas", response_model=List[VentaResponse])
def obtener_mis_ventas(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener ventas del usuario actual"""
    ventas = db.query(Venta).filter(Venta.usuario_id == current_user.id).order_by(Venta.fecha.desc()).offset(skip).limit(limit).all()
    return ventas

@router.get("/{venta_id}", response_model=VentaResponse)
def obtener_venta(
    venta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener detalle de una venta"""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    if venta.usuario_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    return venta

@router.post("/", response_model=VentaResponse)
def crear_venta(
    venta_data: VentaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva venta"""
    if not venta_data.detalles:
        raise HTTPException(status_code=400, detail="Debe incluir al menos un detalle")
    
    total = 0
    detalles = []
    
    for detalle_data in venta_data.detalles:
        producto = db.query(Producto).filter(Producto.id == detalle_data.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {detalle_data.producto_id} no encontrado")
        
        if producto.stock < detalle_data.cantidad:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {producto.nombre}")
        
        subtotal = producto.precio * detalle_data.cantidad
        total += subtotal
        
        detalle = DetalleVenta(
            producto_id=detalle_data.producto_id,
            cantidad=detalle_data.cantidad,
            precio_unitario=producto.precio,
            subtotal=subtotal,
            color_seleccionado=detalle_data.color_seleccionado,
            talla_seleccionada=detalle_data.talla_seleccionada
        )
        
        producto.stock -= detalle_data.cantidad
        db.add(producto)
        detalles.append(detalle)
    
    nueva_venta = Venta(
        usuario_id=current_user.id,
        total=total
    )
    
    db.add(nueva_venta)
    db.flush()
    
    for detalle in detalles:
        detalle.venta_id = nueva_venta.id
        db.add(detalle)
    
    db.commit()
    db.refresh(nueva_venta)
    
    return nueva_venta

@router.put("/{venta_id}", response_model=VentaResponse)
def actualizar_venta(
    venta_id: int,
    datos: VentaUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Actualizar venta (solo admin)"""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    db.add(venta)
    db.commit()
    db.refresh(venta)
    return venta

@router.delete("/{venta_id}")
def cancelar_venta(
    venta_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cancelar venta y devolver stock (solo admin)"""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    for detalle in venta.detalles:
        if detalle.producto:
            detalle.producto.stock += detalle.cantidad
            db.add(detalle.producto)
    
    db.delete(venta)
    db.commit()
    
    return {"message": "Venta cancelada y stock restaurado"}

@router.get("/stats/resumenes")
def obtener_resumenes_totales(
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Obtener resumen total de ventas"""
    ventas = db.query(Venta).all()
    total_ventas = len(ventas)
    total_ingresos = sum(v.total for v in ventas) if ventas else 0
    
    return {
        "total_ventas": total_ventas,
        "total_ingresos": total_ingresos,
        "promedio_venta": total_ingresos / total_ventas if total_ventas > 0 else 0
    }
