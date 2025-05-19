from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class SemanaTema(Base):
    __tablename__ = "semana_tema"

    id = Column(Integer, primary_key=True, index=True)
    materia_id = Column(Integer, ForeignKey("materia.id", ondelete="CASCADE"), nullable=False)
    numero_semana = Column(Integer, nullable=False)
    tema = Column(String(255), nullable=False)

    # Relaciones
    materia = relationship("Materia", back_populates="semanas_temas")
    recursos = relationship("Recurso", back_populates="semana_tema", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Restricción única para materia_id y numero_semana
        {'sqlite_autoincrement': True},
    )