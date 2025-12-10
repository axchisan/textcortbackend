from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, UsuarioResponse, TokenResponse, LoginRequest
from database import get_db
from config import settings

router = APIRouter()

# IMPORTANTE: El tokenUrl debe coincidir exactamente con tu ruta de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")  # Cambio aquí: str en vez de int
        if user_id is None:
            raise credentials_exception
        
        # Convertir a int para buscar en la base de datos
        user_id = int(user_id)  # Cambio aquí: convertir de string a int
    except JWTError as e:
        # Log para debugging
        print(f"JWT Error: {str(e)}")
        raise credentials_exception
    except ValueError:
        # Si no se puede convertir a int
        raise credentials_exception
    
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if usuario is None:
        raise credentials_exception
    return usuario


def get_current_admin(current_user: Usuario = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado. Se requieren permisos de administrador."
        )
    return current_user


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    if db.query(Usuario).filter(Usuario.username == usuario.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    
    nuevo_usuario = Usuario(**usuario.dict(exclude={"password"}))
    nuevo_usuario.set_password(usuario.password)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=TokenResponse)
async def login(
    db: Session = Depends(get_db),
    # Parámetros para form-data (Swagger UI con OAuth2)
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    # Parámetros para JSON (Frontend)
    body: Optional[LoginRequest] = Body(None)
):
    """
    Iniciar sesión y obtener token.
    
    Soporta dos formatos:
    - Form data (OAuth2): username (usar email aquí) y password
    - JSON: {"email": "user@example.com", "password": "password123"}
    """
    # Determinar si viene de form-data o JSON
    if body is not None:
        # Petición JSON desde frontend
        user_email = body.email
        user_password = body.password
    elif username and password:
        # Petición form-data desde Swagger UI
        # En Swagger, el campo 'username' debe contener el email
        user_email = username
        user_password = password
    else:
        raise HTTPException(
            status_code=422, 
            detail="Debe proporcionar credenciales en formato JSON o form-data"
        )
    
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == user_email).first()
    
    if not usuario or not usuario.verify_password(user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Crear token de acceso - IMPORTANTE: convertir user_id a string
    access_token = create_access_token(data={"sub": str(usuario.id)})  # Cambio aquí: str(usuario.id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=usuario
    )


@router.get("/me", response_model=UsuarioResponse)
def get_current_user_info(current_user: Usuario = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(current_user: Usuario = Depends(get_current_user)):
    """Renovar token de acceso"""
    # IMPORTANTE: convertir user_id a string
    access_token = create_access_token(data={"sub": str(current_user.id)})  # Cambio aquí: str(current_user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        usuario=current_user
    )