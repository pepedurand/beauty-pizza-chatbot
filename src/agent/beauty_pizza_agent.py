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
        
        Quando todas essas informações estiverem completas, confirme com o cliente e só então finalize o pedido usando a ferramenta create_order.
        
        REGRAS IMPORTANTES:
        - Seja simpática e natural
        - Mantenha o contexto da conversa
        - Nunca finalize ou crie pedido se faltar alguma dessas informações
        - Valide sabores/tamanhos/bordas antes de adicionar pizzas
        - Ao preencher complement ou reference_point na entrega, se não houver valor, envie string vazia ('')
        """)
        
        self.agent = Agent(
            model=self.model,
            tools=resolve_tools(self.available_tools),
            instructions=self.system_prompt,
            show_tool_calls=False
        )
        
        self.conversation_state = {
            "pizzas": [],
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "conversation_history": [],
            "current_order_id": None,
            "pizza_in_consideration": None
        }
    
    def chat(self, message: str) -> str:
     
        try:
            print("[Bella] Processando mensagem...")
            
            full_context = self._build_full_context(message)
            
            response = self.agent.run(full_context)
            
            self.conversation_state["conversation_history"].append({
                "user": message,
                "agent": response.content
            })
            
            
            if self._is_ready_to_finalize():
                print("[Bella] ✅ Todos os dados coletados. Pronta para finalizar!")
            
            return response.content
            
        except Exception as e:
            print(f"[Erro] {e}")
            return f"Desculpe, ocorreu um erro. Pode repetir por favor? (Erro: {str(e)})"
    
    def _build_full_context(self, message: str) -> str:
        context_parts = []
        
        history = self.conversation_state["conversation_history"]
        if history:
            context_parts.append("\n[HISTÓRICO DA CONVERSA]")
            recent_history = history[-5:] if len(history) > 5 else history
            for h in recent_history:
                context_parts.append(f"Cliente: {h['user']}")
                context_parts.append(f"Bella: {h['agent']}")
        
        if self.conversation_state["pizza_in_consideration"]:
            pizza_info = self.conversation_state["pizza_in_consideration"]
            context_parts.append(f"\n[CONTEXTO] Pizza em consideração: {pizza_info}")
        
        if self.conversation_state["pizzas"]:
            context_parts.append(f"[CONTEXTO] Pizzas no pedido: {self.conversation_state['pizzas']}")
        if self.conversation_state["client_name"]:
            context_parts.append(f"[CONTEXTO] Nome: {self.conversation_state['client_name']}")
        if self.conversation_state["client_document"]:
            context_parts.append(f"[CONTEXTO] Documento: {self.conversation_state['client_document']}")
        if self.conversation_state["delivery_address"]:
            context_parts.append(f"[CONTEXTO] Endereço: {self.conversation_state['delivery_address']}")
        
        context_parts.append(f"\n[MENSAGEM ATUAL] {message}")
        
        return "\n".join(context_parts)
    
    
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
            "conversation_history": [],
            "current_order_id": None,
            "pizza_in_consideration": None
        }
        
        print("[Bella] Conversa reiniciada!")