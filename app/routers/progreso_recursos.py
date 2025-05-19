from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.progreso_recurso import ProgresoRecurso
from ..schemas.progreso_recurso import ProgresoRecursoCreate, ProgresoRecurso as ProgresoRecursoSchema, ProgresoRecursoUpdate, EstadoProgresoEnum
from ..utils.security import get_current_active_user
from ..models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=ProgresoRecursoSchema, status_code=status.HTTP_201_CREATED)
def create_progreso_recurso(
    progreso: ProgresoRecursoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crea o actualiza el progreso de un recurso para el usuario actual.
    """
    # Verificar si ya existe un progreso para este usuario y recurso
    db_progreso = db.query(ProgresoRecurso).filter(
        ProgresoRecurso.matricula == current_user.matricula,
        ProgresoRecurso.recurso_id == progreso.recurso_id
    ).first()
    
    if db_progreso:
        # Actualizar el progreso existente
        for key, value in progreso.dict().items():
            setattr(db_progreso, key, value)
    else:
        # Crear un nuevo progreso
        db_progreso = ProgresoRecurso(
            matricula=current_user.matricula,
            recurso_id=progreso.recurso_id,
            estado=progreso.estado,
            fecha_inicio=progreso.fecha_inicio or datetime.now(),
            fecha_finalizacion=progreso.fecha_finalizacion,
            calificacion=progreso.calificacion,
            comentarios=progreso.comentarios
        )
        db.add(db_progreso)
    
    try:
        db.commit()
        db.refresh(db_progreso)
        return db_progreso
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al registrar el progreso. Verifica que el recurso exista."
        )

@router.get("/", response_model=List[ProgresoRecursoSchema])
def read_progresos_recursos(
    skip: int = 0, 
    limit: int = 100, 
    recurso_id: Optional[int] = None,
    estado: Optional[EstadoProgresoEnum] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene la lista de progresos de recursos del usuario actual con filtros opcionales.
    """
    query = db.query(ProgresoRecurso).filter(ProgresoRecurso.matricula == current_user.matricula)
    
    if recurso_id:
        query = query.filter(ProgresoRecurso.recurso_id == recurso_id)
    
    if estado:
        query = query.filter(ProgresoRecurso.estado == estado)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{progreso_id}", response_model=ProgresoRecursoSchema)
def read_progreso_recurso(
    progreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un progreso de recurso por su ID.
    """
    db_progreso = db.query(ProgresoRecurso).filter(
        ProgresoRecurso.id == progreso_id,
        ProgresoRecurso.matricula == current_user.matricula
    ).first()
    
    if db_progreso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progreso de recurso no encontrado o no pertenece al usuario actual"
        )
    return db_progreso

@router.put("/{progreso_id}", response_model=ProgresoRecursoSchema)
def update_progreso_recurso(
    progreso_id: int,
    progreso: ProgresoRecursoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza un progreso de recurso existente.
    """
    db_progreso = db.query(ProgresoRecurso).filter(
        ProgresoRecurso.id == progreso_id,
        ProgresoRecurso.matricula == current_user.matricula
    ).first()
    
    if db_progreso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progreso de recurso no encontrado o no pertenece al usuario actual"
        )
    
    update_data = progreso.dict(exclude_unset=True)
    
    # Si se marca como completado y no hay fecha de finalización, establecerla
    if update_data.get("estado") == EstadoProgresoEnum.completado and not db_progreso.fecha_finalizacion:
        update_data["fecha_finalizacion"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(db_progreso, key, value)
    
    try:
        db.commit()
        db.refresh(db_progreso)
        return db_progreso
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el progreso."
        )

@router.delete("/{progreso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_progreso_recurso(
    progreso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina un progreso de recurso.
    """
    db_progreso = db.query(ProgresoRecurso).filter(
        ProgresoRecurso.id == progreso_id,
        ProgresoRecurso.matricula == current_user.matricula
    ).first()
    
    if db_progreso is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progreso de recurso no encontrado o no pertenece al usuario actual"
        )
    
    db.delete(db_progreso)
    db.commit()
    return None