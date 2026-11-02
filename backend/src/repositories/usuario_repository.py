"""Módulo de Repositório da Entidade Usuário.

Este módulo contém a classe `UsuarioRepository`, responsável por executar as operações de
persistência, consulta, geração de códigos sequenciais e atualização de senhas referentes aos
usuários diretamente no banco de dados utilizando SQLAlchemy ORM.
"""

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.models.usuario_model import UsuarioModel


class UsuarioRepository:
    """Repositório de dados para a entidade `UsuarioModel`.

    Isola as operações de acesso ao banco de dados (CRUD) da camada de serviço,
    gerenciando transações e tratando reversões (`rollback`) em caso de exceções do SQLAlchemy.
    """

    @staticmethod
    def criar_usuario(db: Session, dados_usuario: dict) -> UsuarioModel:
        """Persiste um novo registro de usuário no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            dados_usuario (dict): Dicionário contendo os atributos do usuário a ser inserido.

        Returns:
            UsuarioModel: Instância do usuário recém-criado com os dados atualizados do banco (ex: `id`).

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a persistência, executando o `rollback`.
        """
        try:
            db_usuario = UsuarioModel(**dados_usuario)
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            return db_usuario
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def alterar_usuario(
        db: Session, db_usuario: UsuarioModel, usuario_dados: dict
    ) -> UsuarioModel:
        """Atualiza os campos de um registro de usuário existente no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_usuario (UsuarioModel): Instância do usuário já carregada do banco de dados.
            usuario_dados (dict): Dicionário com as chaves e novos valores a serem atualizados.

        Returns:
            UsuarioModel: Instância do usuário atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a gravação, executando o `rollback`.
        """
        try:
            for key, value in usuario_dados.items():
                setattr(db_usuario, key, value)
            db.commit()
            db.refresh(db_usuario)
            return db_usuario
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_todos_usuarios(
        db: Session, skip: int = 0, limit: int = 100
    ) -> list[UsuarioModel]:
        """Consulta e retorna uma lista paginada de usuários cadastrados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            skip (int, optional): Quantidade de registros a serem pulados (offset). Padrão é 0.
            limit (int, optional): Limite máximo de registros a serem retornados. Padrão é 100.

        Returns:
            list[UsuarioModel]: Lista contendo as instâncias dos usuários encontrados.
        """
        return db.query(UsuarioModel).offset(skip).limit(limit=limit).all()

    @staticmethod
    def obter_usuario_pelo_id(db: Session, usuario_id: int) -> UsuarioModel | None:
        """Busca um usuário específico através do seu identificador único (`id`).

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            usuario_id (int): Chave primária do usuário desejado.

        Returns:
            UsuarioModel | None: Instância do usuário encontrado ou `None` caso não exista.
        """
        return db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()

    @staticmethod
    def obter_usuario_pelo_codigo(
        db: Session, codigo_usuario: int
    ) -> UsuarioModel | None:
        """Busca um usuário específico através do seu código/matrícula numérico.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            codigo_usuario (int): Código numérico do usuário a ser pesquisado.

        Returns:
            UsuarioModel | None: Instância do usuário encontrado ou `None` caso não exista.
        """
        return (
            db.query(UsuarioModel)
            .filter(UsuarioModel.codigo == codigo_usuario)
            .first()
        )

    @staticmethod
    def obter_usuario_pelo_nome(
        db: Session, nome_usuario: str
    ) -> UsuarioModel | None:
        """Busca um usuário específico pelo nome exato cadastrado.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            nome_usuario (str): Nome do usuário a ser pesquisado.

        Returns:
            UsuarioModel | None: Instância do usuário encontrado ou `None` caso não exista.
        """
        return (
            db.query(UsuarioModel)
            .filter(UsuarioModel.nome == nome_usuario)
            .first()
        )

    @staticmethod
    def obter_usuario_pelo_email(db: Session, email: str) -> UsuarioModel | None:
        """Busca um usuário específico através do seu endereço de e-mail.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            email (str): Endereço de e-mail do usuário a ser pesquisado.

        Returns:
            UsuarioModel | None: Instância do usuário encontrado ou `None` caso não exista.
        """
        return db.query(UsuarioModel).filter(UsuarioModel.email == email).first()

    @staticmethod
    def alterar_senha(
        db: Session, db_usuario: UsuarioModel, nova_senha: str
    ) -> UsuarioModel:
        """Atualiza a senha de acesso de um usuário específico no banco de dados.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.
            db_usuario (UsuarioModel): Instância do usuário carregada do banco de dados.
            nova_senha (str): Nova senha a ser atribuída ao usuário.

        Returns:
            UsuarioModel: Instância do usuário com a senha atualizada.

        Raises:
            SQLAlchemyError: Se ocorrer algum erro durante a gravação, executando o `rollback`.
        """
        try:
            db_usuario.senha = nova_senha
            db.commit()
            db.refresh(db_usuario)
            return db_usuario
        except SQLAlchemyError as e:
            db.rollback()
            raise e

    @staticmethod
    def obter_maior_codigo(db: Session) -> int | None:
        """Consulta e retorna o maior código numérico atualmente cadastrado na tabela de usuários.

        Utilizado pela camada de serviço para determinar o próximo número sequencial de código.

        Args:
            db (Session): Sessão ativa do banco de dados SQLAlchemy.

        Returns:
            int | None: O maior código numérico encontrado ou `None` caso a tabela esteja vazia.
        """
        return db.query(func.max(UsuarioModel.codigo)).scalar()