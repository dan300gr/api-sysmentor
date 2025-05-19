from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import re

from ..database import get_db
from ..models.usuario import Usuario, RolEnum
from ..schemas.usuario import UsuarioBase

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta_aqui"  # Cambia esto por una clave segura en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 365

# Configuración de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 con flujo de contraseña
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def validate_matricula(matricula: str) -> bool:
    """
    Valida que la matrícula tenga el formato correcto: 
    - Debe comenzar con 'ti' (puede ser en mayúscula o minúscula)
    - Seguido de 5 dígitos
    """
    pattern = r'^[tT][iI]\d{5}$'
    return bool(re.match(pattern, matricula))

def normalize_matricula(matricula: str) -> str:
    """
    Normaliza la matrícula convirtiéndola a minúsculas
    """
    return matricula.lower() if matricula else None

def get_user(db: Session, matricula: str):
    # Normalizar la matrícula antes de buscar
    matricula = normalize_matricula(matricula)
    return db.query(Usuario).filter(Usuario.matricula == matricula).first()

def authenticate_user(db: Session, matricula: str, password: str):
    user = get_user(db, matricula)
    if not user:
        return False
    if not verify_password(password, user.contrasena_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        matricula: str = payload.get("sub")
        if matricula is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Normalizar la matrícula antes de buscar
    matricula = normalize_matricula(matricula)
    user = get_user(db, matricula)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: Usuario = Depends(get_current_user)):
    # Eliminamos la verificación de 'activo' ya que no existe en el modelo
    return current_user

def get_admin_user(current_user: Usuario = Depends(get_current_user)):
    """
    Verifica que el usuario actual tenga rol de administrador.
    Si no es administrador, lanza una excepción HTTP 403 Forbidden.
    """
    if current_user.rol != RolEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador para esta operación",
        )
    return current_user