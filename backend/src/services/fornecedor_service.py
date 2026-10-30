from sqlalchemy.orm import Session
from backend.src.models.fornecedor_model import FornecedorModel
from backend.src.schemas.fornecedor_schema import FornecedorCreate, FornecedorUpdate, FornecedorResponse
from backend.src.repositories.fornecedor_repository import FornecedorRepository

class FornecedorService:
    # --------------------------------- Funções helpers ---------------------------------
    @staticmethod
    def verificar_fornecedor_pelo_nome(db:Session, fornecedor_nome:str) -> tuple[FornecedorModel | None, str]:
            fornecedor = FornecedorRepository.obter_fornecedor_pelo_nome(db=db, fornecedor_nome=fornecedor_nome)
            if not fornecedor:
                return None, ""
            return fornecedor, f"Ja existe um fornecedor cadastrado com o nome {fornecedor_nome}" 

    @staticmethod
    def verificar_fornecedor_pelo_id(db:Session, fornecedor_id) -> FornecedorModel:
         fornecedor = FornecedorRepository.obter_fornecedor_pelo_id(db=db, fornecedor_id=fornecedor_id)
         if not fornecedor:
              raise ValueError(f"Fornecedor com o ID {fornecedor_id} não encontrato ou inexistente")
         return fornecedor 
    # --------------------------------- Funções sistema ---------------------------------
    @staticmethod
    def criar_fornecedor(db:Session, fornecedor_dados:FornecedorCreate) -> FornecedorResponse:
        fornecedor, msg = FornecedorService.verificar_fornecedor_pelo_nome(db=db, fornecedor_nome=fornecedor_dados.nome_fornecedor)
        if not fornecedor:
              fornecedor_dict = fornecedor_dados.model_dump()
              novo_fornecedor = FornecedorRepository.criar_fornecedor(db=db, fornecedor_dados=fornecedor_dict)
              return FornecedorResponse.model_validate(novo_fornecedor)
        else:
              raise ValueError(msg)

    @staticmethod
    def alterar_fornecedor(db:Session, fornecedor_id:int, fornecedor_dados:FornecedorUpdate) -> FornecedorResponse:
        fornecedor = FornecedorService.verificar_fornecedor_pelo_id(db=db, fornecedor_id=fornecedor_id)

        fornecedor_dict = fornecedor_dados.model_dump(exclude_unset=True, exclude={"id"})

        if "nome_fornecedor" in fornecedor_dict and fornecedor_dict["nome_fornecedor"] != fornecedor.nome_fornecedor:
              fornecedor_existente, msg = FornecedorService.verificar_fornecedor_pelo_nome(db=db, fornecedor_nome=fornecedor_dict["nome_fornecedor"])
              if fornecedor_existente:
                   raise ValueError(msg)

        fornecedor_atualizado = FornecedorRepository.alterar_fornecedor(db=db, db_fornecedor=fornecedor, fornecedor_dados=fornecedor_dict)
        return FornecedorResponse.model_validate(fornecedor_atualizado)

    @staticmethod
    def obter_todos_fornecedores(db:Session, skip:int = 0, limit:int = 100) -> list[FornecedorResponse]:
         forneceddores = FornecedorRepository.obter_todos_fornecedores(db=db, skip=skip, limit=limit)
         return [FornecedorResponse.model_validate(fornecedor) for fornecedor in forneceddores if fornecedor is not None]

    @staticmethod
    def obter_fornecedor_pelo_id(db: Session, fornecedor_id:int) -> FornecedorResponse:
        fornecedor = FornecedorService.verificar_fornecedor_pelo_id(db=db, fornecedor_id=fornecedor_id)
        return FornecedorResponse.model_validate(fornecedor)

    @staticmethod
    def obter_fornecedor_pelo_nome(db:Session, fornecedor_nome:str) -> FornecedorResponse:
         fornecedor, msg = FornecedorService.verificar_fornecedor_pelo_nome(db=db, fornecedor_nome=fornecedor_nome)
         if fornecedor:
              return FornecedorResponse.model_validate(fornecedor)
         else:
            raise ValueError(msg)

    @staticmethod
    def desativar_ativar_fornecedor(db:Session, fornecedor_id:int, status:bool) -> FornecedorResponse:
         fornecedor = FornecedorService.verificar_fornecedor_pelo_id(db=db, fornecedor_id=fornecedor_id)
         fornecedor_atualizado = FornecedorRepository.destivar_ativar_fornecedor(db=db, db_fornecedor=fornecedor, status=status)
         return FornecedorResponse.model_validate(fornecedor_atualizado)         
