from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class Pregunta(Base):
    __tablename__ = "pregunta"

    id = Column(Integer, primary_key=True, index=True)
    cuestionario_id = Column(Integer, ForeignKey("cuestionario.id", ondelete="CASCADE"), nullable=False)
    texto = Column(Text, nullable=False)

    # Relaciones
    cuestionario = relationship("Cuestionario", back_populates="preguntas")
    opciones = relationship("Opcion", back_populates="pregunta", cascade="all, delete-orphan")