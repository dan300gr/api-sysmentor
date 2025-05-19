from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base

class TipoReaccionEnum(str, enum.Enum):
    like = "like"
    dislike = "dislike"

class ReaccionForo(Base):
    __tablename__ = "reaccion_foro"

    id = Column(Integer, primary_key=True, index=True)
    foro_id = Column(Integer, ForeignKey("foro.id", ondelete="CASCADE"), nullable=False)
    matricula = Column(String(7), ForeignKey("usuario.matricula", ondelete="CASCADE"), nullable=False)
    tipo = Column(Enum(TipoReaccionEnum), nullable=False)
    fecha_reaccion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    foro = relationship("Foro", back_populates="reacciones")
    usuario = relationship("Usuario", backref="reacciones_foro")
    
    __table_args__ = (
        # Restricción única para foro_id y matricula
        {'sqlite_autoincrement': True},
    )