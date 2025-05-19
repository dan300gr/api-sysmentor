from pydantic import BaseModel, Field
from typing import Optional, List

class SemestreBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)

class SemestreCreate(SemestreBase):
    pass

class SemestreUpdate(SemestreBase):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)

class SemestreInDB(SemestreBase):
    id: int
    
    class Config:
        orm_mode = True

class Semestre(SemestreInDB):
    pass