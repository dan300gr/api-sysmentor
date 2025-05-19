from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoReaccionEnum(str, Enum):
    like = "like"
    dislike = "dislike"

class ReaccionForoBase(BaseModel):
    foro_id: int
    matricula: str
    tipo: TipoReaccionEnum

class ReaccionForoCreate(ReaccionForoBase):
    pass

class ReaccionForoUpdate(BaseModel):
    tipo: Optional[TipoReaccionEnum] = None

class ReaccionForoInDB(ReaccionForoBase):
    id: int
    fecha_reaccion: datetime
    
    class Config:
        orm_mode = True

class ReaccionForo(ReaccionForoInDB):
    pass