from textwrap import dedent
from agno.tools import tool
from typing import List, Dict, Optional
from datetime import datetime, date
from beauty_pizza_chatbot.integrations import OrderAPI, KnowledgeBase


TOOLS_REGISTRY = {}

def tool_register(name: str = None, description: str = None):
    """Decorator para registrar ferramentas do agente."""
    def decorator(func):
        key = name or func.__name__

        wrapped_func = tool(
            name=key,
            description=description,
            show_result=True, 
            stop_after_tool_call=False
        )(func)

        TOOLS_REGISTRY[key] = wrapped_func
        return func
    return decorator

def resolve_tools(tool_names: List[str] = None):
    """Resolve as ferramentas pelos nomes."""
    if tool_names is None:
        return []
    return [TOOLS_REGISTRY[name] for name in tool_names if name and name in TOOLS_REGISTRY]


# Instâncias globais para usar nas ferramentas
knowledge_base = KnowledgeBase()
order_api = OrderAPI()


@tool_register(
    name="get_menu",
    description="Retorna o cardápio completo da pizzaria com todas as pizzas disponíveis, sabores, ingredientes e descrições"
)
def get_menu() -> Dict:
    """Obtém o cardápio completo da pizzaria."""
    try:
        pizzas = knowledge_base.get_all_pizzas()
        sizes = knowledge_base.get_sizes()
        crusts = knowledge_base.get_crusts()
        
        return {
            "pizzas": pizzas,
            "tamanhos": sizes,
            "bordas": crusts
        }
    except Exception as e:
        return {"erro": f"Não foi possível obter o cardápio: {str(e)}"}


@tool_register(
    name="get_pizza_info",
    description="Retorna informações detalhadas de uma pizza específica pelo sabor, incluindo ingredientes, descrição e preços por tamanho e borda"
)
def get_pizza_info(sabor: str) -> Dict:
    """Obtém informações detalhadas de uma pizza específica."""
    try:
        pizza = knowledge_base.get_pizza_by_flavor(sabor)
        if not pizza:
            return {"erro": f"Pizza com sabor '{sabor}' não encontrada no cardápio"}
        
        # Buscar preços para todos os tamanhos e bordas
        sizes = knowledge_base.get_sizes()
        crusts = knowledge_base.get_crusts()
        precos = []
        
        for size in sizes:
            for crust in crusts:
                preco = knowledge_base.get_price(pizza['id'], size['id'], crust['id'])
                if preco:
                    precos.append({
                        "tamanho": size['tamanho'],
                        "borda": crust['tipo'],
                        "preco": preco
                    })
        
        return {
            "pizza": pizza,
            "precos": precos
        }
    except Exception as e:
        return {"erro": f"Erro ao buscar informações da pizza: {str(e)}"}


@tool_register(
    name="create_order",
    description="Cria um novo pedido para o cliente com nome, documento. A data de entrega será automaticamente definida para hoje se não especificada."
)
def create_order(client_name: str, client_document: str, delivery_date: str = None) -> Dict:
    """Cria um novo pedido."""
    try:
        # Se não foi fornecida data ou a data é muito antiga, usar data atual
        if not delivery_date:
            delivery_date = date.today().strftime('%Y-%m-%d')
        else:
            # Validar se a data não está no passado
            try:
                parsed_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                if parsed_date < date.today():
                    delivery_date = date.today().strftime('%Y-%m-%d')
            except ValueError:
                delivery_date = date.today().strftime('%Y-%m-%d')
                
        return order_api.create_order(client_name, client_document, delivery_date)
    except Exception as e:
        return {"erro": f"Não foi possível criar o pedido: {str(e)}"}


@tool_register(
    name="add_pizza_to_order",
    description="Adiciona uma pizza ao pedido especificando o ID do pedido, sabor, tamanho, borda e quantidade"
)
def add_pizza_to_order(order_id: int, pizza_flavor: str, size: str, 
                      crust: str, quantity: int = 1) -> Dict:
    """Adiciona uma pizza ao pedido."""
    try:
        return order_api.add_item_to_order(order_id, pizza_flavor, size, crust, quantity)
    except Exception as e:
        return {"erro": f"Não foi possível adicionar pizza ao pedido: {str(e)}"}


