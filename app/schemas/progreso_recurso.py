from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal

class EstadoProgresoEnum(str, Enum):
    no_iniciado = "no_iniciado"
    en_progreso = "en_progreso"
    completado = "completado"

class ProgresoRecursoBase(BaseModel):
    matricula: str
    recurso_id: int
    estado: EstadoProgresoEnum = EstadoProgresoEnum.no_iniciado
    fecha_inicio: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    calificacion: Optional[Decimal] = Field(None, ge=0, le=100)
    comentarios: Optional[str] = None
    
    @validator('calificacion')
    def validate_calificacion(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('La calificación debe estar entre 0 y 100')
        return v

class ProgresoRecursoCreate(ProgresoRecursoBase):
    pass

class ProgresoRecursoUpdate(BaseModel):
    estado: Optional[EstadoProgresoEnum] = None
    fecha_inicio: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    calificacion: Optional[Decimal] = Field(None, ge=0, le=100)
    comentarios: Optional[str] = None

class ProgresoRecursoInDB(ProgresoRecursoBase):
    id: int
    
    class Config:
        orm_mode = True

class ProgresoRecurso(ProgresoRecursoInDB):
    pass