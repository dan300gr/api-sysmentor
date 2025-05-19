from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base

class Foro(Base):
    __tablename__ = "foro"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(7), ForeignKey("usuario.matricula", ondelete="CASCADE"), nullable=False)
    materia_id = Column(Integer, ForeignKey("materia.id", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(255), nullable=False)
    contenido = Column(Text, nullable=False)
    fecha_publicacion = Column(DateTime(timezone=True), server_default=func.now())
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)

    # Relaciones
    usuario = relationship("Usuario", backref="foros")
    materia = relationship("Materia", back_populates="foros")
    comentarios = relationship("ComentarioForo", back_populates="foro", cascade="all, delete-orphan")
    reacciones = relationship("ReaccionForo", back_populates="foro", cascade="all, delete-orphan")