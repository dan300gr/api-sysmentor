from pydantic import BaseModel, Field
from typing import Optional, List

class CuestionarioBase(BaseModel):
    semana_tema_id: int
    titulo: str = Field(..., min_length=2, max_length=255)

class CuestionarioCreate(CuestionarioBase):
    pass

class CuestionarioUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=2, max_length=255)
    semana_tema_id: Optional[int] = None

class CuestionarioInDB(CuestionarioBase):
    id: int
    
    class Config:
        orm_mode = True

class Cuestionario(CuestionarioInDB):
    pass