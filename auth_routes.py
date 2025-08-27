from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from main import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY,
                  bcrypt_context)
from models import Usuario
from schemas import LoginSchema, UsuarioSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Esquema para a resposta do token
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

def criar_token(id_usuario, duarcao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duarcao_token
    dic_info = {
        "sub": str(id_usuario),
        "exp": data_expiracao
    }
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario

# Dependência para autenticação opcional (não lança erro se o token não existir)
oauth2_scheme_opcional = OAuth2PasswordBearer(tokenUrl="/auth/login-form", auto_error=False)

async def pegar_usuario_logado_opcional(
    session: Session = Depends(pegar_sessao),
    token: Optional[str] = Depends(oauth2_scheme_opcional)
) -> Optional[Usuario]:
    """
    Dependência para obter o usuário logado a partir do token JWT.
    Retorna o objeto do usuário se o token for válido, ou None se o token
    não for fornecido ou for inválido. Não lança uma exceção HTTP.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario: str = payload.get("sub")
        if id_usuario is None:
            return None
    except JWTError:
        return None

    usuario = session.query(Usuario).filter(Usuario.id == int(id_usuario)).first()
    return usuario


@auth_router.get("/", summary="Verifica a conexão com as rotas de autenticação")
async def autenticar():
    """
    ## 🔍 Endpoint de Teste de Conexão
    
    **O que faz:** Verifica se as rotas de autenticação estão ativas e funcionando.
    
    **Uso:** Endpoint simples para testar se o serviço está rodando.
    
    **Resposta:** Mensagem de confirmação de que a rota está acessível.
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/auth/"
    ```
    
    **Resposta esperada:**
    ```json
    {
        "message": "Você acessou a rota de autenticação"
    }
    ```
    """
    return {"message": "Você acessou a rota de autenticação"}


# ----------- ROTA PARA QUALQUER UM CRIAR USUÁRIO COMUM -----------
@auth_router.post(
    "/criar_conta",
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma conta de usuário comum",
    description="""
    ## 👤 Criação de Conta de Usuário Comum
    
    **O que faz:** Permite que qualquer pessoa crie uma conta de usuário no sistema.
    
    **⚠️ Importante:** 
    - O campo `admin` não é aceito aqui
    - Todo usuário será criado como **não-admin** por padrão
    - Apenas administradores podem criar outros administradores
    
    **Parâmetros necessários:**
    - `nome` (string): Nome completo do usuário
    - `email` (string): Email único do usuário (será validado)
    - `senha` (string): Senha que será criptografada automaticamente
    
    **Validações:**
    - Email deve ser único no sistema
    - Nome e senha são obrigatórios
    - Senha é automaticamente criptografada com bcrypt
    
    **Resposta de sucesso:** Confirmação da criação com o email do usuário
    
    **Possíveis erros:**
    - `400`: Email já existe no sistema
    - `500`: Erro interno do servidor
    """,
    response_description="Mensagem de sucesso na criação do usuário com o email criado."
)
async def criar_conta(
    usuario_schema: UsuarioSchema,
    session: Session = Depends(pegar_sessao)
):
    # Checa se já existe usuário com esse e-mail
    usuario_existente = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Já existe um usuário com esse email")

    try:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)

        novo_usuario = Usuario(
            nome=usuario_schema.nome,
            email=usuario_schema.email,
            senha=senha_criptografada,
            ativo=True,
            admin=False  # Sempre falso aqui
        )

        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

    return {"message": f"Usuário {novo_usuario.email} criado com sucesso"}


# ----------- ROTA EXCLUSIVA PARA ADMINS CRIAR OUTROS ADMINS -----------
@auth_router.post(
    "/criar_admin",
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma conta de administrador",
    description="""
    ## 👑 Criação de Conta de Administrador
    
    **O que faz:** Permite que administradores criem outras contas de administrador.
    
    **🔒 Segurança:** 
    - **Acesso restrito apenas a administradores autenticados**
    - Token de acesso deve ser enviado no cabeçalho `Authorization: Bearer <token>`
    
    **Parâmetros necessários:**
    - `nome` (string): Nome completo do administrador
    - `email` (string): Email único do administrador
    - `senha` (string): Senha que será criptografada
    
    **Validações:**
    - Usuário logado deve ter privilégios de administrador
    - Email deve ser único no sistema
    - Todos os campos são obrigatórios
    
    **Resposta de sucesso:** Confirmação da criação do administrador
    
    **Possíveis erros:**
    - `401`: Token de autenticação inválido ou ausente
    - `403`: Usuário logado não é administrador
    - `400`: Email já existe no sistema
    - `500`: Erro interno do servidor
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/auth/criar_admin" \
         -H "Authorization: Bearer <seu_token_admin>" \
         -H "Content-Type: application/json" \
         -d '{"nome": "Admin Silva", "email": "admin@email.com", "senha": "senha123"}'
    ```
    """,
    response_description="Mensagem de sucesso na criação do administrador com o email criado."
)
async def criar_admin(
    usuario_schema: UsuarioSchema,
    session: Session = Depends(pegar_sessao),
    usuario_logado: Usuario = Depends(verificar_token)  # aqui obriga login
):
    # Garante que só admins podem criar admins
    if not usuario_logado.admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar outros administradores")

    usuario_existente = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Já existe um usuário com esse email")

    try:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)

        novo_admin = Usuario(
            nome=usuario_schema.nome,
            email=usuario_schema.email,
            senha=senha_criptografada,
            ativo=True,
            admin=True
        )

        session.add(novo_admin)
        session.commit()
        session.refresh(novo_admin)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar administrador: {str(e)}")

    return {"message": f"Administrador {novo_admin.email} criado com sucesso"}


@auth_router.post("/login", summary="Autentica um usuário e retorna tokens", response_model=TokenSchema)
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    """
    ## 🔑 Autenticação de Usuário
    
    **O que faz:** Recebe credenciais de email e senha, verifica se são válidas e retorna tokens de acesso.
    
    **Parâmetros necessários:**
    - `email` (string): Email do usuário cadastrado
    - `senha` (string): Senha do usuário (será comparada com a versão criptografada)
    
    **Processo de autenticação:**
    1. Busca o usuário pelo email fornecido
    2. Verifica se a senha fornecida corresponde à senha criptografada no banco
    3. Se válido, gera tokens de acesso e refresh
    
    **Resposta de sucesso:**
    - `access_token`: Token JWT para autorização (expira em 30 minutos)
    - `refresh_token`: Token para renovar o access_token (expira em 7 dias)
    - `token_type`: Tipo do token (sempre "Bearer")
    
    **Possíveis erros:**
    - `401`: Credenciais inválidas (usuário não existe ou senha incorreta)
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/auth/login" \
         -H "Content-Type: application/json" \
         -d '{"email": "usuario@email.com", "senha": "minhasenha"}'
    ```
    
    **Resposta esperada:**
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "Bearer"
    }
    ```
    
    **⚠️ Importante:** Guarde o `access_token` para usar nos endpoints protegidos!
    """
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = criar_token(usuario.id)
    refresh_token = criar_token(usuario.id, timedelta(days=7))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


@auth_router.post(
    "/login-form",
    summary="Autenticação via formulário para o Swagger UI",
    description="""
    ## 🌐 Login via Formulário (Swagger UI)
    
    **O que faz:** Endpoint compatível com OAuth2 para permitir o login diretamente na documentação interativa.
    
    **🎯 Uso principal:** 
    - Facilita os testes diretamente no Swagger UI (`/docs`)
    - Permite que você faça login e teste endpoints protegidos sem sair da interface
    
    **Parâmetros (via formulário):**
    - `username`: Email do usuário
    - `password`: Senha do usuário
    
    **Diferença do endpoint `/login`:**
    - Retorna apenas o `access_token` (sem refresh_token)
    - Formato compatível com OAuth2 para integração com Swagger UI
    
    **Como usar no Swagger UI:**
    1. Acesse `/docs`
    2. Clique no botão "Authorize" (🔒) no topo da página
    3. Use este endpoint para fazer login
    4. O token será automaticamente aplicado aos próximos requests
    
    **Resposta:** Apenas o `access_token` necessário para autorização
    
    **⚠️ Nota:** Este endpoint é otimizado para uso na interface web, não para integração direta via API.
    """,
    response_model=TokenSchema
)
async def login_form(
        dados_formulario: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(pegar_sessao)
):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }

@auth_router.get(
    "/refresh",
    summary="Gera um novo token de acesso usando um refresh token",
    description="""
    ## 🔄 Renovação de Token de Acesso
    
    **O que faz:** Permite obter um novo `access_token` sem precisar enviar credenciais novamente.
    
    **🔑 Como funciona:**
    - Use um `refresh_token` válido (obtido no login)
    - Envie como Bearer token no cabeçalho de autorização
    - Receba um novo `access_token` válido
    
    **Parâmetros:**
    - **Header obrigatório:** `Authorization: Bearer <refresh_token>`
    
    **Vantagens:**
    - Não precisa reenviar email/senha
    - Mantém o usuário logado por mais tempo
    - Mais seguro que armazenar credenciais
    
    **Fluxo de uso:**
    1. Faça login e receba `access_token` + `refresh_token`
    2. Use `access_token` para acessar endpoints
    3. Quando `access_token` expirar, use `refresh_token` aqui
    4. Continue usando o novo `access_token`
    
    **Resposta:** Novo `access_token` válido
    
    **Possíveis erros:**
    - `401`: Refresh token inválido ou expirado
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/auth/refresh" \
         -H "Authorization: Bearer <seu_refresh_token>"
    ```
    
    **⚠️ Importante:** Refresh tokens expiram em 7 dias. Após isso, o usuário deve fazer login novamente.
    """,
    response_model=TokenSchema
)
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }
