from statistics import quantiles

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

"""
* cria a conexão com o banco de dados
* aqui usei SQLite, mas você poderia usar outro banco de dados como PostgreSQL, MySQL, etc.
* basta alterar a string de conexão
* Exemplo para PostgreSQL: "postgresql://user:password@localhost/dbname"
"""
db = create_engine("sqlite:///banco.db")

# cria a base do banco de dados
Base = declarative_base()

# cria as classes que representam as tabelas do banco de dados

# Usuario
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String(100), nullable=False)
    email = Column("email", String(100), nullable=False)
    senha = Column("senha", String(100), nullable=False)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin
        
# Pedido
class Pedido(Base):
    __tablename__ = "pedidos"
    
    # STATUS_PEDIDOS = (
    #     ("PENDENTE", "PENDENTE"),
    #     ("CANCELADO", "CANCELADO"),
    #     ("FINALIZADO", "FINALIZADO"),
    # )
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String, nullable=False) # pendete, cancelado, finalizado.
    usuario = Column("usuario", Integer, ForeignKey("usuarios.id"), nullable=False)
    preco = Column("preco", Float)
    itens = relationship("ItemPedido", cascade="all, delete")

    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.usuario = usuario
        self.status = status
        self.preco = preco

    def calcular_preco(self):
        # percorrer todos os itens do pedido
        # somar todos os preços de todos os itens  dos pedidos
        # editar no campo "preco" o valor final do preco do pedido
        self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)

# ItensPedido
class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer, nullable=False)
    sabor = Column("sabor", String(100), nullable=False)
    tamanho = Column("tamanho", String(100), nullable=False)
    preco_unitario = Column("preco_unitario", Float, nullable=False)
    pedido = Column("pedido", Integer, ForeignKey("pedidos.id"), nullable=False)

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido

# executa a criação dos metadados do banco de dados(criar efetivamente o banco de dados)



# Migrar o banco de dados:

# criar a migraçção: alembic revision --autogenerate -m "mensagem"
# executar a migração: alembic upgrade head


