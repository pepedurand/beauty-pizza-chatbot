from textwrap import dedent
from agno import Agent
from agno.models import ChatOpenAI
from typing import Dict, List, Optional

from .tools import resolve_tools


class BeautyPizzaAgent:
    """Agente da pizzaria Beauty Pizza usando Agno."""
    
    def __init__(self, openai_api_key: str):
        """
        Inicializa o agente da Beauty Pizza.
        
        Args:
            openai_api_key: Chave da API do OpenAI
        """
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            temperature=0.7
        )
        
        # Lista de ferramentas disponíveis para o agente
        self.available_tools = [
            "get_menu",
            "get_pizza_info", 
            "get_pizza_price",
            "create_order",
            "add_pizza_to_order",
            "get_order_items",
            "get_order_total",
            "update_delivery_address",
            "remove_item_from_order",
            "update_item_quantity"
        ]
        
        self.system_prompt = dedent("""
            Você é um atendente virtual da pizzaria "Beauty Pizza". Seu nome é Bella e você é muito simpática, 
            atenciosa e sempre disposta a ajudar os clientes.

            SUAS RESPONSABILIDADES:
            1. Cumprimentar os clientes de forma calorosa e apresentar a pizzaria
            2. Apresentar o cardápio quando solicitado ou no início da conversa
            3. Responder perguntas sobre ingredientes, sabores, tamanhos, bordas e preços
            4. Ajudar o cliente a fazer seu pedido completo
            5. Gerenciar pedidos: adicionar itens, calcular totais, atualizar quantidades
            6. Coletar informações de entrega (endereço completo)
            7. Manter o histórico da conversa e do pedido atual

            DIRETRIZES DE COMPORTAMENTO:
            - Seja sempre educada, simpática e prestativa
            - Use linguagem natural e amigável 
            - Faça perguntas para esclarecer dúvidas do cliente
            - Sugira pizzas populares ou promoções quando apropriado
            - Confirme os dados do pedido antes de finalizar
            - Mantenha o controle do estado da conversa

            INFORMAÇÕES IMPORTANTES:
            - A pizzaria se chama "Beauty Pizza"
            - Você tem acesso ao cardápio completo via ferramentas
            - Pode criar e gerenciar pedidos via API
            - Sempre confirme detalhes importantes com o cliente
            - Use as ferramentas disponíveis para consultar preços e informações

            FLUXO TÍPICO DE ATENDIMENTO:
            1. Cumprimento inicial
            2. Apresentação do cardápio ou resposta a perguntas
            3. Coleta de dados do cliente (nome, documento)
            4. Criação do pedido
            5. Adição de itens (pizzas) ao pedido
            6. Coleta do endereço de entrega
            7. Confirmação final e total do pedido

            Lembre-se: você deve usar as ferramentas disponíveis para acessar informações do cardápio 
            e gerenciar pedidos. Nunca invente preços ou informações - sempre consulte via ferramentas.
        """)
        
        self.agent = Agent(
            model=self.model,
            tools=resolve_tools(self.available_tools),
            system_prompt=self.system_prompt,
            max_loops=10,
            show_tool_calls=True
        )
        
        # Estado da conversa
        self.conversation_state = {
            "current_order_id": None,
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "conversation_history": []
        }
    
    def chat(self, message: str) -> str:
        """
        Processa uma mensagem do cliente e retorna a resposta.
        
        Args:
            message: Mensagem do cliente
            
        Returns:
            Resposta do agente
        """
        try:
            # Adicionar contexto do estado atual se necessário
            context_message = self._build_context_message(message)
            
            # Processar com o agente
            response = self.agent.run(context_message)
            
            # Atualizar histórico
            self.conversation_state["conversation_history"].append({
                "user": message,
                "agent": response.content
            })
            
            return response.content
            
        except Exception as e:
            error_msg = f"Desculpe, ocorreu um erro inesperado. Tente novamente. (Erro: {str(e)})"
            return error_msg
    
    def _build_context_message(self, message: str) -> str:
        """Constrói mensagem com contexto do estado atual."""
        context_parts = [message]
        
        # Adicionar contexto do pedido atual se existe
        if self.conversation_state["current_order_id"]:
            context_parts.append(f"\n[CONTEXTO] Pedido atual ID: {self.conversation_state['current_order_id']}")
        
        if self.conversation_state["client_name"]:
            context_parts.append(f"Cliente: {self.conversation_state['client_name']}")
        
        return "\n".join(context_parts)
    
    def reset_conversation(self):
        """Reinicia o estado da conversa."""
        self.conversation_state = {
            "current_order_id": None,
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "conversation_history": []
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Retorna o histórico da conversa."""
        return self.conversation_state["conversation_history"]
    
    def update_client_info(self, name: str = None, document: str = None):
        """Atualiza informações do cliente no estado."""
        if name:
            self.conversation_state["client_name"] = name
        if document:
            self.conversation_state["client_document"] = document
    
    def set_current_order(self, order_id: int):
        """Define o ID do pedido atual."""
        self.conversation_state["current_order_id"] = order_id