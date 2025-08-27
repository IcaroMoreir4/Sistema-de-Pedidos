from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token
from models import ItemPedido, Pedido, Usuario
from schemas import ItemPedidoSchema, ResponsePedidoSchema

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])


async def obter_pedido_autorizado(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
) -> Pedido:
    """
    Dependência para obter um pedido e verificar se o usuário logado
    tem permissão para acessá-lo (se é o dono ou um admin).
    Retorna o objeto do pedido se a autorização for bem-sucedida.
    """
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem autorização para realizar esta ação")

    return pedido


async def obter_item_pedido_autorizado(
    id_item_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
) -> ItemPedido:
    """
    Dependência para obter um item de pedido e verificar se o usuário logado
    tem permissão para modificá-lo (se é o dono do pedido ou um admin).
    """
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()

    if not item_pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de pedido não encontrado")

    # Acessa o pedido associado ao item para verificação de permissão
    pedido_do_item = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()

    if not usuario.admin and usuario.id != pedido_do_item.usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem autorização para realizar esta ação")

    return item_pedido


@order_router.get("/", response_model=List[ResponsePedidoSchema], summary="Listar todos os pedidos (Admin)")
async def listar_todos_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    ## 👑 Listagem de Todos os Pedidos (Apenas Administradores)
    
    **O que faz:** Retorna uma lista completa de todos os pedidos existentes no sistema.
    
    **🔒 Acesso:** 
    - **Restrito apenas a administradores autenticados**
    - Usuários comuns não podem acessar esta rota
    
    **Parâmetros:**
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    
    **Resposta:** Lista de todos os pedidos com detalhes completos
    
    **Estrutura da resposta:**
    ```json
    [
        {
            "id": 1,
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
    ]
    ```
    
    **Possíveis erros:**
    - `401`: Token de autenticação inválido ou ausente
    - `403`: Usuário logado não é administrador
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/pedidos/" \
         -H "Authorization: Bearer <seu_token_admin>"
    ```
    
    **⚠️ Importante:** Esta rota é útil para administradores monitorarem todos os pedidos do sistema.
    """
    if not usuario.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem autorização para acessar esta rota")
    
    pedidos = session.query(Pedido).all()
    return pedidos


@order_router.post("/", response_model=ResponsePedidoSchema, status_code=status.HTTP_201_CREATED, summary="Criar um novo pedido")
async def criar_pedido(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    """
    ## 🆕 Criação de Novo Pedido
    
    **O que faz:** Cria um novo pedido vazio para o usuário autenticado.
    
    **🔑 Características:**
    - O ID do usuário é obtido automaticamente do token de autenticação
    - O pedido é criado com status "PENDENTE" por padrão
    - Preço inicial é 0.00 (será calculado quando itens forem adicionados)
    
    **Parâmetros:**
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    - **Body:** Nenhum (endpoint sem parâmetros no corpo)
    
    **Resposta de sucesso:**
    ```json
    {
        "id": 123,
        "status": "PENDENTE",
        "preco": 0.0,
        "itens": []
    }
    ```
    
    **Fluxo de uso típico:**
    1. Crie um pedido vazio (este endpoint)
    2. Adicione itens usando `/pedidos/{id}/itens`
    3. O preço será calculado automaticamente
    
    **Possíveis erros:**
    - `401`: Token de autenticação inválido ou ausente
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/pedidos/" \
         -H "Authorization: Bearer <seu_token>"
    ```
    
    **💡 Dica:** Após criar o pedido, use o ID retornado para adicionar itens.
    """
    novo_pedido = Pedido(usuario=usuario.id)
    session.add(novo_pedido)
    session.commit()
    session.refresh(novo_pedido)
    return novo_pedido


@order_router.get("/meus", response_model=List[ResponsePedidoSchema], summary="Listar meus pedidos")
async def listar_meus_pedidos(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    """
    ## 👤 Listagem dos Meus Pedidos
    
    **O que faz:** Retorna todos os pedidos feitos pelo usuário autenticado.
    
    **🔍 Filtro automático:**
    - Mostra apenas pedidos onde `usuario_id` = ID do usuário logado
    - Administradores veem apenas seus próprios pedidos nesta rota
    - Para ver todos os pedidos, administradores devem usar `/pedidos/`
    
    **Parâmetros:**
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    
    **Resposta:** Lista de pedidos do usuário logado
    
    **Estrutura da resposta:**
    ```json
    [
        {
            "id": 1,
            "status": "FINALIZADO",
            "preco": 67.80,
            "itens": [
                {
                    "quantidade": 1,
                    "sabor": "X-Burger",
                    "tamanho": "Família",
                    "preco_unitario": 45.90
                },
                {
                    "quantidade": 2,
                    "sabor": "Refrigerante",
                    "tamanho": "Lata",
                    "preco_unitario": 10.95
                }
            ]
        }
    ]
    ```
    
    **Possíveis erros:**
    - `401`: Token de autenticação inválido ou ausente
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/pedidos/meus" \
         -H "Authorization: Bearer <seu_token>"
    ```
    
    **💡 Dica:** Esta é a rota ideal para usuários acompanharem o histórico de seus pedidos.
    """
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return pedidos


@order_router.get("/{id_pedido}", response_model=ResponsePedidoSchema, summary="Visualizar um pedido específico")
async def visualizar_pedido(pedido: Pedido = Depends(obter_pedido_autorizado)):
    """
    ## 👁️ Visualização de Pedido Específico
    
    **O que faz:** Retorna os detalhes completos de um pedido específico.
    
    **🔐 Controle de acesso:**
    - **Dono do pedido:** Pode visualizar seus próprios pedidos
    - **Administradores:** Podem visualizar qualquer pedido
    - **Outros usuários:** Acesso negado
    
    **Parâmetros:**
    - **Path:** `id_pedido` (integer) - ID único do pedido
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    
    **Resposta:** Detalhes completos do pedido solicitado
    
    **Estrutura da resposta:**
    ```json
    {
        "id": 123,
        "status": "EM_PREPARO",
        "preco": 89.50,
        "itens": [
            {
                "quantidade": 2,
                "sabor": "X-Bacon",
                "tamanho": "Família",
                "preco_unitario": 44.75
            }
        ]
    }
    ```
    
    **Possíveis erros:**
    - `401`: Token de autenticação inválido ou ausente
    - `403`: Usuário não tem permissão para acessar este pedido
    - `404`: Pedido não encontrado
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/pedidos/123" \
         -H "Authorization: Bearer <seu_token>"
    ```
    
    **💡 Dica:** Use esta rota para verificar o status e detalhes de um pedido específico.
    """
    return pedido


@order_router.post("/{id_pedido}/cancelar", response_model=ResponsePedidoSchema, summary="Cancelar um pedido")
async def cancelar_pedido(pedido: Pedido = Depends(obter_pedido_autorizado), session: Session = Depends(pegar_sessao)):
    """
    ## ❌ Cancelamento de Pedido
    
    **O que faz:** Altera o status de um pedido para "CANCELADO".
    
    **📋 Regras de cancelamento:**
    - **Status permitidos para cancelamento:** `PENDENTE`, `EM_PREPARO`
    - **Status que NÃO podem ser cancelados:** `FINALIZADO`, `CANCELADO`
    
    **🔐 Controle de acesso:**
    - **Dono do pedido:** Pode cancelar seus próprios pedidos
    - **Administradores:** Podem cancelar qualquer pedido
    
    **Parâmetros:**
    - **Path:** `id_pedido` (integer) - ID do pedido a ser cancelado
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    
    **Resposta:** Pedido atualizado com status "CANCELADO"
    
    **Possíveis erros:**
    - `400`: Pedido não pode ser cancelado (status inválido)
    - `401`: Token de autenticação inválido ou ausente
    - `403`: Usuário não tem permissão para cancelar este pedido
    - `404`: Pedido não encontrado
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/pedidos/123/cancelar" \
         -H "Authorization: Bearer <seu_token>"
    ```
    
    **⚠️ Importante:** Cancelamentos são irreversíveis. Considere bem antes de cancelar um pedido.
    """
    if pedido.status not in ["PENDENTE", "EM_PREPARO"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Não é possível cancelar um pedido com status '{pedido.status}'")
    
    pedido.status = "CANCELADO"
    session.commit()
    session.refresh(pedido)
    return pedido


@order_router.post("/{id_pedido}/finalizar", response_model=ResponsePedidoSchema, summary="Finalizar um pedido")
async def finalizar_pedido(pedido: Pedido = Depends(obter_pedido_autorizado), session: Session = Depends(pegar_sessao)):
    """
    ## ✅ Finalização de Pedido
    
    **O que faz:** Altera o status de um pedido para "FINALIZADO".
    
    **📋 Regras de finalização:**
    - **Status permitido para finalização:** `EM_PREPARO` apenas
    - **Status que NÃO podem ser finalizados:** `PENDENTE`, `CANCELADO`, `FINALIZADO`
    
    **🔐 Controle de acesso:**
    - **Dono do pedido:** Pode finalizar seus próprios pedidos
    - **Administradores:** Podem finalizar qualquer pedido
    
    **Parâmetros:**
    - **Path:** `id_pedido` (integer) - ID do pedido a ser finalizado
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    
    **Resposta:** Pedido atualizado com status "FINALIZADO"
    
    **Possíveis erros:**
    - `400`: Pedido não pode ser finalizado (status inválido)
    - `401`: Token de autenticação inválido ou ausente
    - `403`: Usuário não tem permissão para finalizar este pedido
    - `404`: Pedido não encontrado
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/pedidos/123/finalizar" \
         -H "Authorization: Bearer <seu_token>"
    ```
    
    **💡 Dica:** Use esta rota quando o pedido estiver pronto para entrega.
    """
    if pedido.status != "EM_PREPARO":
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Só é possível finalizar um pedido com status 'EM_PREPARO'")

    pedido.status = "FINALIZADO"
    session.commit()
    session.refresh(pedido)
    return pedido


@order_router.post("/{id_pedido}/itens", response_model=ResponsePedidoSchema, summary="Adicionar item a um pedido")
async def adicionar_item_pedido(
    item_schema: ItemPedidoSchema,
    pedido: Pedido = Depends(obter_pedido_autorizado),
    session: Session = Depends(pegar_sessao)
):
    """
    ## ➕ Adição de Item ao Pedido
    
    **O que faz:** Adiciona um novo item (lanche, bebida, etc.) a um pedido existente.
    
    **🔢 Cálculo automático:**
    - O preço total do pedido é recalculado automaticamente
    - Preço = Soma de (quantidade × preço_unitario) de todos os itens
    
    **🔐 Controle de acesso:**
    - **Dono do pedido:** Pode adicionar itens aos seus pedidos
    - **Administradores:** Podem adicionar itens a qualquer pedido
    
    **Parâmetros:**
    - **Path:** `id_pedido` (integer) - ID do pedido
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    - **Body (JSON):**
        ```json
        {
            "quantidade": 2,
            "sabor": "X-Burger",
            "tamanho": "Grande",
            "preco_unitario": 25.90
        }
        ```
    
    **Campos do item:**
    - `quantidade` (integer): Quantidade do item (obrigatório)
    - `sabor` (string): Nome/descrição do item (obrigatório)
    - `tamanho` (string): Tamanho do item (obrigatório)
    - `preco_unitario` (float): Preço por unidade (obrigatório)
    
    **Resposta:** Pedido atualizado com o novo item e preço recalculado
    
    **Possíveis erros:**
    - `401`: Token de autenticação inválido ou ausente
    - `403`: Usuário não tem permissão para modificar este pedido
    - `404`: Pedido não encontrado
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/pedidos/123/itens" \
         -H "Authorization: Bearer <seu_token>" \
         -H "Content-Type: application/json" \
         -d '{
             "quantidade": 1,
             "sabor": "X-Bacon",
             "tamanho": "Média",
             "preco_unitario": 22.50
         }'
    ```
    
    **💡 Dica:** Você pode adicionar múltiplos itens ao mesmo pedido chamando este endpoint várias vezes.
    """
    item_pedido = ItemPedido(
        quantidade=item_schema.quantidade,
        sabor=item_schema.sabor,
        tamanho=item_schema.tamanho,
        preco_unitario=item_schema.preco_unitario,
        pedido=pedido.id
    )
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    session.refresh(pedido)
    return pedido


@order_router.delete("/itens/{id_item_pedido}", response_model=ResponsePedidoSchema, summary="Remover item de um pedido")
async def remover_item_pedido(
    item_pedido: ItemPedido = Depends(obter_item_pedido_autorizado),
    session: Session = Depends(pegar_sessao)
):
    """
    ## ➖ Remoção de Item do Pedido
    
    **O que faz:** Remove um item específico de um pedido.
    
    **🔢 Cálculo automático:**
    - O preço total do pedido é recalculado automaticamente após a remoção
    - Preço = Soma de (quantidade × preço_unitário) dos itens restantes
    
    **🔐 Controle de acesso:**
    - **Dono do pedido:** Pode remover itens dos seus pedidos
    - **Administradores:** Podem remover itens de qualquer pedido
    
    **Parâmetros:**
    - **Path:** `id_item_pedido` (integer) - ID único do item a ser removido
    - **Header obrigatório:** `Authorization: Bearer <access_token>`
    
    **Resposta:** Pedido atualizado sem o item removido e preço recalculado
    
    **Possíveis erros:**
    - `401`: Token de autenticação inválido ou ausente
    - `403`: Usuário não tem permissão para modificar este pedido
    - `404`: Item de pedido não encontrado
    
    **Exemplo de uso:**
    ```bash
    curl -X DELETE "http://localhost:8000/pedidos/itens/456" \
         -H "Authorization: Bearer <seu_token>"
    ```
    
    **⚠️ Importante:** A remoção é permanente e não pode ser desfeita.
    
    **💡 Dica:** Use esta rota para corrigir pedidos com itens incorretos ou para cancelar itens específicos.
    """
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    session.refresh(pedido)
    return pedido