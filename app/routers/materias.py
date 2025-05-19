from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_db
from ..models.materia import Materia
from ..schemas.materia import MateriaCreate, Materia as MateriaSchema, MateriaUpdate
from ..utils.security import get_current_active_user, get_admin_user
from ..models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=MateriaSchema, status_code=status.HTTP_201_CREATED)
def create_materia(
    materia: MateriaCreate,
    current_user: Usuario = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva materia (solo administradores).
    """
    db_materia = Materia(
        nombre=materia.nombre,
        descripcion=materia.descripcion,
        semestre_id=materia.semestre_id
    )
    
    try:
        db.add(db_materia)
        db.commit()
        db.refresh(db_materia)
        return db_materia
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la materia. Verifica que el semestre exista."
        )

@router.get("/", response_model=List[MateriaSchema])
def read_materias(
    skip: int = 0, 
    limit: int = 100, 
    semestre_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene la lista de materias con filtros opcionales.
    """
    query = db.query(Materia)
    
    if semestre_id:
        query = query.filter(Materia.semestre_id == semestre_id)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            (Materia.nombre.like(search)) |
            (Materia.descripcion.like(search))
        )
    
    return query.offset(skip).limit(limit).all()

@router.get("/{materia_id}", response_model=MateriaSchema)
def read_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene una materia por su ID.
    """
    db_materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    return db_materia

@router.put("/{materia_id}", response_model=MateriaSchema)
def update_materia(
    materia_id: int,
    materia: MateriaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Actualiza una materia existente (solo administradores).
    """
    db_materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    
    update_data = materia.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_materia, key, value)
    
    try:
        db.commit()
        db.refresh(db_materia)
        return db_materia
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar la materia. Verifica que el semestre exista."
        )

@router.delete("/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Elimina una materia (solo administradores).
    """
    db_materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    
    try:
        db.delete(db_materia)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la materia porque tiene registros asociados"
        )

@router.get("/{materia_id}/semanas", response_model=List)
def read_semanas_by_materia(
    materia_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene todas las semanas/temas de una materia.
    """
    from ..models.semana_tema import SemanaTema
    from ..schemas.semana_tema import SemanaTema as SemanaTemaSchema
    
    db_materia = db.query(Materia).filter(Materia.id == materia_id).first()
    if db_materia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    
    semanas = db.query(SemanaTema).filter(SemanaTema.materia_id == materia_id).all()
    return semanas