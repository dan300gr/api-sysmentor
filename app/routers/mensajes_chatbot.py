from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
import logging
import traceback
from app.database import get_db
from app.models.mensaje_chatbot import MensajeChatbot as MensajeChatbotModel
from app.models.mensaje_chatbot import ConversacionChatbot as ConversacionModel
from app.models.usuario import Usuario as UsuarioModel
from app.schemas.mensaje_chatbot import (
    MensajeChatbot,
    MensajeChatbotCreate,
    MensajeChatbotUpdate,
    MensajeChatbotWithUsuario,
    Conversacion,
    ConversacionWithMensajes,
)
from app.utils.chatbot import get_chatbot_response, ChatbotException, update_conversation, get_conversation_history

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/mensajes-chatbot",
    tags=["mensajes-chatbot"],
    responses={404: {"description": "No encontrado"}},
)

# Función auxiliar para convertir objetos ORM a modelos Pydantic
def orm_to_pydantic(orm_obj, pydantic_model):
    obj_dict = {c.name: getattr(orm_obj, c.name) for c in orm_obj.__table__.columns}

    if pydantic_model == MensajeChatbotWithUsuario and hasattr(orm_obj, "usuario") and orm_obj.usuario:
        from app.schemas.usuario import Usuario
        obj_dict["usuario"] = orm_to_pydantic(orm_obj.usuario, Usuario)

    return pydantic_model(**obj_dict)

@router.post("/conversar", response_model=MensajeChatbot, status_code=status.HTTP_201_CREATED)
async def conversar_chatbot(mensaje: MensajeChatbotCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Crea un nuevo mensaje de chatbot con contexto mejorado y obtiene una respuesta de Gemini.
    """
    logger.info(f"Recibida solicitud POST /conversar con mensaje: {mensaje.dict()}")
    
    try:
        # Verificar usuario si se proporciona matrícula
        if mensaje.matricula:
            db_usuario = db.query(UsuarioModel).filter(UsuarioModel.matricula == mensaje.matricula).first()
            if not db_usuario:
                logger.warning(f"Usuario no encontrado: {mensaje.matricula}")
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar si session_id es proporcionado y gestionarlo correctamente
        session_id = mensaje.session_id if mensaje.session_id and mensaje.session_id.strip() else str(uuid.uuid4())
        logger.info(f"Usando session_id: {session_id}")
        
        # Obtener respuesta del chatbot con metadatos
        chatbot_response, metadatos = await get_chatbot_response(
            mensaje.mensaje, 
            "", 
            db, 
            matricula=mensaje.matricula, 
            session_id=session_id
        )
        
        logger.info(f"Respuesta del chatbot obtenida: {chatbot_response[:50]}...")

        # Guardar el nuevo mensaje con metadatos
        db_mensaje = MensajeChatbotModel(
            matricula=mensaje.matricula,
            session_id=session_id,
            mensaje=mensaje.mensaje,
            respuesta=chatbot_response,
            metadatos=metadatos
        )

        db.add(db_mensaje)
        db.commit()
        db.refresh(db_mensaje)
        logger.info(f"Mensaje guardado con ID: {db_mensaje.id}")
        
        # Actualizar la conversación en segundo plano
        background_tasks.add_task(
            update_conversation,
            session_id,
            mensaje.matricula,
            mensaje.mensaje,
            chatbot_response,
            db
        )

        return orm_to_pydantic(db_mensaje, MensajeChatbot)

    except ChatbotException as e:
        logger.error(f"ChatbotException en conversar_chatbot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Exception en conversar_chatbot: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.get("/conversaciones", response_model=List[Conversacion])
def get_conversaciones(matricula: Optional[str] = None, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Obtiene todas las conversaciones, opcionalmente filtradas por matrícula."""
    query = db.query(ConversacionModel)
    
    if matricula:
        query = query.filter(ConversacionModel.matricula == matricula)
    
    conversaciones = query.order_by(ConversacionModel.fecha_ultima_actividad.desc()).offset(skip).limit(limit).all()
    return [orm_to_pydantic(conv, Conversacion) for conv in conversaciones]

@router.get("/conversaciones/{session_id}", response_model=ConversacionWithMensajes)
def get_conversacion_by_id(session_id: str, db: Session = Depends(get_db)):
    """Obtiene una conversación completa con todos sus mensajes."""
    conversacion = db.query(ConversacionModel).filter(ConversacionModel.session_id == session_id).first()
    
    if not conversacion:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Obtener todos los mensajes de la conversación
    mensajes = db.query(MensajeChatbotModel).filter(
        MensajeChatbotModel.session_id == session_id
    ).order_by(MensajeChatbotModel.fecha.asc()).all()
    
    # Construir el resultado
    result = orm_to_pydantic(conversacion, Conversacion)
    result_dict = result.dict()
    result_dict["mensajes"] = [orm_to_pydantic(m, MensajeChatbot) for m in mensajes]
    
    return ConversacionWithMensajes(**result_dict)

@router.get("/", response_model=List[MensajeChatbotWithUsuario])
def read_mensajes_chatbot(skip: int = 0, limit: int = 100, matricula: str = None, session_id: str = None, db: Session = Depends(get_db)):
    """Obtiene todos los mensajes de chatbot, filtrando opcionalmente por matrícula o session_id."""
    query = db.query(MensajeChatbotModel)
    if matricula:
        query = query.filter(MensajeChatbotModel.matricula == matricula)
    if session_id:
        query = query.filter(MensajeChatbotModel.session_id == session_id)

    mensajes = query.order_by(MensajeChatbotModel.fecha.desc()).offset(skip).limit(limit).all()
    return [orm_to_pydantic(mensaje, MensajeChatbotWithUsuario) for mensaje in mensajes]

@router.get("/{mensaje_id}", response_model=MensajeChatbotWithUsuario)
def read_mensaje_chatbot(mensaje_id: int, db: Session = Depends(get_db)):
    """Obtiene un mensaje de chatbot por su ID."""
    db_mensaje = db.query(MensajeChatbotModel).filter(MensajeChatbotModel.id == mensaje_id).first()
    if db_mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

    return orm_to_pydantic(db_mensaje, MensajeChatbotWithUsuario)

@router.delete("/{mensaje_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mensaje_chatbot(mensaje_id: int, db: Session = Depends(get_db)):
    """Elimina un mensaje de chatbot."""
    db_mensaje = db.query(MensajeChatbotModel).filter(MensajeChatbotModel.id == mensaje_id).first()
    if db_mensaje is None:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")

    db.delete(db_mensaje)
    db.commit()
    return None