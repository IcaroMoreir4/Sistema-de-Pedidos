import os
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Configuração melhorada do FastAPI com metadados descritivos
app = FastAPI(
    title="🍽️ Sistema de Pedidos - API",
    description="""
    ## 🚀 Bem-vindo ao Sistema de Pedidos!
    
    Esta API permite gerenciar pedidos de qualquer lanchonete, restaurante ou estabelecimento com sistema de autenticação e autorização.
    
    ### 📚 **Como usar esta API:**
    
    1. **Primeiro, acesse `/docs`** para ver a documentação interativa completa
    2. **Crie uma conta** usando `/auth/criar_conta`
    3. **Faça login** usando `/auth/login` para obter um token de acesso
    4. **Use o token** no cabeçalho `Authorization: Bearer <seu_token>` para acessar as rotas protegidas
    
    ### 🔐 **Autenticação:**
    - Todas as rotas de pedidos requerem autenticação
    - Use o endpoint `/auth/login-form` no Swagger UI para facilitar os testes
    - Tokens expiram em 30 minutos por padrão
    
    ### 👥 **Tipos de Usuário:**
    - **Usuários comuns**: Podem criar pedidos e gerenciar seus próprios pedidos
    - **Administradores**: Podem acessar todos os pedidos e criar outros administradores
    
    ### 📋 **Funcionalidades Principais:**
    - Sistema de autenticação JWT
    - Gerenciamento de pedidos com status
    - Adição/remoção de itens nos pedidos
    - Controle de preços automático
    - Sistema de permissões baseado em roles
    
    ---
    **Desenvolvido com FastAPI, SQLAlchemy e SQLite**
    """,
    version="1.0.0",
    contact={
        "name": "Equipe de Desenvolvimento",
        "email": "dev@restaurante.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Operações de autenticação e gerenciamento de usuários. Inclui login, criação de contas e gerenciamento de tokens."
        },
        {
            "name": "pedidos",
            "description": "Gerenciamento completo de pedidos. Inclui criação, visualização, atualização e cancelamento de pedidos e itens."
        }
    ]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)

@app.get("/", tags=["principal"])
async def rota_principal():
    """
    # 🏠 Página Principal da API de Pedidos
    
    ## 📖 Instruções de Uso
    
    ### 🔍 Para Desenvolvedores e Testadores:
    - **Acesse `/docs`** para a documentação interativa completa (Swagger UI)
    - **Acesse `/redoc`** para uma documentação alternativa mais limpa
    
    ### 🚀 Primeiros Passos:
    1. **Documentação**: Comece explorando `/docs` para entender todos os endpoints
    2. **Criação de Conta**: Use `/auth/criar_conta` para criar um usuário
    3. **Autenticação**: Use `/auth/login` para obter um token de acesso
    4. **Teste os Endpoints**: Use o Swagger UI para testar todas as funcionalidades
    
    ### 🛠️ Endpoints Disponíveis:
    
    #### 🔐 **Autenticação (`/auth`)**
    - `POST /auth/criar_conta` - Criar conta de usuário comum
    - `POST /auth/criar_admin` - Criar conta de administrador (requer admin)
    - `POST /auth/login` - Login com email/senha
    - `POST /auth/login-form` - Login via formulário (para Swagger UI)
    - `GET /auth/refresh` - Renovar token de acesso
    
    #### 🍽️ **Pedidos (`/pedidos`)**
    - `GET /pedidos/` - Listar todos os pedidos (apenas admin)
    - `POST /pedidos/` - Criar novo pedido
    - `GET /pedidos/meus` - Listar meus pedidos
    - `GET /pedidos/{id}` - Visualizar pedido específico
    - `POST /pedidos/{id}/cancelar` - Cancelar pedido
    - `POST /pedidos/{id}/finalizar` - Finalizar pedido
    - `POST /pedidos/{id}/itens` - Adicionar item ao pedido
    - `DELETE /pedidos/itens/{id}` - Remover item do pedido
    
    ### 🔧 **Tecnologias Utilizadas:**
    - **Backend**: FastAPI (Python)
    - **Banco de Dados**: SQLite com SQLAlchemy
    - **Autenticação**: JWT (JSON Web Tokens)
    - **Criptografia**: bcrypt para senhas
    - **Documentação**: Swagger UI automática
    
    ### 📝 **Exemplo de Uso:**
    ```bash
    # 1. Criar conta
    curl -X POST "http://localhost:8000/auth/criar_conta" \
         -H "Content-Type: application/json" \
         -d '{"nome": "João Silva", "email": "joao@email.com", "senha": "123456"}'
    
    # 2. Fazer login
    curl -X POST "http://localhost:8000/auth/login" \
         -H "Content-Type: application/json" \
         -d '{"email": "joao@email.com", "senha": "123456"}'
    
    # 3. Usar o token retornado para acessar endpoints protegidos
    curl -X GET "http://localhost:8000/pedidos/meus" \
         -H "Authorization: Bearer <seu_token_aqui>"
    ```
    
    ---
    **🎯 Dica**: Use sempre o Swagger UI em `/docs` para uma experiência mais interativa e visual!
    """
    return {
        "message": "🍽️ Bem-vindo ao Sistema de Pedidos!",
        "instrucoes": "Acesse /docs para a documentação completa e interativa",
        "endpoints_disponiveis": {
            "documentacao": {
                "swagger_ui": "/docs",
                "redoc": "/redoc"
            },
            "autenticacao": "/auth",
            "pedidos": "/pedidos"
        },
        "primeiros_passos": [
            "1. Acesse /docs para explorar a API",
            "2. Crie uma conta em /auth/criar_conta",
            "3. Faça login em /auth/login",
            "4. Use o token para acessar endpoints protegidos"
        ]
    }

# para rodar o código , executar no terminal:
# uvicorn main:app --reload

