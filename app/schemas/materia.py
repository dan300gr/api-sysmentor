from pydantic import BaseModel, Field
from typing import Optional, List

class MateriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None
    semestre_id: int

class MateriaCreate(MateriaBase):
    pass

class MateriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = None
    semestre_id: Optional[int] = None

class MateriaInDB(MateriaBase):
    id: int
    
    class Config:
        orm_mode = True

class Materia(MateriaInDB):
    pass