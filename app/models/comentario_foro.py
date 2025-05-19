from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class ComentarioForo(Base):
    __tablename__ = "comentario_foro"

    id = Column(Integer, primary_key=True, index=True)
    foro_id = Column(Integer, ForeignKey("foro.id", ondelete="CASCADE"), nullable=False)
    matricula = Column(String(7), ForeignKey("usuario.matricula", ondelete="CASCADE"), nullable=False)
    comentario = Column(Text, nullable=False)
    fecha_comentario = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    foro = relationship("Foro", back_populates="comentarios")
    usuario = relationship("Usuario", backref="comentarios_foro")