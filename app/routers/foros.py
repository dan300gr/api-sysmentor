from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_db
from ..models.foro import Foro
from ..models.reaccion_foro import ReaccionForo
from ..schemas.foro import ForoCreate, Foro as ForoSchema, ForoUpdate
from ..schemas.comentario_foro import ComentarioForoCreate, ComentarioForo as ComentarioForoSchema
from ..schemas.reaccion_foro import ReaccionForoCreate, TipoReaccionEnum
from ..utils.security import get_current_active_user
from ..models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=ForoSchema, status_code=status.HTTP_201_CREATED)
def create_foro(
    foro: ForoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crea un nuevo tema en el foro.
    """
    db_foro = Foro(
        matricula=current_user.matricula,
        materia_id=foro.materia_id,
        titulo=foro.titulo,
        contenido=foro.contenido
    )
    
    try:
        db.add(db_foro)
        db.commit()
        db.refresh(db_foro)
        return db_foro
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el tema en el foro. Verifica que la materia exista."
        )

@router.get("/", response_model=List[ForoSchema])
def read_foros(
    skip: int = 0, 
    limit: int = 100, 
    materia_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene la lista de temas en el foro con filtros opcionales.
    """
    query = db.query(Foro)
    
    if materia_id:
        query = query.filter(Foro.materia_id == materia_id)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            (Foro.titulo.like(search)) |
            (Foro.contenido.like(search))
        )
    
    return query.order_by(Foro.fecha_publicacion.desc()).offset(skip).limit(limit).all()

@router.get("/{foro_id}", response_model=ForoSchema)
def read_foro(
    foro_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un tema del foro por su ID.
    """
    db_foro = db.query(Foro).filter(Foro.id == foro_id).first()
    if db_foro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tema del foro no encontrado"
        )
    return db_foro

@router.put("/{foro_id}", response_model=ForoSchema)
def update_foro(
    foro_id: int,
    foro: ForoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza un tema del foro existente.
    """
    db_foro = db.query(Foro).filter(Foro.id == foro_id).first()
    if db_foro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tema del foro no encontrado"
        )
    
    # Solo el autor o un administrador puede actualizar
    if db_foro.matricula != current_user.matricula and current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este tema del foro"
        )
    
    update_data = foro.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_foro, key, value)
    
    try:
        db.commit()
        db.refresh(db_foro)
        return db_foro
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el tema del foro."
        )

@router.delete("/{foro_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_foro(
    foro_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina un tema del foro.
    """
    db_foro = db.query(Foro).filter(Foro.id == foro_id).first()
    if db_foro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tema del foro no encontrado"
        )
    
    # Solo el autor o un administrador puede eliminar
    if db_foro.matricula != current_user.matricula and current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este tema del foro"
        )
    
    try:
        db.delete(db_foro)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el tema del foro porque tiene registros asociados"
        )

@router.post("/{foro_id}/reacciones", status_code=status.HTTP_201_CREATED)
def create_reaccion(
    foro_id: int,
    tipo: TipoReaccionEnum,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Añade o actualiza una reacción (like/dislike) a un tema del foro.
    """
    db_foro = db.query(Foro).filter(Foro.id == foro_id).first()
    if db_foro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tema del foro no encontrado"
        )
    
    # Verificar si ya existe una reacción de este usuario
    db_reaccion = db.query(ReaccionForo).filter(
        ReaccionForo.foro_id == foro_id,
        ReaccionForo.matricula == current_user.matricula
    ).first()
    
    if db_reaccion:
        # Si la reacción es la misma, eliminarla (toggle)
        if db_reaccion.tipo == tipo:
            # Actualizar contadores
            if tipo == TipoReaccionEnum.like:
                db_foro.likes -= 1
            else:
                db_foro.dislikes -= 1
            
            db.delete(db_reaccion)
        else:
            # Cambiar el tipo de reacción
            old_tipo = db_reaccion.tipo
            db_reaccion.tipo = tipo
            
            # Actualizar contadores
            if old_tipo == TipoReaccionEnum.like:
                db_foro.likes -= 1
                db_foro.dislikes += 1
            else:
                db_foro.likes += 1
                db_foro.dislikes -= 1
    else:
        # Crear nueva reacción
        db_reaccion = ReaccionForo(
            foro_id=foro_id,
            matricula=current_user.matricula,
            tipo=tipo
        )
        db.add(db_reaccion)
        
        # Actualizar contadores
        if tipo == TipoReaccionEnum.like:
            db_foro.likes += 1
        else:
            db_foro.dislikes += 1
    
    try:
        db.commit()
        return {"message": "Reacción registrada correctamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al registrar la reacción."
        )