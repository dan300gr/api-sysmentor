from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models.opcion import Opcion
from ..schemas.opcion import OpcionUpdate, Opcion as OpcionSchema
from ..utils.security import get_current_active_user, get_admin_user
from ..models.usuario import Usuario

router = APIRouter()

@router.get("/{opcion_id}", response_model=OpcionSchema)
def read_opcion(
    opcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene una opción por su ID.
    """
    db_opcion = db.query(Opcion).filter(Opcion.id == opcion_id).first()
    if db_opcion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opción no encontrada"
        )
    return db_opcion

@router.put("/{opcion_id}", response_model=OpcionSchema)
def update_opcion(
    opcion_id: int,
    opcion: OpcionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Actualiza una opción existente (solo administradores).
    """
    db_opcion = db.query(Opcion).filter(Opcion.id == opcion_id).first()
    if db_opcion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opción no encontrada"
        )
    
    update_data = opcion.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_opcion, key, value)
    
    try:
        db.commit()
        db.refresh(db_opcion)
        return db_opcion
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar la opción."
        )

@router.delete("/{opcion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opcion(
    opcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Elimina una opción (solo administradores).
    """
    db_opcion = db.query(Opcion).filter(Opcion.id == opcion_id).first()
    if db_opcion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opción no encontrada"
        )
    
    try:
        db.delete(db_opcion)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al eliminar la opción."
        )