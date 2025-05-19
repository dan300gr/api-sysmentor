from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from ..database import get_db
from ..models.pregunta import Pregunta
from ..models.opcion import Opcion
from ..schemas.pregunta import PreguntaUpdate, Pregunta as PreguntaSchema
from ..schemas.opcion import OpcionCreate, Opcion as OpcionSchema, OpcionUpdate
from ..utils.security import get_current_active_user, get_admin_user
from ..models.usuario import Usuario

router = APIRouter()

@router.get("/{pregunta_id}", response_model=PreguntaSchema)
def read_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene una pregunta por su ID.
    """
    db_pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
    if db_pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    return db_pregunta

@router.put("/{pregunta_id}", response_model=PreguntaSchema)
def update_pregunta(
    pregunta_id: int,
    pregunta: PreguntaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Actualiza una pregunta existente (solo administradores).
    """
    db_pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
    if db_pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    update_data = pregunta.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pregunta, key, value)
    
    try:
        db.commit()
        db.refresh(db_pregunta)
        return db_pregunta
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar la pregunta."
        )

@router.delete("/{pregunta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Elimina una pregunta (solo administradores).
    """
    db_pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
    if db_pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    try:
        db.delete(db_pregunta)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la pregunta porque tiene registros asociados"
        )

@router.post("/{pregunta_id}/opciones", response_model=OpcionSchema)
def create_opcion(
    pregunta_id: int,
    opcion: OpcionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Añade una opción a una pregunta (solo administradores).
    """
    db_pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
    if db_pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    db_opcion = Opcion(
        pregunta_id=pregunta_id,
        texto=opcion.texto,
        es_correcta=opcion.es_correcta
    )
    
    try:
        db.add(db_opcion)
        db.commit()
        db.refresh(db_opcion)
        return db_opcion
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la opción."
        )

@router.get("/{pregunta_id}/opciones", response_model=List[OpcionSchema])
def read_opciones_by_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene todas las opciones de una pregunta.
    """
    db_pregunta = db.query(Pregunta).filter(Pregunta.id == pregunta_id).first()
    if db_pregunta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pregunta no encontrada"
        )
    
    opciones = db.query(Opcion).filter(Opcion.pregunta_id == pregunta_id).all()
    return opciones