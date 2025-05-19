from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class Opcion(Base):
    __tablename__ = "opcion"

    id = Column(Integer, primary_key=True, index=True)
    pregunta_id = Column(Integer, ForeignKey("pregunta.id", ondelete="CASCADE"), nullable=False)
    texto = Column(String(255), nullable=False)
    es_correcta = Column(Boolean, nullable=False)

    # Relaciones
    pregunta = relationship("Pregunta", back_populates="opciones")