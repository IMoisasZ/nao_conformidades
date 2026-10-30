from sqlalchemy.orm import Session
from backend.src.models.cliente_model import ClienteModel
from backend.src.repositories.cliente_repository import ClienteRepository
from backend.src.schemas.cliente_schema import ClienteCreate, ClienteUpdate, ClienteResponse

class ClienteService:
    # --------------------------------- Funções helpers ---------------------------------
    @staticmethod
    def verificar_cliente_pelo_nome(db:Session, nome_cliente:str) -> tuple[ClienteResponse | None, str]:
        cliente = ClienteRepository.obter_cliente_pelo_nome(db=db, nome_cliente=nome_cliente)
        if not cliente:
            return None, ""
        return cliente, f"Já existe um cliente com o nome {nome_cliente}"

    @staticmethod
    def verificar_cliente_pelo_id(db:Session, cliente_id:int) -> ClienteModel:
        cliente = ClienteRepository.obter_cliente_pelo_id(db=db, cliente_id=cliente_id)
        if not cliente:
            raise ValueError(f"Cliente com o ID {cliente_id} não encontrado ou inexistente")
        return cliente

    # --------------------------------- Funções do sistema ---------------------------------
    
    @staticmethod
    def criar_cliente(db:Session, cliente_dados:ClienteCreate) -> ClienteResponse:
        cliente, msg = ClienteService.verificar_cliente_pelo_nome(db=db, nome_cliente=cliente_dados.nome_cliente)
        if not cliente:
            cliente_dict = cliente_dados.model_dump()
            novo_cliente = ClienteRepository.criar_cliente(db=db, cliente_dados=cliente_dict)
            return ClienteResponse.model_validate(novo_cliente)
        else:
            raise ValueError(msg)

    @staticmethod
    def alterar_cliente(db:Session, cliente_id:int, cliente_dados:ClienteUpdate) -> ClienteResponse:
        cliente = ClienteService.verificar_cliente_pelo_id(db=db, cliente_id=cliente_id)

        cliente_dict = cliente_dados.model_dump(exclude_unset=True, exclude={"id"})

        if "nome_cliente" in cliente_dict and cliente_dict["nome_cliente"] != cliente.nome_cliente:
            cliente_existente, msg = ClienteService.verificar_cliente_pelo_nome(db=db, nome_cliente=cliente_dict["nome_cliente"])
            if cliente_existente:
                raise ValueError(msg)

        cliente_atualizado = ClienteRepository.alterar_cliente(db=db, db_cliente=cliente, cliente_dados=cliente_dict)
        return ClienteResponse.model_validate(cliente_atualizado)

    @staticmethod
    def obter_todos_clientes(db:Session, skip:int = 0, limit:int = 100) -> list[ClienteResponse]:
        clientes = ClienteRepository.obter_todos_clientes(db=db, skip=skip, limit=limit)
        return [ClienteResponse.model_validate(cliente) for cliente in clientes if cliente is not None]

    @staticmethod
    def obter_cliente_pelo_id(db: Session, cliente_id:int) -> ClienteResponse:
        cliente = ClienteService.verificar_cliente_pelo_id(db=db, cliente_id=cliente_id)
        return ClienteResponse.model_validate(cliente)

    @staticmethod
    def obter_cliente_pelo_nome(db:Session, nome_clinete:str) -> ClienteResponse:
        cliente, _ = ClienteService.verificar_cliente_pelo_nome(db=db, nome_cliente=nome_clinete)
        if cliente:
            return ClienteResponse.model_validate(cliente)
        else:
            raise ValueError(f"Cliente {nome_clinete} não encontrato.")

    @staticmethod
    def desativar_ativar_cliente(db:Session, cliente_id:int, status:bool) -> ClienteResponse:
        cliente = ClienteService.verificar_cliente_pelo_id(db=db, cliente_id=cliente_id)
        cliente_atualizado = ClienteRepository.desativar_ativar_cliente(db=db, db_cliente=cliente, status=status)
        return ClienteResponse.model_validate(cliente_atualizado)