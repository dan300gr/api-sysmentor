import os
from google import genai
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import logging
import json
from typing import Dict, Any, List, Tuple
from app.models.mensaje_chatbot import MensajeChatbot as MensajeChatbotModel
from app.models.mensaje_chatbot import ConversacionChatbot as ConversacionModel
from app.models.usuario import Usuario as UsuarioModel
from sqlalchemy.sql import func

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configurar la clave de API de Google
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Definición de la excepción personalizada
class ChatbotException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

# Función para obtener información del estudiante
def get_student_info(matricula: str, db: Session) -> Dict[str, Any]:
    """Obtiene información relevante del estudiante para personalizar respuestas."""
    if not matricula:
        return {}
    
    try:
        # Obtener información básica del estudiante
        estudiante = db.query(UsuarioModel).filter(UsuarioModel.matricula == matricula).first()
        if not estudiante:
            return {}
        
        # Construir el contexto del estudiante
        student_info = {
            "nombre": f"{estudiante.nombre} {estudiante.apellido_paterno}",
        }
        
        # Añadir información del semestre si está disponible
        if hasattr(estudiante, 'semestre') and estudiante.semestre:
            student_info["semestre_actual"] = estudiante.semestre.nombre
        
        return student_info
    except Exception as e:
        logger.error(f"Error al obtener información del estudiante: {str(e)}")
        return {}

# Función para obtener el historial de conversación mejorado
def get_conversation_history(session_id: str, db: Session, limit: int = 10) -> Tuple[str, Dict[str, Any]]:
    """
    Obtiene el historial de conversación y metadatos asociados.
    
    Args:
        session_id: ID de la sesión
        db: Sesión de base de datos
        limit: Número máximo de mensajes a recuperar
        
    Returns:
        Tuple con (contexto_texto, metadatos)
    """
    # Buscar la conversación
    conversacion = db.query(ConversacionModel).filter(
        ConversacionModel.session_id == session_id
    ).first()
    
    # Buscar los últimos mensajes de la misma sesión
    mensajes = db.query(MensajeChatbotModel).filter(
        MensajeChatbotModel.session_id == session_id
    ).order_by(MensajeChatbotModel.fecha.desc()).limit(limit).all()
    
    # Invertir para tener orden cronológico
    mensajes.reverse()
    
    # Crear el contexto basado en los mensajes previos
    contexto = ""
    metadatos = {
        "num_mensajes": len(mensajes),
        "temas_detectados": [],
        "tiene_conversacion_previa": bool(mensajes)
    }
    
    # Añadir información de la conversación si existe
    if conversacion:
        metadatos["titulo_conversacion"] = conversacion.titulo
        metadatos["temas"] = conversacion.temas
        
        # Añadir un resumen al inicio del contexto si existe
        if conversacion.resumen:
            contexto += f"Resumen de la conversación anterior: {conversacion.resumen}\n\n"
    
    # Añadir los mensajes al contexto
    for mensaje in mensajes:
        contexto += f"Usuario: {mensaje.mensaje}\nChatbot: {mensaje.respuesta}\n\n"
        
        # Recopilar metadatos de los mensajes
        if hasattr(mensaje, 'metadatos') and mensaje.metadatos and isinstance(mensaje.metadatos, dict):
            for tema in mensaje.metadatos.get("temas_detectados", []):
                if tema not in metadatos["temas_detectados"]:
                    metadatos["temas_detectados"].append(tema)
    
    return contexto, metadatos

# Función para generar un sistema prompt personalizado
def generate_system_prompt(matricula: str, metadatos: Dict[str, Any], db: Session) -> str:
    """Genera un prompt de sistema personalizado basado en el estudiante y la conversación."""
    
    # Obtener información del estudiante
    student_info = get_student_info(matricula, db)
    
    # Construir el prompt de sistema
    system_prompt = """Eres un asistente académico especializado en Ingeniería en Sistemas y Tecnologías de la Información. 
Tu objetivo es ayudar a los estudiantes a comprender conceptos, resolver dudas y proporcionar orientación académica.
Debes ser claro, preciso y educativo en tus respuestas."""
    
    # Personalizar según el estudiante
    if student_info:
        system_prompt += f"\n\nEstás hablando con {student_info['nombre']}"
        
        # Solo incluimos esta parte si existe semestre_actual en student_info
        if student_info.get("semestre_actual"):
            system_prompt += f", quien está cursando el {student_info['semestre_actual']} semestre"
    
    # Personalizar según los temas de la conversación
    if metadatos.get("temas_detectados"):
        temas = ", ".join(metadatos["temas_detectados"])
        system_prompt += f"\n\nEsta conversación ha tratado sobre: {temas}"
    
    # Añadir instrucciones específicas
    system_prompt += """

Directrices importantes:
1. Proporciona explicaciones claras y ejemplos prácticos cuando sea posible
2. Si no conoces la respuesta, indícalo claramente en lugar de inventar información
3. Cuando sea relevante, menciona recursos adicionales que el estudiante pueda consultar
4. Adapta tu nivel de explicación al contexto de la conversación
5. Mantén un tono profesional pero amigable"""

    return system_prompt

