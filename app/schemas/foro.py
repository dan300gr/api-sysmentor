from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ForoBase(BaseModel):
    matricula: str
    materia_id: int
    titulo: str = Field(..., min_length=5, max_length=255)
    contenido: str = Field(..., min_length=10)

class ForoCreate(ForoBase):
    pass

class ForoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5, max_length=255)
    contenido: Optional[str] = Field(None, min_length=10)

class ForoInDB(ForoBase):
    id: int
    fecha_publicacion: datetime
    likes: int
    dislikes: int
    
    class Config:
        orm_mode = True

class Foro(ForoInDB):
    pass