from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class Cuestionario(Base):
    __tablename__ = "cuestionario"

    id = Column(Integer, primary_key=True, index=True)
    semana_tema_id = Column(Integer, ForeignKey("semana_tema.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255), nullable=False)

    # Relaciones
    semana_tema = relationship("SemanaTema")
    preguntas = relationship("Pregunta", back_populates="cuestionario", cascade="all, delete-orphan")
    recurso = relationship("Recurso", back_populates="cuestionario", uselist=False)