from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.producto import Producto
from schemas.venta import DetalleVentaBase
from database import get_db
from api.routes.auth import get_current_user
from models.usuario import Usuario
from typing import List, Dict, Any

router = APIRouter()

# Simulación de carrito en memoria (en producción usar Redis o BD)
carritos = {}

@router.get("/")
def obtener_carrito(current_user: Usuario = Depends(get_current_user)):
    """Obtener el carrito del usuario actual"""
    usuario_id = current_user.id
    carrito = carritos.get(usuario_id, {})
    
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    cantidad_items = sum(item['cantidad'] for item in carrito.values())
    
    return {
        "items": list(carrito.values()),
        "total": round(total, 2),
        "cantidad_items": cantidad_items
    }

@router.post("/agregar")
def agregar_al_carrito(
    producto_id: int,
    cantidad: int,
    color: str = "Único",
    talla: str = "Única",
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar producto al carrito"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if producto.stock < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")
    
    usuario_id = current_user.id
    if usuario_id not in carritos:
        carritos[usuario_id] = {}
    
    clave_item = f"{producto_id}_{color}_{talla}"
    
    if clave_item in carritos[usuario_id]:
        carritos[usuario_id][clave_item]['cantidad'] += cantidad
    else:
        carritos[usuario_id][clave_item] = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'imagen': producto.imagen,
            'cantidad': cantidad,
            'color': color,
            'talla': talla,
            'clave_unica': clave_item
        }
    
    return {"message": "Producto agregado al carrito", "item": carritos[usuario_id][clave_item]}

@router.put("/actualizar/{clave_unica}/{accion}")
def actualizar_cantidad(
    clave_unica: str,
    accion: str,
    current_user: Usuario = Depends(get_current_user)
):
    """Actualizar cantidad de producto en carrito"""
    usuario_id = current_user.id
    
    if usuario_id not in carritos or clave_unica not in carritos[usuario_id]:
        raise HTTPException(status_code=404, detail="Item no encontrado en carrito")
    
    if accion == 'aumentar':
        carritos[usuario_id][clave_unica]['cantidad'] += 1
    elif accion == 'disminuir':
        if carritos[usuario_id][clave_unica]['cantidad'] > 1:
            carritos[usuario_id][clave_unica]['cantidad'] -= 1
        else:
            del carritos[usuario_id][clave_unica]
            return {"message": "Producto eliminado del carrito"}
    
    return {"quantity": carritos[usuario_id][clave_unica]['cantidad']}

@router.delete("/eliminar/{clave_unica}")
def eliminar_del_carrito(
    clave_unica: str,
    current_user: Usuario = Depends(get_current_user)
):
    """Eliminar producto del carrito"""
    usuario_id = current_user.id
    
    if usuario_id not in carritos or clave_unica not in carritos[usuario_id]:
        raise HTTPException(status_code=404, detail="Item no encontrado en carrito")
    
    nombre_producto = carritos[usuario_id][clave_unica]['nombre']
    del carritos[usuario_id][clave_unica]
    
    return {"message": f"{nombre_producto} eliminado del carrito"}

@router.post("/vaciar")
def vaciar_carrito(current_user: Usuario = Depends(get_current_user)):
    """Vaciar carrito"""
    usuario_id = current_user.id
    if usuario_id in carritos:
        del carritos[usuario_id]
    
    return {"message": "Carrito vaciado"}
