from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class MensajeChatbotBase(BaseModel):
    matricula: Optional[str] = None
    session_id: Optional[str] = None
    mensaje: str
    respuesta: Optional[str] = None
    contexto: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None  # Cambiado de metadata a metadatos

class MensajeChatbotCreate(BaseModel):
    matricula: Optional[str] = None
    session_id: Optional[str] = None
    mensaje: str
    metadatos: Optional[Dict[str, Any]] = None  # Cambiado de metadata a metadatos

class MensajeChatbotUpdate(BaseModel):
    respuesta: Optional[str] = None
    contexto: Optional[str] = None
    metadatos: Optional[Dict[str, Any]] = None  # Cambiado de metadata a metadatos

class MensajeChatbot(MensajeChatbotBase):
    id: int
    fecha: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Importamos Usuario aquí para evitar referencias circulares
from app.schemas.usuario import Usuario

class MensajeChatbotWithUsuario(MensajeChatbot):
    usuario: Optional[Usuario] = None
    
    model_config = ConfigDict(from_attributes=True)

# Esquemas para la gestión de conversaciones
class ConversacionBase(BaseModel):
    session_id: str
    matricula: Optional[str] = None
    titulo: Optional[str] = None
    resumen: Optional[str] = None
    temas: Optional[List[str]] = None

class ConversacionCreate(ConversacionBase):
    pass

class ConversacionUpdate(BaseModel):
    titulo: Optional[str] = None
    resumen: Optional[str] = None
    temas: Optional[List[str]] = None

class Conversacion(ConversacionBase):
    id: int
    fecha_inicio: datetime
    fecha_ultima_actividad: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConversacionWithMensajes(Conversacion):
    mensajes: List[MensajeChatbot] = []
    
    model_config = ConfigDict(from_attributes=True)

# Opcional: Esquema para respuestas con metadatos
class ChatbotResponse(BaseModel):
    respuesta: str
    metadatos: Optional[Dict[str, Any]] = None  # Cambiado de metadata a metadatos