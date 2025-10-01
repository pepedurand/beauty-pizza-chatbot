from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from .tools import resolve_tools


class BeautyPizzaAgent:
    def __init__(self, openai_api_key: str):
        self.model = OpenAIChat(
            id="gpt-4o-mini",
            api_key=openai_api_key,
            temperature=0.7
        )
        
        self.available_tools = [
            "get_menu",
            "get_pizza_info", 
            "get_pizza_price",
            "add_pizza_to_order",
            "get_order_items",
            "get_order_total",
            "update_delivery_address",
            "remove_item_from_order",
            "remember_pizza_offered",
            "create_order",
        ]
        
        self.system_prompt = dedent("""
        Você é Bella, atendente virtual da pizzaria Beauty Pizza.
        Seu objetivo é ajudar o cliente a montar e finalizar o pedido, coletando:
        - pizzas desejadas
        - nome e documento
        - endereço de entrega
        
        IMPORTANTE: Quando todas as informações estiverem completas:
        1. PRIMEIRO mostre um resumo completo do pedido
        2. PERGUNTE se o cliente confirma
        3. SÓ ENTÃO use create_order após confirmação explícita (sim/confirmo/ok/etc)
        
        REGRAS IMPORTANTES:
        - Seja simpática e natural
        - NUNCA chame create_order sem confirmação explícita do cliente
        - Nunca finalize ou crie pedido se faltar alguma dessas informações
        - Valide sabores/tamanhos/bordas antes de adicionar pizzas
        - Ao preencher complement ou reference_point na entrega, se não houver valor, envie string vazia ('')
        """)
        
        self.agent = Agent(
            model=self.model,
            tools=resolve_tools(self.available_tools),
            instructions=self.system_prompt,
            show_tool_calls=False,
            add_history_to_messages=True,  
            num_history_responses=5,  
        )
        
        self.conversation_state = {
            "pizzas": [],
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "awaiting_confirmation": False
        }
    
    def chat(self, message: str) -> str:
        try:
            print("[Bella] Processando mensagem...")
            
            enriched_message = self._enrich_with_business_context(message)
            
            response = self.agent.run(enriched_message)
            
            if self._is_ready_to_finalize() and not self.conversation_state["awaiting_confirmation"]:
                self.conversation_state["awaiting_confirmation"] = True
                print("[Bella] ✅ Todos os dados coletados. Aguardando confirmação...")
            
            return response.content
            
        except Exception as e:
            print(f"[Erro] {e}")
            return f"Desculpe, ocorreu um erro. Pode repetir por favor? (Erro: {str(e)})"
    
    def _enrich_with_business_context(self, message: str) -> str:
        """Adiciona apenas contexto de negócio relevante à mensagem"""
        context_parts = []
        
        if self.conversation_state["pizzas"]:
            context_parts.append(f"[PEDIDO] {len(self.conversation_state['pizzas'])} pizza(s) no carrinho")
        
        if self.conversation_state["client_name"]:
            context_parts.append(f"[CLIENTE] Nome: {self.conversation_state['client_name']}")
        
        if self.conversation_state["client_document"]:
            context_parts.append(f"[CLIENTE] Documento: {self.conversation_state['client_document']}")
        
        if self.conversation_state["delivery_address"]:
            context_parts.append(f"[ENTREGA] Endereço cadastrado")
        
        if self.conversation_state["awaiting_confirmation"]:
            context_parts.append("[STATUS] AGUARDANDO CONFIRMAÇÃO - Só crie o pedido se o cliente confirmar explicitamente!")
        elif self._is_ready_to_finalize():
            context_parts.append("[STATUS] Todas informações coletadas - Mostre resumo e PEÇA CONFIRMAÇÃO antes de criar pedido")
        
        if context_parts:
            return f"{' | '.join(context_parts)}\n\n{message}"
        return message
    
    
    def _is_ready_to_finalize(self) -> bool:
        return (
            self.conversation_state["pizzas"]
            and self.conversation_state["client_name"]
            and self.conversation_state["client_document"]
            and self.conversation_state["delivery_address"]
        )
    
    def reset_conversation(self):
        self.conversation_state = {
            "pizzas": [],
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "awaiting_confirmation": False
        }
        
        print("[Bella] Conversa reiniciada!")