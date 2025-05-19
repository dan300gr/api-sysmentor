from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
import re

from ..models.usuario import RolEnum

# Esquema base para Usuario (sin validador)
class UsuarioBase(BaseModel):
    matricula: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    correo: EmailStr
    rol: Optional[RolEnum] = RolEnum.estudiante
    semestre_id: Optional[int] = None

# Esquema para crear un Usuario (con validador)
class UsuarioCreate(BaseModel):
    matricula: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    correo: EmailStr
    contrasena: str
    rol: Optional[RolEnum] = RolEnum.estudiante
    semestre_id: Optional[int] = None

    # Validador para asegurar que la matrícula tenga el formato correcto
    @validator('matricula')
    def matricula_format(cls, v):
        pattern = r'^[tT][iI]\d{5}$'
        if not re.match(pattern, v):
            raise ValueError('La matrícula debe comenzar con "ti" seguido de 5 dígitos (ejemplo: ti43806)')
        return v.lower()  # Convertir a minúsculas

# Esquema para actualizar un Usuario
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    rol: Optional[RolEnum] = None
    semestre_id: Optional[int] = None

# Esquema para respuesta de Usuario (usado en el router actualizado)
class UsuarioResponse(UsuarioBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True  # Antes conocido como orm_mode = True

# Esquema para compatibilidad con código existente
class Usuario(UsuarioBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True  # Antes conocido como orm_mode = True

# Esquema para la base de datos (para compatibilidad)
class UsuarioInDB(Usuario):
    contrasena_hash: str

# Esquema para login de Usuario
class UsuarioLogin(BaseModel):
    matricula: str
    contrasena: str

    # Validador para asegurar que la matrícula tenga el formato correcto
    @validator('matricula')
    def matricula_format(cls, v):
        pattern = r'^[tT][iI]\d{5}$'
        if not re.match(pattern, v):
            raise ValueError('La matrícula debe comenzar con "ti" seguido de 5 dígitos (ejemplo: ti43806)')
        return v.lower()  # Convertir a minúsculas

# Esquema para token de autenticación
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    matricula: str
    nombre: str
    rol: str