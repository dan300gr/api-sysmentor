# Importación de todos los esquemas
from .usuario import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioInDB, UsuarioLogin
from .semestre import Semestre, SemestreCreate, SemestreUpdate, SemestreInDB
from .materia import Materia, MateriaCreate, MateriaUpdate, MateriaInDB
from .semana_tema import SemanaTema, SemanaTemaCreate, SemanaTemaUpdate, SemanaTemaInDB
from .cuestionario import Cuestionario, CuestionarioCreate, CuestionarioUpdate, CuestionarioInDB
from .pregunta import Pregunta, PreguntaCreate, PreguntaUpdate, PreguntaInDB
from .opcion import Opcion, OpcionCreate, OpcionUpdate, OpcionInDB
from .recurso import Recurso, RecursoCreate, RecursoUpdate, RecursoInDB, TipoRecursoEnum
from .progreso_recurso import ProgresoRecurso, ProgresoRecursoCreate, ProgresoRecursoUpdate, ProgresoRecursoInDB, EstadoProgresoEnum
from .foro import Foro, ForoCreate, ForoUpdate, ForoInDB
from .comentario_foro import ComentarioForo, ComentarioForoCreate, ComentarioForoUpdate, ComentarioForoInDB
from .reaccion_foro import ReaccionForo, ReaccionForoCreate, ReaccionForoUpdate, ReaccionForoInDB, TipoReaccionEnum
from app.schemas.mensaje_chatbot import MensajeChatbot, MensajeChatbotCreate, MensajeChatbotUpdate
from app.schemas.mensaje_chatbot import MensajeChatbotWithUsuario