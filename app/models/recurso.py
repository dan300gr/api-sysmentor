from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from ..database import Base

class TipoRecursoEnum(str, enum.Enum):
    lectura = "lectura"
    video = "video"
    cuestionario = "cuestionario"

class Recurso(Base):
    __tablename__ = "recurso"

    id = Column(Integer, primary_key=True, index=True)
    semana_tema_id = Column(Integer, ForeignKey("semana_tema.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(Enum(TipoRecursoEnum), nullable=False)
    contenido_lectura = Column(Text)
    url_video = Column(String(255))
    cuestionario_id = Column(Integer, ForeignKey("cuestionario.id", ondelete="CASCADE"), nullable=True)

    # Relaciones
    semana_tema = relationship("SemanaTema", back_populates="recursos")
    cuestionario = relationship("Cuestionario", back_populates="recurso")
    progresos = relationship("ProgresoRecurso", back_populates="recurso", cascade="all, delete-orphan")