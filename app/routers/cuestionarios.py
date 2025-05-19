from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from ..database import get_db
from ..models.cuestionario import Cuestionario
from ..models.pregunta import Pregunta
from ..models.opcion import Opcion
from ..schemas.cuestionario import CuestionarioCreate, Cuestionario as CuestionarioSchema, CuestionarioUpdate
from ..schemas.pregunta import PreguntaCreate, Pregunta as PreguntaSchema
from ..utils.security import get_current_active_user, get_admin_user
from ..models.usuario import Usuario

router = APIRouter()

@router.post("/", response_model=CuestionarioSchema, status_code=status.HTTP_201_CREATED)
def create_cuestionario(
    cuestionario: CuestionarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Crea un nuevo cuestionario (solo administradores).
    """
    db_cuestionario = Cuestionario(
        semana_tema_id=cuestionario.semana_tema_id,
        titulo=cuestionario.titulo
    )
    
    try:
        db.add(db_cuestionario)
        db.commit()
        db.refresh(db_cuestionario)
        return db_cuestionario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el cuestionario. Verifica que la semana/tema exista."
        )

@router.get("/", response_model=List[CuestionarioSchema])
def read_cuestionarios(
    skip: int = 0, 
    limit: int = 100, 
    semana_tema_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene la lista de cuestionarios con filtros opcionales.
    """
    query = db.query(Cuestionario)
    
    if semana_tema_id:
        query = query.filter(Cuestionario.semana_tema_id == semana_tema_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{cuestionario_id}", response_model=CuestionarioSchema)
def read_cuestionario(
    cuestionario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un cuestionario por su ID.
    """
    db_cuestionario = db.query(Cuestionario).filter(Cuestionario.id == cuestionario_id).first()
    if db_cuestionario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuestionario no encontrado"
        )
    return db_cuestionario

@router.put("/{cuestionario_id}", response_model=CuestionarioSchema)
def update_cuestionario(
    cuestionario_id: int,
    cuestionario: CuestionarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Actualiza un cuestionario existente (solo administradores).
    """
    db_cuestionario = db.query(Cuestionario).filter(Cuestionario.id == cuestionario_id).first()
    if db_cuestionario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuestionario no encontrado"
        )
    
    update_data = cuestionario.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cuestionario, key, value)
    
    try:
        db.commit()
        db.refresh(db_cuestionario)
        return db_cuestionario
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el cuestionario. Verifica que la semana/tema exista."
        )

@router.delete("/{cuestionario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cuestionario(
    cuestionario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Elimina un cuestionario (solo administradores).
    """
    db_cuestionario = db.query(Cuestionario).filter(Cuestionario.id == cuestionario_id).first()
    if db_cuestionario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuestionario no encontrado"
        )
    
    try:
        db.delete(db_cuestionario)
        db.commit()
        return None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el cuestionario porque tiene registros asociados"
        )

@router.post("/{cuestionario_id}/preguntas", response_model=PreguntaSchema)
def create_pregunta(
    cuestionario_id: int,
    pregunta: PreguntaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_admin_user)
):
    """
    Añade una pregunta a un cuestionario (solo administradores).
    """
    db_cuestionario = db.query(Cuestionario).filter(Cuestionario.id == cuestionario_id).first()
    if db_cuestionario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuestionario no encontrado"
        )
    
    db_pregunta = Pregunta(
        cuestionario_id=cuestionario_id,
        texto=pregunta.texto
    )
    
    try:
        db.add(db_pregunta)
        db.commit()
        db.refresh(db_pregunta)
        
        # Añadir opciones si se proporcionaron
        for opcion_data in pregunta.opciones:
            db_opcion = Opcion(
                pregunta_id=db_pregunta.id,
                texto=opcion_data.texto,
                es_correcta=opcion_data.es_correcta
            )
            db.add(db_opcion)
        
        db.commit()
        db.refresh(db_pregunta)
        return db_pregunta
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la pregunta."
        )

@router.get("/{cuestionario_id}/preguntas", response_model=List[PreguntaSchema])
def read_preguntas_by_cuestionario(
    cuestionario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene todas las preguntas de un cuestionario.
    """
    db_cuestionario = db.query(Cuestionario).filter(Cuestionario.id == cuestionario_id).first()
    if db_cuestionario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuestionario no encontrado"
        )
    
    preguntas = db.query(Pregunta).filter(Pregunta.cuestionario_id == cuestionario_id).all()
    return preguntas