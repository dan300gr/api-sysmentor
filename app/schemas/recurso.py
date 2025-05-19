from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from enum import Enum

class TipoRecursoEnum(str, Enum):
    lectura = "lectura"
    video = "video"
    cuestionario = "cuestionario"

class RecursoBase(BaseModel):
    semana_tema_id: int
    tipo: TipoRecursoEnum
    contenido_lectura: Optional[str] = None
    url_video: Optional[str] = None
    cuestionario_id: Optional[int] = None
    
    @validator('contenido_lectura')
    def validate_contenido_lectura(cls, v, values):
        if values.get('tipo') == TipoRecursoEnum.lectura and not v:
            raise ValueError('El contenido de lectura es obligatorio para recursos de tipo lectura')
        return v
    
    @validator('url_video')
    def validate_url_video(cls, v, values):
        if values.get('tipo') == TipoRecursoEnum.video and not v:
            raise ValueError('La URL del video es obligatoria para recursos de tipo video')
        return v
    
    @validator('cuestionario_id')
    def validate_cuestionario_id(cls, v, values):
        if values.get('tipo') == TipoRecursoEnum.cuestionario and not v:
            raise ValueError('El ID del cuestionario es obligatorio para recursos de tipo cuestionario')
        return v

class RecursoCreate(RecursoBase):
    pass

class RecursoUpdate(BaseModel):
    tipo: Optional[TipoRecursoEnum] = None
    contenido_lectura: Optional[str] = None
    url_video: Optional[str] = None
    cuestionario_id: Optional[int] = None

class RecursoInDB(RecursoBase):
    id: int
    
    class Config:
        orm_mode = True

class Recurso(RecursoInDB):
    pass