from sqlalchemy.orm import Session
from backend.src.models.usuario_model import UsuarioModel
from backend.src.repositories.usuario_repository import UsuarioRepository
from backend.src.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioUpdateSenha, UsuarioResponse

class UsuarioService:
    # ------------------------------- Funções helpers  -------------------------------
    @staticmethod
    def verificar_usuario_pelo_email(db:Session, email:str) -> bool:
        if not email:
            raise ValueError(f"Email não informado!")
        
        usuario = UsuarioRepository.obter_usuario_pelo_email(db=db, email=email)
        
        if usuario:
            raise ValueError(f"Ja existe um usuário cadastrado com o email {email}")
        
        return True
    
    @staticmethod
    def verificar_usuario_pelo_id(db:Session, usuario_id:int) -> UsuarioModel:
        usuario = UsuarioRepository.obter_usuario_pelo_id(db=db, usuario_id=usuario_id)
        
        if not usuario:
            raise ValueError(f"Não existe usuario cadastrado com o ID {usuario_id}")
        return usuario
    
    @staticmethod
    def verificar_usuario_pelo_nome(db:Session, nome:str) -> UsuarioModel:
        usuario = UsuarioRepository.obter_usuario_pelo_nome(db=db, nome_usuario=nome)
        
        if not usuario:
            raise ValueError(f"Não encontrado o usuario pelo com o nome {nome}")
        return usuario
# ------------------------------- Funções sistema -------------------------------
    @staticmethod
    def criar_usuario(db:Session, usuario_dados:UsuarioCreate) -> UsuarioResponse:
        UsuarioService.verificar_usuario_pelo_email(db=db, email=usuario_dados.email)
        
        usuario_dict = usuario_dados.model_dump()
        novo_usuario = UsuarioRepository.criar_usuario(db=db, dados_usuario=usuario_dict)
        return UsuarioResponse.model_validate(novo_usuario)
    
    @staticmethod
    def alterar_usuario(db:Session, usuario_id:int, usuario_dados:UsuarioUpdate) -> UsuarioResponse:
        usuario = UsuarioService.verificar_usuario_pelo_id(db=db, usuario_id=usuario_id)
        
        usurio_dict = usuario_dados.model_dump(exclude_unset=True, exclude={"id"})
        
        usuario_atualizado = UsuarioRepository.alterar_usuario(db=db, db_usuario=usuario, usuario_dados=usurio_dict)
        return UsuarioResponse.model_validate(usuario_atualizado)
    
    @staticmethod
    def obter_todos_usuarios(db:Session, skip:int = 0, limit:int = 100) -> list[UsuarioModel]:
        usuarios = UsuarioRepository.obter_todos_usuarios(db=db, skip=skip, limit=limit)
        return [UsuarioResponse.model_validate(usuarios) for usuario in usuarios if usuario is not None]
    
    @staticmethod
    def obter_usuario_pelo_id(db:Session, usuario_id: int) -> UsuarioModel | None:
        usuario = UsuarioService.verificar_usuario_pelo_id(db=db, usuario_id=usuario_id)
        
        return UsuarioResponse.model_validate(usuario)
    
    @staticmethod
    def obter_usuario_pelo_nome(db:Session, nome:str) -> UsuarioModel:
        usuario = UsuarioService.verificar_usuario_pelo_nome(db=db, nome=nome)
        return UsuarioResponse.model_validate(usuario)
    
    @staticmethod
    def obter_usuario_pelo_email(db:Session, email:str) -> UsuarioModel:
        tem_usuario = UsuarioService.verificar_usuario_pelo_email(db=db, email=email)
        if tem_usuario:
            usuario = UsuarioRepository.obter_usuario_pelo_email(db=db, email=email)
            return UsuarioResponse.model_validate(usuario)
        
        