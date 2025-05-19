from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from ..database import get_db
from ..models.comentario_foro import ComentarioForo
from ..schemas.comentario_foro import ComentarioForoCreate, ComentarioForo as ComentarioForoSchema, ComentarioForoUpdate
from ..utils.security import get_current_active_user
from ..models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=ComentarioForoSchema, status_code=status.HTTP_201_CREATED)
def create_comentario_foro(
    comentario: ComentarioForoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crea un nuevo comentario en un tema del foro.
    """
    db_comentario = ComentarioForo(
        foro_id=comentario.foro_id,
        matricula=current_user.matricula,
        comentario=comentario.comentario
    )
    
    try:
        db.add(db_comentario)
        db.commit()
        db.refresh(db_comentario)
        return db_comentario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el comentario. Verifica que el tema del foro exista."
        )

@router.get("/foro/{foro_id}", response_model=List[ComentarioForoSchema])
def read_comentarios_by_foro(
    foro_id: int,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene todos los comentarios de un tema del foro.
    """
    comentarios = db.query(ComentarioForo).filter(
        ComentarioForo.foro_id == foro_id
    ).order_by(ComentarioForo.fecha_comentario).offset(skip).limit(limit).all()
    
    return comentarios

@router.get("/{comentario_id}", response_model=ComentarioForoSchema)
def read_comentario_foro(
    comentario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un comentario por su ID.
    """
    db_comentario = db.query(ComentarioForo).filter(ComentarioForo.id == comentario_id).first()
    if db_comentario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado"
        )
    return db_comentario

@router.put("/{comentario_id}", response_model=ComentarioForoSchema)
def update_comentario_foro(
    comentario_id: int,
    comentario: ComentarioForoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza un comentario existente.
    """
    db_comentario = db.query(ComentarioForo).filter(ComentarioForo.id == comentario_id).first()
    if db_comentario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado"
        )
    
    # Solo el autor o un administrador puede actualizar
    if db_comentario.matricula != current_user.matricula and current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este comentario"
        )
    
    update_data = comentario.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_comentario, key, value)
    
    try:
        db.commit()
        db.refresh(db_comentario)
        return db_comentario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el comentario."
        )

@router.delete("/{comentario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comentario_foro(
    comentario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina un comentario.
    """
    db_comentario = db.query(ComentarioForo).filter(ComentarioForo.id == comentario_id).first()
    if db_comentario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado"
        )
    
    # Solo el autor o un administrador puede eliminar
    if db_comentario.matricula != current_user.matricula and current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este comentario"
        )
    
    db.delete(db_comentario)
    db.commit()
    return None