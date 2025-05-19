from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base

class EstadoProgresoEnum(str, enum.Enum):
    no_iniciado = "no_iniciado"
    en_progreso = "en_progreso"
    completado = "completado"

class ProgresoRecurso(Base):
    __tablename__ = "progreso_recurso"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(7), ForeignKey("usuario.matricula", ondelete="CASCADE"), nullable=False)
    recurso_id = Column(Integer, ForeignKey("recurso.id", ondelete="CASCADE"), nullable=False)
    estado = Column(Enum(EstadoProgresoEnum), default=EstadoProgresoEnum.no_iniciado, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True))
    fecha_finalizacion = Column(DateTime(timezone=True))
    calificacion = Column(Numeric(5, 2))
    comentarios = Column(Text)

    # Relaciones
    usuario = relationship("Usuario", backref="progresos_recursos")
    recurso = relationship("Recurso", back_populates="progresos")
    
    __table_args__ = (
        # Restricción única para matricula y recurso_id
        {'sqlite_autoincrement': True},
    )