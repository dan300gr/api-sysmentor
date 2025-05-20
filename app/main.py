from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import get_db
from .routers import (
    usuarios, 
    semestres, 
    materias, 
    semanas_temas, 
    cuestionarios, 
    preguntas, 
    opciones, 
    recursos, 
    progreso_recursos, 
    foros, 
    comentarios_foro,  
    mensajes_chatbot
)

app = FastAPI(
    title="SysMentor API",
    description="API para la plataforma académica SysMentor",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://api-sysmentor.onrender.com", "https://sysmentor-frontend.vercel.app/"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(semestres.router, prefix="/api/semestres", tags=["Semestres"])
app.include_router(materias.router, prefix="/api/materias", tags=["Materias"])
app.include_router(semanas_temas.router, prefix="/api/semanas-temas", tags=["Semanas y Temas"])
app.include_router(cuestionarios.router, prefix="/api/cuestionarios", tags=["Cuestionarios"])
app.include_router(preguntas.router, prefix="/api/preguntas", tags=["Preguntas"])
app.include_router(opciones.router, prefix="/api/opciones", tags=["Opciones"])
app.include_router(recursos.router, prefix="/api/recursos", tags=["Recursos"])
app.include_router(progreso_recursos.router, prefix="/api/progreso-recursos", tags=["Progreso de Recursos"])
app.include_router(foros.router, prefix="/api/foros", tags=["Foros"])
app.include_router(comentarios_foro.router, prefix="/api/comentarios-foro", tags=["Comentarios de Foros"])
app.include_router(mensajes_chatbot.router, prefix="/api/mensajes", tags=["Mensajes de Chatbot"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de SysMentor"}

@app.get("/health")
def health_check():
    return {"status": "ok"}