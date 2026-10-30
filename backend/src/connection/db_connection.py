"""Módulo de Conexão e Gerenciamento do Banco de Dados.

Este módulo é responsável por carregar as variáveis de ambiente, configurar
a engine do SQLAlchemy, definir a base declarativa para os modelos ORM e 
fornecer o gerenciador de contexto para sessões de banco de dados.
"""

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Carrega as variáveis de ambiente definidas no arquivo .env
load_dotenv()

# Base declarativa para o mapeamento dos modelos ORM
Base = declarative_base()

# Construção segura da URL de conexão utilizando os parâmetros do ambiente
DATABASE_URL = URL.create(
    drivername=os.getenv("DB_DRIVER", "mysql+pymysql"),
    username=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    database=os.getenv("DB_NAME", "sistema_injetaq"),
)

if not DATABASE_URL:
    raise ValueError("A variável DATABASE_URL não foi encontrada no arquivo .env!")

# Criação da engine de conexão com o banco de dados
# pool_pre_ping=True garante a reconexão automática caso a conexão caia
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Fábrica de sessões do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Gerenciador de contexto para criar e fechar sessões do banco de dados.

    Yields:
        Session: Instância ativa da sessão do SQLAlchemy.

    Example:
        >>> with get_db() as db:
        ...     setores = SetorService.obter_todos_setores(db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria todas as tabelas registradas nos modelos ORM que ainda não existem no banco."""
    Base.metadata.create_all(bind=engine)