from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ComentarioForoBase(BaseModel):
    foro_id: int
    matricula: str
    comentario: str = Field(..., min_length=1)

class ComentarioForoCreate(ComentarioForoBase):
    pass

class ComentarioForoUpdate(BaseModel):
    comentario: Optional[str] = Field(None, min_length=1)

class ComentarioForoInDB(ComentarioForoBase):
    id: int
    fecha_comentario: datetime
    
    class Config:
        orm_mode = True

class ComentarioForo(ComentarioForoInDB):
    pass