# Función para analizar el mensaje y extraer metadatos
async def analyze_message(mensaje: str, db: Session) -> Dict[str, Any]:
    """Analiza el mensaje del usuario para extraer metadatos útiles."""
    try:
        # Usar Gemini para analizar el mensaje
        prompt = f"""Analiza el siguiente mensaje de un estudiante de Ingeniería en Sistemas:

"{mensaje}"

Extrae y devuelve SOLO un objeto JSON con la siguiente estructura:
{{
  "temas_detectados": ["tema1", "tema2"],  // Lista de temas técnicos mencionados
  "tipo_consulta": "conceptual" | "práctica" | "duda" | "proyecto",  // Tipo principal de consulta
  "nivel_complejidad": "básico" | "intermedio" | "avanzado",  // Nivel estimado de la consulta
  "sentimiento": "positivo" | "neutral" | "negativo" | "confundido"  // Sentimiento detectado
}}
"""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        # Intentar extraer el JSON de la respuesta
        try:
            # Buscar contenido JSON en la respuesta
            text = response.text
            # Encontrar el primer { y el último }
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = text[start:end]
                metadatos = json.loads(json_str)
                logger.info(f"Metadatos extraídos: {metadatos}")
                return metadatos
            else:
                logger.warning("No se pudo encontrar JSON en la respuesta de análisis")
                return {}
        except json.JSONDecodeError:
            logger.warning("Error al decodificar JSON de análisis")
            return {}
            
    except Exception as e:
        logger.error(f"Error en analyze_message: {str(e)}")
        return {}

# Función para actualizar o crear la conversación
def update_conversation(session_id: str, matricula: str, mensaje: str, respuesta: str, db: Session) -> None:
    """Actualiza o crea el registro de conversación con metadatos."""
    try:
        # Buscar conversación existente
        conversacion = db.query(ConversacionModel).filter(
            ConversacionModel.session_id == session_id
        ).first()
        
        if not conversacion:
            # Generar título para la conversación
            titulo_prompt = f"""Basado en este mensaje de un estudiante: "{mensaje}"
            
Genera un título corto y descriptivo para esta conversación (máximo 5 palabras).
Responde SOLO con el título, sin comillas ni puntuación adicional."""
            
            titulo_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=titulo_prompt
            )
            
            titulo = titulo_response.text.strip()
            
            # Crear nueva conversación
            conversacion = ConversacionModel(
                session_id=session_id,
                matricula=matricula,
                titulo=titulo,
                temas=[]
            )
            db.add(conversacion)
        else:
            # Actualizar fecha de última actividad
            conversacion.fecha_ultima_actividad = func.now()
            
            # Cada 5 mensajes, actualizar el resumen
            mensajes_count = db.query(MensajeChatbotModel).filter(
                MensajeChatbotModel.session_id == session_id
            ).count()
            
            if mensajes_count % 5 == 0:
                # Obtener los últimos mensajes
                ultimos_mensajes = db.query(MensajeChatbotModel).filter(
                    MensajeChatbotModel.session_id == session_id
                ).order_by(MensajeChatbotModel.fecha.desc()).limit(5).all()
                
                # Crear contexto para el resumen
                contexto_resumen = "\n".join([
                    f"Usuario: {m.mensaje}\nChatbot: {m.respuesta}"
                    for m in reversed(ultimos_mensajes)
                ])
                
                # Generar resumen
                resumen_prompt = f"""Basado en esta conversación:

{contexto_resumen}

Genera un resumen conciso (máximo 2 frases) que capture los puntos principales discutidos."""
                
                resumen_response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=resumen_prompt
                )
                
                conversacion.resumen = resumen_response.text.strip()
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error al actualizar conversación: {str(e)}")
        # No lanzamos excepción para no interrumpir el flujo principal

# Función principal para obtener respuesta del chatbot
async def get_chatbot_response(user_input: str, context_history: str, db: Session, matricula: str = None, session_id: str = None) -> Tuple[str, Dict[str, Any]]:
    """
    Obtiene una respuesta del chatbot con contexto mejorado.
    
    Args:
        user_input: Mensaje del usuario
        context_history: Contexto previo (opcional)
        db: Sesión de base de datos
        matricula: Matrícula del estudiante (opcional)
        session_id: ID de sesión (opcional)
        
    Returns:
        Tuple con (respuesta, metadatos)
    """
    try:
        logger.info(f"Generando respuesta para: {user_input}")
        
        # Analizar el mensaje para extraer metadatos
        message_metadatos = await analyze_message(user_input, db)
        
        # Si hay un session_id, obtener el historial completo
        if session_id:
            context_history, conv_metadatos = get_conversation_history(session_id, db)
            logger.info(f"Contexto obtenido de session_id {session_id}: {len(context_history)} caracteres")
        else:
            conv_metadatos = {"tiene_conversacion_previa": False}
        
        # Generar el prompt de sistema personalizado
        system_prompt = generate_system_prompt(matricula, conv_metadatos, db)
        
        # Construir el prompt completo
        prompt = f"{system_prompt}\n\n"
        
        if context_history:
            prompt += f"{context_history}\n"
            
        prompt += f"Usuario: {user_input}\nChatbot:"
        
        # Llamar al modelo de Gemini con el prompt completo
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        # Obtener la respuesta generada
        chatbot_response = response.text.strip()
        logger.info(f"Respuesta generada: {chatbot_response[:50]}...")
        
        # Combinar metadatos
        metadatos = {
            **message_metadatos,
            "longitud_respuesta": len(chatbot_response),
            "longitud_contexto": len(context_history)
        }
        
        # Si hay session_id, actualizar la conversación
        if session_id and matricula:
            update_conversation(session_id, matricula, user_input, chatbot_response, db)
        
        return chatbot_response, metadatos

    except Exception as e:
        logger.error(f"Error en get_chatbot_response: {str(e)}")
        raise ChatbotException(f"Error al obtener respuesta del chatbot: {e}")
