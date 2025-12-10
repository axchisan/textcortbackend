from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from api.routes.auth import get_current_admin
from models.usuario import Usuario
from models.producto import Producto
from models.venta import Venta, DetalleVenta
from models.gasto import Gasto
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
def estadisticas_dashboard(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Estadísticas principales para dashboard"""
    
    # Totales generales
    total_usuarios = db.query(func.count(Usuario.id)).scalar() or 0
    total_productos = db.query(func.count(Producto.id)).scalar() or 0
    total_ventas = db.query(func.sum(Venta.total)).scalar() or 0
    total_gastos = db.query(func.sum(Gasto.monto)).scalar() or 0
    
    # Hoy
    hoy = datetime.now().date()
    ventas_hoy = db.query(func.sum(Venta.total)).filter(
        func.date(Venta.created_at) == hoy
    ).scalar() or 0
    
    gastos_hoy = db.query(func.sum(Gasto.monto)).filter(
        func.date(Gasto.created_at) == hoy
    ).scalar() or 0
    
    # Usuarios activos
    usuarios_activos = db.query(func.count(Usuario.id)).filter(Usuario.is_active == True).scalar() or 0
    
    # Productos destacados
    productos_destacados = db.query(func.count(Producto.id)).filter(Producto.destacado == True).scalar() or 0
    
    # Stock bajo
    stock_bajo = db.query(func.count(Producto.id)).filter(Producto.stock < 10).scalar() or 0
    
    # Ticket promedio
    cantidad_ventas = db.query(func.count(Venta.id)).scalar() or 0
    ticket_promedio = total_ventas / cantidad_ventas if cantidad_ventas > 0 else 0
    
    return {
        "total_usuarios": total_usuarios,
        "usuarios_activos": usuarios_activos,
        "total_productos": total_productos,
        "productos_destacados": productos_destacados,
        "stock_bajo": stock_bajo,
        "total_ventas": round(total_ventas, 2),
        "total_gastos": round(total_gastos, 2),
        "neto": round(total_ventas - total_gastos, 2),
        "ventas_hoy": round(ventas_hoy, 2),
        "gastos_hoy": round(gastos_hoy, 2),
        "cantidad_ventas": cantidad_ventas,
        "ticket_promedio": round(ticket_promedio, 2)
    }

@router.get("/usuarios")
def estadisticas_usuarios(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Estadísticas de usuarios"""
    total = db.query(func.count(Usuario.id)).scalar() or 0
    activos = db.query(func.count(Usuario.id)).filter(Usuario.is_active == True).scalar() or 0
    admins = db.query(func.count(Usuario.id)).filter(Usuario.is_admin == True).scalar() or 0
    
    # Nuevos usuarios este mes
    hoy = datetime.now()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1)
    nuevos_mes = db.query(func.count(Usuario.id)).filter(
        Usuario.created_at >= primer_dia_mes
    ).scalar() or 0
    
    return {
        "total": total,
        "activos": activos,
        "inactivos": total - activos,
        "administradores": admins,
        "clientes": total - admins,
        "nuevos_este_mes": nuevos_mes
    }

@router.get("/productos")
def estadisticas_productos(
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Estadísticas de productos"""
    total = db.query(func.count(Producto.id)).scalar() or 0
    destacados = db.query(func.count(Producto.id)).filter(Producto.destacado == True).scalar() or 0
    sin_stock = db.query(func.count(Producto.id)).filter(Producto.stock == 0).scalar() or 0
    stock_bajo = db.query(func.count(Producto.id)).filter(
        (Producto.stock > 0) & (Producto.stock < 10)
    ).scalar() or 0
    
    valor_inventario = db.query(
        func.sum(Producto.precio * Producto.stock)
    ).scalar() or 0
    
    return {
        "total": total,
        "destacados": destacados,
        "sin_stock": sin_stock,
        "stock_bajo": stock_bajo,
        "valor_inventario": round(valor_inventario, 2)
    }
