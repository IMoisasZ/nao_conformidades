from sqlalchemy.orm import Session
from backend.src.models.setor_model import SetorModel
from backend.src.schemas.setor_schema import SetorCreate, SetorUpdate, SetorResponse
from backend.src.repositories.setor_repository import SetorRepository

class SetorService:
    # --------------------------- Funções helpers ---------------------------
    @staticmethod
    def verifica_setor_pelo_nome(db:Session, nome_setor: str) -> tuple[SetorModel | None, str]:
        setor = SetorRepository.obter_setor_pelo_nome(db=db, nome_setor=nome_setor)
        if not setor:
            return None, ""
        return setor, f"O setor {nome_setor} já foi cadastrado!"

    @staticmethod
    def verifica_setor_pelo_id(db:Session, setor_id:int) -> SetorModel:
        setor = SetorRepository.obter_setor_pelo_id(db=db, setor_id=setor_id)
        if not setor:
            raise ValueError(f"O ID {setor_id} não foi encontrado ou inexistente!")
        return setor
    
    # --------------------------- Funções do sistema ---------------------------
    @staticmethod
    def criar_setor(db:Session, setor_dados:SetorCreate) -> SetorResponse:
        setor, msg = SetorService.verifica_setor_pelo_nome(db=db, nome_setor=setor_dados.nome_setor)

        if not setor:
            setor_dict = setor_dados.model_dump()
            novo_setor = SetorRepository.criar_setor(db=db, setor_dados=setor_dict)
            return SetorResponse.model_validate(novo_setor)
        else:
            raise ValueError(msg)

    @staticmethod
    def alterar_setor(db:Session, setor_id:int, setor_dados:SetorUpdate) -> SetorResponse:
        setor = SetorService.verifica_setor_pelo_id(db=db, setor_id=setor_id)

        setor_dict = setor_dados.model_dump(exclude_unset=True, exclude={"id"})

        if "nome_setor" in setor_dict and setor_dict["nome_setor"] != setor.nome_setor:
            setor_existente, msg = SetorService.verifica_setor_pelo_nome(db=db, nome_setor=setor_dict["nome_setor"])
            if setor_existente:
                raise ValueError(msg)

        setor_atualizado = SetorRepository.alterar_setor(db=db, db_setor=setor, setor_dados=setor_dict)
        return SetorResponse.model_validate(setor_atualizado)

    @staticmethod
    def obter_todos_setores(db:Session, skip:int=0, limit:int=100) -> list[SetorResponse]:
        setores = SetorRepository.obter_todos_setores(db=db, skip=skip, limit=limit)
        return [SetorResponse.model_validate(setor) for setor in setores if setor is not None]

    @staticmethod
    def obter_setor_pelo_id(db:Session, setor_id:int) -> SetorResponse:
        setor = SetorService.verifica_setor_pelo_id(db=db, setor_id=setor_id)
        return SetorResponse.model_validate(setor)

    @staticmethod
    def obter_setor_pelo_nome(db:Session, nome_setor:str) -> SetorResponse:
        setor, _ = SetorService.verifica_setor_pelo_nome(db=db, nome_setor=nome_setor)
        if setor:
            return SetorResponse.model_validate(setor)
        else:
            raise ValueError(f"Setor {nome_setor} não foi encontrato.")

    @staticmethod
    def desativar_ativar_setor(db:Session, setor_id:int, status:bool) -> SetorResponse:
        setor = SetorService.verifica_setor_pelo_id(db=db, setor_id=setor_id)
        setor_atualizado = SetorRepository.desativar_ativar_Setor(db=db, db_setor=setor, status=status)
        return SetorResponse.model_validate(setor_atualizado)