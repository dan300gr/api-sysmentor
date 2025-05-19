from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from ..database import get_db
from ..models.semestre import Semestre
from ..schemas.semestre import SemestreCreate, Semestre as SemestreSchema, SemestreUpdate
from ..utils.security import get_admin_user

router = APIRouter()

@router.post("/", response_model=SemestreSchema, status_code=status.HTTP_201_CREATED)
def create_semestre(
    semestre: SemestreCreate, 
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo semestre (solo administradores).
    """
    db_semestre = Semestre(nombre=semestre.nombre)
    
    try:
        db.add(db_semestre)
        db.commit()
        db.refresh(db_semestre)
        return db_semestre
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un semestre con ese nombre"
        )

@router.get("/", response_model=List[SemestreSchema])
def read_semestres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene la lista de semestres.
    """
    return db.query(Semestre).offset(skip).limit(limit).all()

@router.get("/{semestre_id}", response_model=SemestreSchema)
def read_semestre(semestre_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un semestre por su ID.
    """
    db_semestre = db.query(Semestre).filter(Semestre.id == semestre_id).first()
    if db_semestre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semestre no encontrado"
        )
    return db_semestre

@router.put("/{semestre_id}", response_model=SemestreSchema)
def update_semestre(
    semestre_id: int,
    semestre: SemestreUpdate,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza un semestre existente (solo administradores).
    """
    db_semestre = db.query(Semestre).filter(Semestre.id == semestre_id).first()
    if db_semestre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semestre no encontrado"
        )
    
    update_data = semestre.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_semestre, key, value)
    
    try:
        db.commit()
        db.refresh(db_semestre)
        return db_semestre
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un semestre con ese nombre"
        )

@router.delete("/{semestre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_semestre(
    semestre_id: int,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Elimina un semestre (solo administradores).
    """
    db_semestre = db.query(Semestre).filter(Semestre.id == semestre_id).first()
    if db_semestre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semestre no encontrado"
        )
    
    try:
        db.delete(db_semestre)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el semestre porque tiene registros asociados"
        )