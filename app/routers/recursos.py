from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_db
from ..models.recurso import Recurso
from ..schemas.recurso import RecursoCreate, Recurso as RecursoSchema, RecursoUpdate, TipoRecursoEnum
from ..utils.security import get_current_active_user, get_admin_user
from ..models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=RecursoSchema, status_code=status.HTTP_201_CREATED)
def create_recurso(
    recurso: RecursoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Crea un nuevo recurso (solo administradores).
    """
    db_recurso = Recurso(
        semana_tema_id=recurso.semana_tema_id,
        tipo=recurso.tipo,
        contenido_lectura=recurso.contenido_lectura,
        url_video=recurso.url_video,
        cuestionario_id=recurso.cuestionario_id
    )
    
    try:
        db.add(db_recurso)
        db.commit()
        db.refresh(db_recurso)
        return db_recurso
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el recurso. Verifica que la semana/tema y el cuestionario (si aplica) existan."
        )

@router.get("/", response_model=List[RecursoSchema])
def read_recursos(
    skip: int = 0, 
    limit: int = 100, 
    semana_tema_id: Optional[int] = None,
    tipo: Optional[TipoRecursoEnum] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene la lista de recursos con filtros opcionales.
    """
    query = db.query(Recurso)
    
    if semana_tema_id:
        query = query.filter(Recurso.semana_tema_id == semana_tema_id)
    
    if tipo:
        query = query.filter(Recurso.tipo == tipo)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{recurso_id}", response_model=RecursoSchema)
def read_recurso(
    recurso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un recurso por su ID.
    """
    db_recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
    if db_recurso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    return db_recurso

@router.put("/{recurso_id}", response_model=RecursoSchema)
def update_recurso(
    recurso_id: int,
    recurso: RecursoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Actualiza un recurso existente (solo administradores).
    """
    db_recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
    if db_recurso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    update_data = recurso.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_recurso, key, value)
    
    try:
        db.commit()
        db.refresh(db_recurso)
        return db_recurso
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el recurso. Verifica que la semana/tema y el cuestionario (si aplica) existan."
        )

@router.delete("/{recurso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurso(
    recurso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Elimina un recurso (solo administradores).
    """
    db_recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
    if db_recurso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    try:
        db.delete(db_recurso)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el recurso porque tiene registros asociados"
        )