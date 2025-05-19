from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class Materia(Base):
    __tablename__ = "materia"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    semestre_id = Column(Integer, ForeignKey("semestre.id", ondelete="CASCADE"), nullable=False)

    # Relaciones
    semestre = relationship("Semestre", back_populates="materias")
    semanas_temas = relationship("SemanaTema", back_populates="materia", cascade="all, delete-orphan")
    foros = relationship("Foro", back_populates="materia", cascade="all, delete-orphan")