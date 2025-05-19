from pydantic import BaseModel, Field
from typing import Optional, List
from .opcion import OpcionCreate, Opcion

class PreguntaBase(BaseModel):
    cuestionario_id: int
    texto: str = Field(..., min_length=5)

class PreguntaCreate(PreguntaBase):
    opciones: List[OpcionCreate] = []

class PreguntaUpdate(BaseModel):
    texto: Optional[str] = Field(None, min_length=5)

class PreguntaInDB(PreguntaBase):
    id: int
    
    class Config:
        orm_mode = True

class Pregunta(PreguntaInDB):
    opciones: List[Opcion] = []