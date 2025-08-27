# 🍽️ Sistema de Pedidos - API

## 📖 Descrição

Sistema completo de gerenciamento de pedidos para qualquer lanchonete, restaurante ou estabelecimento desenvolvido com **FastAPI**, incluindo autenticação JWT, controle de usuários, gerenciamento de pedidos e sistema de permissões baseado em roles.

## 🚀 Funcionalidades Principais

### 🔐 **Sistema de Autenticação**
- **JWT (JSON Web Tokens)** para autenticação segura
- **Criptografia bcrypt** para senhas
- **Sistema de refresh tokens** para renovação automática
- **Controle de acesso baseado em roles** (usuário comum vs administrador)

### 👥 **Gerenciamento de Usuários**
- Criação de contas de usuário comum
- Criação de contas de administrador (apenas por admins)
- Sistema de ativação/desativação de contas
- Validação de emails únicos

### 🍽️ **Gerenciamento de Pedidos**
- Criação de pedidos vazios
- Adição/remoção de itens (lanches, bebidas, etc.)
- **Cálculo automático de preços**
- Controle de status dos pedidos:
  - `PENDENTE` → `EM_PREPARO` → `FINALIZADO`
  - Cancelamento disponível para pedidos pendentes

### 🔒 **Sistema de Permissões**
- **Usuários comuns**: Gerenciam apenas seus próprios pedidos
- **Administradores**: Acesso completo a todos os pedidos e usuários

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI (Python 3.8+)
- **Banco de Dados**: SQLite com SQLAlchemy ORM
- **Autenticação**: JWT com PyJWT
- **Criptografia**: bcrypt para senhas
- **Validação**: Pydantic para schemas e validação
- **Documentação**: Swagger UI automática
- **Migrações**: Alembic para controle de versão do banco

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## 🚀 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd ProjetoFastAPI
```

### 2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Execute as migrações do banco
```bash
alembic upgrade head
```

### 6. Inicie o servidor
```bash
uvicorn main:app --reload
```

A aplicação estará disponível em: `http://localhost:8000`

## 📚 Como Usar a API

### 🔍 **Documentação Interativa**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 🏠 **Página Principal**
- **Rota**: `GET /`
- **Descrição**: Instruções completas de uso e visão geral da API

### 🔐 **Endpoints de Autenticação**

#### Criar Conta de Usuário
```bash
POST /auth/criar_conta
Content-Type: application/json

{
    "nome": "João Silva",
    "email": "joao@email.com",
    "senha": "minhasenha123"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
    "email": "joao@email.com",
    "senha": "minhasenha123"
}
```

