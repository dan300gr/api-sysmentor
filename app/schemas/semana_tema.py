from pydantic import BaseModel, Field, validator
from typing import Optional, List

class SemanaTemaBase(BaseModel):
    materia_id: int
    numero_semana: int = Field(..., gt=0)
    tema: str = Field(..., min_length=2, max_length=255)
    
    @validator('numero_semana')
    def validate_numero_semana(cls, v):
        if v <= 0:
            raise ValueError('El número de semana debe ser mayor que 0')
        return v

class SemanaTemaCreate(SemanaTemaBase):
    pass

class SemanaTemaUpdate(BaseModel):
    numero_semana: Optional[int] = Field(None, gt=0)
    tema: Optional[str] = Field(None, min_length=2, max_length=255)

class SemanaTemaInDB(SemanaTemaBase):
    id: int
    
    class Config:
        orm_mode = True

class SemanaTema(SemanaTemaInDB):
    pass