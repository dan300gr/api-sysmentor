from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_db
from ..models.semana_tema import SemanaTema
from ..schemas.semana_tema import SemanaTemaCreate, SemanaTema as SemanaTemaSchema, SemanaTemaUpdate
from ..utils.security import get_current_active_user, get_admin_user
from ..models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=SemanaTemaSchema, status_code=status.HTTP_201_CREATED)
def create_semana_tema(
    semana_tema: SemanaTemaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Crea una nueva semana/tema (solo administradores).
    """
    db_semana_tema = SemanaTema(
        materia_id=semana_tema.materia_id,
        numero_semana=semana_tema.numero_semana,
        tema=semana_tema.tema
    )
    
    try:
        db.add(db_semana_tema)
        db.commit()
        db.refresh(db_semana_tema)
        return db_semana_tema
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la semana/tema. Verifica que la materia exista y que no haya duplicados."
        )

@router.get("/", response_model=List[SemanaTemaSchema])
def read_semanas_temas(
    skip: int = 0, 
    limit: int = 100, 
    materia_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene la lista de semanas/temas con filtros opcionales.
    """
    query = db.query(SemanaTema)
    
    if materia_id:
        query = query.filter(SemanaTema.materia_id == materia_id)
    
    return query.order_by(SemanaTema.materia_id, SemanaTema.numero_semana).offset(skip).limit(limit).all()

@router.get("/{semana_tema_id}", response_model=SemanaTemaSchema)
def read_semana_tema(
    semana_tema_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene una semana/tema por su ID.
    """
    db_semana_tema = db.query(SemanaTema).filter(SemanaTema.id == semana_tema_id).first()
    if db_semana_tema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semana/tema no encontrado"
        )
    return db_semana_tema

@router.put("/{semana_tema_id}", response_model=SemanaTemaSchema)
def update_semana_tema(
    semana_tema_id: int,
    semana_tema: SemanaTemaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Actualiza una semana/tema existente (solo administradores).
    """
    db_semana_tema = db.query(SemanaTema).filter(SemanaTema.id == semana_tema_id).first()
    if db_semana_tema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semana/tema no encontrado"
        )
    
    update_data = semana_tema.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_semana_tema, key, value)
    
    try:
        db.commit()
        db.refresh(db_semana_tema)
        return db_semana_tema
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar la semana/tema. Verifica que no haya duplicados."
        )

@router.delete("/{semana_tema_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_semana_tema(
    semana_tema_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Elimina una semana/tema (solo administradores).
    """
    db_semana_tema = db.query(SemanaTema).filter(SemanaTema.id == semana_tema_id).first()
    if db_semana_tema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semana/tema no encontrado"
        )
    
    try:
        db.delete(db_semana_tema)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la semana/tema porque tiene registros asociados"
        )

@router.get("/{semana_tema_id}/recursos", response_model=List)
def read_recursos_by_semana_tema(
    semana_tema_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene todos los recursos de una semana/tema.
    """
    from ..models.recurso import Recurso
    from ..schemas.recurso import Recurso as RecursoSchema
    
    db_semana_tema = db.query(SemanaTema).filter(SemanaTema.id == semana_tema_id).first()
    if db_semana_tema is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semana/tema no encontrado"
        )
    
    recursos = db.query(Recurso).filter(Recurso.semana_tema_id == semana_tema_id).all()
    return recursos