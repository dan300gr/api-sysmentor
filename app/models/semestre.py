from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base

class Semestre(Base):
    __tablename__ = "semestre"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="semestre")
    materias = relationship("Materia", back_populates="semestre", cascade="all, delete-orphan")