@tool_register(
    name="get_order_total",
    description="Calcula e retorna o valor total do pedido pelo ID"
)
def get_order_total(order_id: int) -> Dict:
    """Obtém o valor total do pedido."""
    try:
        return order_api.get_order_total(order_id)
    except Exception as e:
        return {"erro": f"Não foi possível calcular o total do pedido: {str(e)}"}


@tool_register(
    name="get_order_items",
    description="Lista todos os itens (pizzas) que já foram adicionados ao pedido"
)
def get_order_items(order_id: int) -> Dict:
    """Lista os itens do pedido."""
    try:
        items = order_api.get_order_items(order_id)
        return {"items": items}
    except Exception as e:
        return {"erro": f"Não foi possível obter os itens do pedido: {str(e)}"}


@tool_register(
    name="update_delivery_address",
    description="Atualiza o endereço de entrega do pedido com rua, número, complemento e ponto de referência"
)
def update_delivery_address(order_id: int, street_name: str, number: str, 
                          complement: str = None, reference_point: str = None) -> Dict:
    """Atualiza o endereço de entrega."""
    try:
        return order_api.update_delivery_address(
            order_id, street_name, number, complement, reference_point
        )
    except Exception as e:
        return {"erro": f"Não foi possível atualizar o endereço: {str(e)}"}


@tool_register(
    name="get_pizza_price",
    description="Retorna o preço específico de uma pizza com sabor, tamanho e borda específicos"
)
def get_pizza_price(sabor: str, tamanho: str, borda: str) -> Dict:
    """Obtém o preço de uma pizza específica."""
    try:
        pizza_info = knowledge_base.get_pizza_with_price(sabor, tamanho, borda)
        if not pizza_info:
            return {"erro": f"Não foi possível encontrar preço para pizza {sabor}, tamanho {tamanho}, borda {borda}"}
        
        return {
            "sabor": pizza_info['sabor'],
            "tamanho": pizza_info['tamanho'],
            "borda": pizza_info['borda'],
            "preco": pizza_info['preco']
        }
    except Exception as e:
        return {"erro": f"Erro ao buscar preço da pizza: {str(e)}"}


@tool_register(
    name="remove_item_from_order",
    description="Remove um item específico do pedido pelo ID do item"
)
def remove_item_from_order(order_id: int, item_id: int) -> Dict:
    """Remove um item do pedido."""
    try:
        return order_api.delete_order_item(order_id, item_id)
    except Exception as e:
        return {"erro": f"Não foi possível remover item do pedido: {str(e)}"}


@tool_register(
    name="update_item_quantity",
    description="Atualiza a quantidade de um item específico no pedido"
)
def update_item_quantity(order_id: int, item_id: int, quantity: int) -> Dict:
    """Atualiza a quantidade de um item no pedido."""
    try:
        return order_api.update_order_item(order_id, item_id, quantity)
    except Exception as e:
        return {"erro": f"Não foi possível atualizar quantidade do item: {str(e)}"}


@tool_register(
    name="remember_pizza_offered",
    description="Registra uma pizza que foi oferecida ao cliente com preço, para manter contexto da conversa"
)
def remember_pizza_offered(sabor: str, tamanho: str, borda: str, preco: float) -> Dict:
    """Registra uma pizza oferecida para manter contexto."""
    try:
        # Esta é uma ferramenta de contexto - não faz nada externamente
        # Apenas confirma que a informação foi registrada
        return {
            "status": "registrado",
            "pizza": {
                "sabor": sabor,
                "tamanho": tamanho,
                "borda": borda,
                "preco": preco
            },
            "mensagem": f"Pizza {sabor} {tamanho} com borda {borda} por R$ {preco} registrada como oferecida ao cliente"
        }
    except Exception as e:
        return {"erro": f"Erro ao registrar pizza oferecida: {str(e)}"}