import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class MensajeChatbot(Base):
    __tablename__ = "mensaje_chatbot"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matricula = Column(String(7), ForeignKey("usuario.matricula", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(36), nullable=False, default=lambda: str(uuid.uuid4()))
    mensaje = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    fecha = Column(DateTime, default=func.now())
    contexto = Column(Text, nullable=True)  # Contexto textual de la conversación
    metadatos = Column(JSON, nullable=True)  # Metadatos adicionales como temas, sentimiento, etc.
    
    # Relaciones
    usuario = relationship("Usuario", backref="mensajes_chatbot")

class ConversacionChatbot(Base):
    __tablename__ = "conversacion_chatbot"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False)
    matricula = Column(String(7), ForeignKey("usuario.matricula", ondelete="SET NULL"), nullable=True)
    titulo = Column(String(255), nullable=True)  # Título generado para la conversación
    fecha_inicio = Column(DateTime, default=func.now())
    fecha_ultima_actividad = Column(DateTime, default=func.now(), onupdate=func.now())
    resumen = Column(Text, nullable=True)  # Resumen de la conversación
    temas = Column(JSON, nullable=True)  # Temas principales detectados
    
    # Relaciones
    usuario = relationship("Usuario", backref="conversaciones_chatbot")