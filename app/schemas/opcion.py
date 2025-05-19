from pydantic import BaseModel, Field
from typing import Optional

class OpcionBase(BaseModel):
    pregunta_id: int
    texto: str = Field(..., min_length=1, max_length=255)
    es_correcta: bool

class OpcionCreate(BaseModel):
    texto: str = Field(..., min_length=1, max_length=255)
    es_correcta: bool

class OpcionUpdate(BaseModel):
    texto: Optional[str] = Field(None, min_length=1, max_length=255)
    es_correcta: Optional[bool] = None

class OpcionInDB(OpcionBase):
    id: int
    
    class Config:
        orm_mode = True

class Opcion(OpcionInDB):
    pass