**Resposta:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer"
}
```

#### Renovar Token
```bash
GET /auth/refresh
Authorization: Bearer <refresh_token>
```

### 🍽️ **Endpoints de Pedidos**

**⚠️ Todos os endpoints de pedidos requerem autenticação!**

#### Criar Pedido
```bash
POST /pedidos/
Authorization: Bearer <access_token>
```

#### Adicionar Item ao Pedido
```bash
POST /pedidos/{id_pedido}/itens
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "quantidade": 2,
    "sabor": "X-Burger",
    "tamanho": "Grande",
    "preco_unitario": 25.90
}
```

#### Listar Meus Pedidos
```bash
GET /pedidos/meus
Authorization: Bearer <access_token>
```

#### Visualizar Pedido Específico
```bash
GET /pedidos/{id_pedido}
Authorization: Bearer <access_token>
```

#### Cancelar Pedido
```bash
POST /pedidos/{id_pedido}/cancelar
Authorization: Bearer <access_token>
```

#### Finalizar Pedido
```bash
POST /pedidos/{id_pedido}/finalizar
Authorization: Bearer <access_token>
```

## 🔧 Estrutura do Projeto

```
ProjetoFastAPI/
├── alembic/                 # Migrações do banco de dados
├── main.py                  # Aplicação principal FastAPI
├── models.py                # Modelos SQLAlchemy
├── schemas.py               # Schemas Pydantic
├── dependencies.py          # Dependências e funções auxiliares
├── auth_routes.py           # Rotas de autenticação
├── order_routes.py          # Rotas de pedidos
├── requirements.txt         # Dependências Python
├── alembic.ini             # Configuração Alembic
└── banco.db                # Banco SQLite
```

## 🔐 Segurança

### **Autenticação JWT**
- Tokens de acesso expiram em 30 minutos
- Refresh tokens expiram em 7 dias
- Validação automática em todas as rotas protegidas

### **Criptografia**
- Senhas criptografadas com bcrypt
- Hash único para cada usuário
- Proteção contra ataques de força bruta

### **Controle de Acesso**
- Verificação de permissões em cada operação
- Usuários só acessam seus próprios dados
- Administradores têm acesso completo

## 📊 Modelos de Dados

### **Usuário**
- ID único
- Nome completo
- Email único
- Senha criptografada
- Status ativo/inativo
- Privilégios de administrador

### **Pedido**
- ID único
- Usuário proprietário
- Status (PENDENTE, EM_PREPARO, FINALIZADO, CANCELADO)
- Preço total calculado automaticamente
- Lista de itens

### **Item do Pedido**
- ID único
- Quantidade
- Sabor/descrição
- Tamanho
- Preço unitário
- Referência ao pedido

## 🧪 Testando a API

### **1. Usando o Swagger UI (Recomendado)**
1. Acesse `http://localhost:8000/docs`
2. Clique em "Authorize" (🔒) no topo
3. Use `/auth/login-form` para fazer login
4. Teste todos os endpoints diretamente na interface

### **2. Usando cURL**
```bash
# 1. Criar conta
curl -X POST "http://localhost:8000/auth/criar_conta" \
     -H "Content-Type: application/json" \
     -d '{"nome": "Teste", "email": "teste@email.com", "senha": "123456"}'

# 2. Fazer login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "teste@email.com", "senha": "123456"}'

# 3. Usar o token para acessar endpoints protegidos
curl -X GET "http://localhost:8000/pedidos/meus" \
     -H "Authorization: Bearer <seu_token_aqui>"
```

### **3. Usando Postman/Insomnia**
- Importe a coleção do Swagger UI
- Configure a autenticação Bearer Token
- Teste todos os endpoints

## 🚨 Tratamento de Erros

### **Códigos de Status HTTP**
- `200`: Sucesso
- `201`: Criado com sucesso
- `400`: Erro de validação ou regra de negócio
- `401`: Não autenticado
- `403`: Não autorizado
- `404`: Recurso não encontrado
- `500`: Erro interno do servidor

### **Mensagens de Erro**
Todas as mensagens de erro são em português e incluem:
- Descrição clara do problema
- Sugestões de correção
- Códigos de erro específicos

## 🔄 Migrações do Banco

### **Criar nova migração**
```bash
alembic revision --autogenerate -m "descrição da mudança"
```

### **Aplicar migrações**
```bash
alembic upgrade head
```

### **Reverter migração**
```bash
alembic downgrade -1
```

## 🚀 Deploy

### **Desenvolvimento**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Produção**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Docker (futuro)**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

- **Issues**: Use o sistema de issues do GitHub
- **Documentação**: Consulte `/docs` na aplicação rodando
- **Email**: dev@restaurante.com

## 🎯 Roadmap

- [ ] Sistema de notificações
- [ ] Relatórios e analytics
- [ ] Integração com sistemas de pagamento
- [ ] API para aplicativos móveis
- [ ] Sistema de cupons e descontos
- [ ] Dashboard administrativo
- [ ] Testes automatizados
- [ ] CI/CD pipeline

---

**🍽️ Desenvolvido com ❤️ usando FastAPI**

*Última atualização: Dezembro 2024*
