from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
from api.routes.auth import get_current_admin
from models.venta import Venta, DetalleVenta
from models.gasto import Gasto
from models.producto import Producto
from models.usuario import Usuario

router = APIRouter()

@router.get("/financiero")
def reporte_financiero(
    fecha_desde: str = Query(None),
    fecha_hasta: str = Query(None),
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reporte financiero general"""
    query_ventas = db.query(Venta)
    query_gastos = db.query(Gasto)
    
    if fecha_desde:
        fd = datetime.strptime(fecha_desde, "%Y-%m-%d")
        query_ventas = query_ventas.filter(Venta.created_at >= fd)
        query_gastos = query_gastos.filter(Gasto.created_at >= fd)
    
    if fecha_hasta:
        fh = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1)
        query_ventas = query_ventas.filter(Venta.created_at < fh)
        query_gastos = query_gastos.filter(Gasto.created_at < fh)
    
    ventas = query_ventas.all()
    gastos = query_gastos.all()
    
    total_ventas = sum(v.total for v in ventas) if ventas else 0
    total_gastos = sum(g.monto for g in gastos) if gastos else 0
    
    return {
        "total_ventas": round(total_ventas, 2),
        "total_gastos": round(total_gastos, 2),
        "neto": round(total_ventas - total_gastos, 2),
        "cantidad_ventas": len(ventas),
        "cantidad_gastos": len(gastos),
        "ticket_promedio": round(total_ventas / len(ventas), 2) if ventas else 0
    }

@router.get("/ventas-por-mes")
def ventas_por_mes(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reporte de ventas por mes"""
    datos = db.query(
        func.month(Venta.created_at).label('mes'),
        func.sum(Venta.total).label('total')
    ).group_by(func.month(Venta.created_at)).all()
    
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    resultado = {}
    
    for mes, total in datos:
        if mes and mes <= 12:
            resultado[meses[mes-1]] = round(total, 2)
    
    return resultado

@router.get("/productos-top")
def productos_mas_vendidos(
    limit: int = Query(10, le=50),
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Productos más vendidos"""
    datos = db.query(
        Producto.id,
        Producto.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta).group_by(Producto.id).order_by(func.sum(DetalleVenta.cantidad).desc()).limit(limit).all()
    
    return [{"id": d[0], "nombre": d[1], "cantidad_vendida": d[2]} for d in datos]

@router.get("/categorias-rendimiento")
def rendimiento_categorias(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Rendimiento por categoría"""
    datos = db.query(
        func.count(Venta.id).label('cantidad_ventas'),
        func.sum(Venta.total).label('total')
    ).join(DetalleVenta).join(Producto).group_by(Producto.categoria_id).all()
    
    return {
        "cantidad_categorias": len(datos),
        "total_vendido": round(sum(d[1] or 0 for d in datos), 2)
    }

@router.get("/clientes-top")
def clientes_top(
    limit: int = Query(10, le=50),
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Clientes con más compras"""
    datos = db.query(
        Usuario.id,
        Usuario.username,
        Usuario.email,
        func.count(Venta.id).label('total_compras'),
        func.sum(Venta.total).label('monto_total')
    ).join(Venta).group_by(Usuario.id).order_by(func.sum(Venta.total).desc()).limit(limit).all()
    
    return [
        {
            "usuario_id": d[0],
            "username": d[1],
            "email": d[2],
            "total_compras": d[3],
            "monto_total": round(d[4], 2)
        }
        for d in datos
    ]

@router.get("/stock-bajo")
def productos_stock_bajo(
    umbral: int = Query(10),
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Productos con stock bajo"""
    productos = db.query(Producto).filter(Producto.stock < umbral).all()
    return [
        {
            "id": p.id,
            "nombre": p.nombre,
            "stock": p.stock,
            "sku": p.sku
        }
        for p in productos
    ]
