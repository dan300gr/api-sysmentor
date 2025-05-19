from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base

class RolEnum(str, enum.Enum):
    estudiante = "estudiante"
    admin = "admin"

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(7), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100), nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolEnum), default=RolEnum.estudiante)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())
    correo = Column(String(100), unique=True, index=True, nullable=False)
    semestre_id = Column(Integer, ForeignKey("semestre.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)

    # Relación con Semestre
    semestre = relationship("Semestre", back_populates="usuarios")
    
    # Método para convertir matrícula a minúsculas
    def __setattr__(self, key, value):
        if key == 'matricula' and value is not None:
            value = value.lower()
        super().__setattr__(key, value)