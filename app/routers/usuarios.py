from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import timedelta

from ..database import get_db
from ..models.usuario import Usuario, RolEnum
from ..schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate, Token
from ..utils.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_active_user,
    get_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    normalize_matricula
)

router = APIRouter()

@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en el sistema.
    """
    # La matrícula ya viene en minúsculas gracias al validador
    matricula = normalize_matricula(usuario.matricula)
    
    # Verificar si la matrícula ya existe
    db_usuario = db.query(Usuario).filter(Usuario.matricula == matricula).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La matrícula ya está registrada"
        )
    
    # Verificar si el correo ya existe
    db_usuario = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )
    
    # Crear el usuario
    hashed_password = get_password_hash(usuario.contrasena)
    db_usuario = Usuario(
        matricula=matricula,  # Ya está en minúsculas
        nombre=usuario.nombre,
        apellido_paterno=usuario.apellido_paterno,
        apellido_materno=usuario.apellido_materno,
        contrasena_hash=hashed_password,
        rol=usuario.rol,
        correo=usuario.correo,
        semestre_id=usuario.semestre_id
    )
    
    try:
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el usuario. Verifica que el semestre exista."
        )

@router.get("/", response_model=List[UsuarioResponse])
def read_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    current_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de usuarios (solo administradores).
    """
    query = db.query(Usuario)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            (Usuario.nombre.like(search)) |
            (Usuario.apellido_paterno.like(search)) |
            (Usuario.apellido_materno.like(search)) |
            (Usuario.matricula.like(search)) |
            (Usuario.correo.like(search))
        )
    
    return query.offset(skip).limit(limit).all()

@router.get("/{matricula}", response_model=UsuarioResponse)
def read_usuario(
    matricula: str, 
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene un usuario por su matrícula.
    """
    # Convertir a minúsculas para la búsqueda
    matricula = normalize_matricula(matricula)
    
    # Solo el propio usuario o un administrador puede ver los detalles
    if current_user.matricula != matricula and current_user.rol != RolEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )
    
    db_usuario = db.query(Usuario).filter(Usuario.matricula == matricula).first()
    if db_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return db_usuario

@router.put("/{matricula}", response_model=UsuarioResponse)
def update_usuario(
    matricula: str,
    usuario: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza un usuario existente.
    """
    # Convertir a minúsculas para la búsqueda
    matricula = normalize_matricula(matricula)
    
    # Solo el propio usuario o un administrador puede actualizar
    if current_user.matricula != matricula and current_user.rol != RolEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    db_usuario = db.query(Usuario).filter(Usuario.matricula == matricula).first()
    if db_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar campos si están presentes
    update_data = usuario.dict(exclude_unset=True)
    
    # Solo un administrador puede cambiar el rol
    if "rol" in update_data and current_user.rol != RolEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar el rol"
        )
    
    # Si hay una nueva contraseña, hashearla
    if "contrasena" in update_data:
        update_data["contrasena_hash"] = get_password_hash(update_data.pop("contrasena"))
    
    for key, value in update_data.items():
        setattr(db_usuario, key, value)
    
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el usuario. Verifica que el semestre exista o que el correo no esté en uso."
        )

@router.delete("/{matricula}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    matricula: str,
    current_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario (solo administradores).
    """
    # Convertir a minúsculas para la búsqueda
    matricula = normalize_matricula(matricula)
    
    db_usuario = db.query(Usuario).filter(Usuario.matricula == matricula).first()
    if db_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    db.delete(db_usuario)
    db.commit()
    return None

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica un usuario y devuelve un token JWT.
    """
    # Convertir a minúsculas para la búsqueda
    username = normalize_matricula(form_data.username)
    
    user = db.query(Usuario).filter(Usuario.matricula == username).first()
    if not user or not verify_password(form_data.password, user.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matrícula o contraseña incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.matricula}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "matricula": user.matricula,
        "nombre": user.nombre,
        "rol": user.rol
    }

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    old_password: str,
    new_password: str,
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario actual.
    """
    if not verify_password(old_password, current_user.contrasena_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    current_user.contrasena_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}