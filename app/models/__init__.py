# Importar todos los modelos para que estén disponibles al importar el paquete
from .usuario import Usuario
from .semestre import Semestre
from .materia import Materia
from .semana_tema import SemanaTema
from .recurso import Recurso
from .cuestionario import Cuestionario
from .pregunta import Pregunta
from .opcion import Opcion
from .foro import Foro
from .comentario_foro import ComentarioForo
from .reaccion_foro import ReaccionForo
from .progreso_recurso import ProgresoRecurso
from app.models.mensaje_chatbot import MensajeChatbot