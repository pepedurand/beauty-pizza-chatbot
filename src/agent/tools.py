from agno.tools import tool
from typing import List, Dict
from datetime import datetime, date
from integrations import OrderAPI, KnowledgeBase


TOOLS_REGISTRY = {}

def tool_register(name: str = None, description: str = None):
    def decorator(func):
        key = name or func.__name__

        wrapped_func = tool(
            name=key,
            description=description,
            show_result=False, 
            stop_after_tool_call=False
        )(func)

        TOOLS_REGISTRY[key] = wrapped_func
        return func
    return decorator

def resolve_tools(tool_names: List[str] = None):
    if tool_names is None:
        return []
    return [TOOLS_REGISTRY[name] for name in tool_names if name and name in TOOLS_REGISTRY]


knowledge_base = KnowledgeBase()
order_api = OrderAPI()


@tool_register(
    name="get_menu",
    description="Retorna o cardápio completo da pizzaria com todas as pizzas disponíveis, sabores, ingredientes e descrições"
)
def get_menu() -> Dict:
    try:
        print("[Bella] Buscando informações do cardápio no banco de dados...")
        pizzas = knowledge_base.get_all_pizzas()
        sizes = knowledge_base.get_sizes()
        crusts = knowledge_base.get_crusts()
        print("[Bella] Cardápio recuperado com sucesso.")
        return {
            "pizzas": pizzas,
            "tamanhos": sizes,
            "bordas": crusts
        }
    except Exception as e:
        print(f"[Bella] Erro ao buscar cardápio: {e}")
        return {"erro": f"Não foi possível obter o cardápio: {str(e)}"}


@tool_register(
    name="get_pizza_info",
    description="Retorna informações detalhadas de uma pizza específica pelo sabor, incluindo ingredientes, descrição e preços por tamanho e borda"
)
def get_pizza_info(sabor: str) -> Dict:
    try:
        print(f"[Bella] Buscando informações da pizza '{sabor}' no banco de dados...")
        pizza = knowledge_base.get_pizza_by_flavor(sabor)
        if not pizza:
            print(f"[Bella] Pizza '{sabor}' não encontrada.")
            return {"erro": f"Pizza com sabor '{sabor}' não encontrada no cardápio"}
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
        print(f"[Bella] Informações da pizza '{sabor}' recuperadas.")
        return {
            "pizza": pizza,
            "precos": precos
        }
    except Exception as e:
        print(f"[Bella] Erro ao buscar informações da pizza: {e}")
        return {"erro": f"Erro ao buscar informações da pizza: {str(e)}"}


@tool_register(
    name="create_order",
    description="Cria um novo pedido para o cliente após confirmação explícita. Retorna o código do pedido criado. IMPORTANTE: Informe ao cliente o código do pedido no formato 'Pedido #XXXXX criado com sucesso!'"
)
def create_order(client_name: str, client_document: str, delivery_date: str = None) -> Dict:
    try:
        print("[Bella] Chamando a API de pedidos para criar um novo pedido...")
        today_str = date.today().strftime('%Y-%m-%d')
        safe_delivery_date = today_str
        if delivery_date:
            try:
                parsed_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                if parsed_date >= date.today():
                    safe_delivery_date = parsed_date.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass

        existing_orders = order_api.filter_orders_by_document(client_document, delivery_date=safe_delivery_date)

        if existing_orders and isinstance(existing_orders, list) and len(existing_orders) > 0:
            latest_order = max(existing_orders, key=lambda o: o.get('id', 0))
            status = order_api.get_status_order(latest_order['id'])
            if status.get('status') != 'finalizado':
                latest_order['status_beauty'] = 'existing'
                order_id = latest_order.get('id')
                latest_order['mensagem_pedido'] = f"🎉 Pedido #{order_id} recuperado! Informe este código ao cliente."
                return latest_order

        new_order = order_api.create_order(client_name, client_document, safe_delivery_date)
        new_order['status_beauty'] = 'created'
        order_id = new_order.get('id')
        new_order['mensagem_pedido'] = f"🎉 Pedido #{order_id} criado com sucesso! Informe este código ao cliente."
        return new_order
    except Exception as e:
        return {"erro": f"Não foi possível criar ou verificar o pedido: {str(e)}"}


@tool_register(
    name="add_pizza_to_order",
    description="Adiciona uma pizza ao pedido especificando o ID do pedido, sabor, tamanho, borda e quantidade"
)
def add_pizza_to_order(order_id: int, pizza_flavor: str, size: str, 
                      crust: str, quantity: int = 1) -> Dict:
    try:
        pizza_info = knowledge_base.get_pizza_with_price(pizza_flavor, size, crust)
        if not pizza_info:
            return {"erro": f"Não foi possível encontrar preço para pizza {pizza_flavor}, tamanho {size}, borda {crust}"}
        
        unit_price = pizza_info['preco']
        
        return order_api.add_item_to_order(order_id, pizza_flavor, size, crust, quantity, unit_price)
    except Exception as e:
        return {"erro": f"Não foi possível adicionar pizza ao pedido: {str(e)}"}


@tool_register(
    name="get_order_total",
    description="Calcula e retorna o valor total do pedido pelo ID"
)
def get_order_total(order_id: int) -> Dict:
    try:
        return order_api.get_order_total(order_id)
    except Exception as e:
        return {"erro": f"Não foi possível calcular o total do pedido: {str(e)}"}


@tool_register(
    name="get_order_items",
    description="Lista todos os itens (pizzas) que já foram adicionados ao pedido"
)
def get_order_items(order_id: int) -> Dict:
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
    try:
        return order_api.delete_order_item(order_id, item_id)
    except Exception as e:
        return {"erro": f"Não foi possível remover item do pedido: {str(e)}"}


@tool_register(
    name="remember_pizza_offered",
    description="Registra uma pizza que foi oferecida ao cliente com preço, para manter contexto da conversa"
)
def remember_pizza_offered(sabor: str, tamanho: str, borda: str, preco: float) -> Dict:
    try:
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


