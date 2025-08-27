from pydantic import BaseModel, Field
from typing import Optional, List

class UsuarioAdminSchema(BaseModel):
    nome: str = Field(..., description="Nome completo do usuário", example="João Silva")
    email: str = Field(..., description="Email único do usuário", example="joao@email.com")
    senha: str = Field(..., description="Senha do usuário (será criptografada)", example="minhasenha123")
    ativo: Optional[bool] = Field(True, description="Status de ativação da conta", example=True)
    admin: Optional[bool] = Field(False, description="Privilégios de administrador", example=False)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "email": "joao@email.com",
                "senha": "minhasenha123",
                "ativo": True,
                "admin": False
            }
        }

class UsuarioSchema(BaseModel):
    nome: str = Field(..., description="Nome completo do usuário", example="Maria Santos")
    email: str = Field(..., description="Email único do usuário", example="maria@email.com")
    senha: str = Field(..., description="Senha do usuário (será criptografada)", example="senha123")
    ativo: Optional[bool] = Field(True, description="Status de ativação da conta", example=True)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "nome": "Maria Santos",
                "email": "maria@email.com",
                "senha": "senha123",
                "ativo": True
            }
        }
        
class PedidoSchema(BaseModel):
    id_usuario: int = Field(..., description="ID do usuário que criou o pedido", example=1)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_usuario": 1
            }
        }

class LoginSchema(BaseModel):
    email: str = Field(..., description="Email do usuário cadastrado", example="usuario@email.com")
    senha: str = Field(..., description="Senha do usuário", example="minhasenha")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "usuario@email.com",
                "senha": "minhasenha"
            }
        }

class ItemPedidoSchema(BaseModel):
    quantidade: int = Field(..., description="Quantidade do item", example=2, ge=1)
    sabor: str = Field(..., description="Nome/descrição do item (ex: X-Burger, X-Bacon, Refrigerante)", example="X-Burger")
    tamanho: str = Field(..., description="Tamanho do item (ex: Pequeno, Médio, Grande, Família, Lata, Garrafa)", example="Grande")
    preco_unitario: float = Field(..., description="Preço por unidade do item", example=25.90, ge=0)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "quantidade": 2,
                "sabor": "X-Burger",
                "tamanho": "Grande",
                "preco_unitario": 25.90
            }
        }

class ResponsePedidoSchema(BaseModel):
    id: int = Field(..., description="ID único do pedido", example=123)
    status: str = Field(..., description="Status atual do pedido (PENDENTE, EM_PREPARO, FINALIZADO, CANCELADO)", example="PENDENTE")
    preco: float = Field(..., description="Preço total do pedido", example=45.50, ge=0)
    itens: List[ItemPedidoSchema] = Field(..., description="Lista de itens no pedido")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "status": "PENDENTE",
                "preco": 45.50,
                "itens": [
                    {
                        "quantidade": 2,
                        "sabor": "X-Burger",
                        "tamanho": "Grande",
                        "preco_unitario": 22.75
                    }
                ]
            }
        }