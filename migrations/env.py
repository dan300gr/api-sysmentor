from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Cerca del principio del archivo, después de las importaciones existentes
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importa la clase Base
from app.database import Base

# Importa todos los modelos
from app.models.usuario import Usuario
from app.models.semestre import Semestre
from app.models.materia import Materia
from app.models.semana_tema import SemanaTema
from app.models.recurso import Recurso
from app.models.cuestionario import Cuestionario
from app.models.pregunta import Pregunta
from app.models.opcion import Opcion
from app.models.foro import Foro
from app.models.comentario_foro import ComentarioForo
from app.models.reaccion_foro import ReaccionForo
from app.models.progreso_recurso import ProgresoRecurso
from app.models.conversacion_chatbot import ConversacionChatbot
from app.models.mensaje_chatbot import MensajeChatbot

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Obtener la URL de la base de datos desde la variable de entorno
# si está disponible, de lo contrario usar la configurada en alembic.ini
def get_url():
    return os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

# Configuración adicional para trabajar con una base de datos existente
def include_object(object, name, type_, reflected, compare_to):
    # Excluir vistas, si las hay
    if type_ == "table" and name.startswith("vw_"):
        return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Opciones adicionales para trabajar con una base de datos existente
        include_object=include_object,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=True,  # Útil para SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Modificar la configuración para usar la URL de la variable de entorno
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Opciones adicionales para trabajar con una base de datos existente
            include_object=include_object,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True,  # Útil para SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()