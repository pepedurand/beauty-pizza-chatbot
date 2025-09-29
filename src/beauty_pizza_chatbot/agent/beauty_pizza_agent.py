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
            "create_order",
            "add_pizza_to_order",
            "get_order_items",
            "get_order_total",
            "update_delivery_address",
            "remove_item_from_order",
            "remember_pizza_offered",
            "finalize_order"
        ]
        
        self.system_prompt = dedent("""
            Você é Bella, atendente virtual da pizzaria Beauty Pizza: simpática, educada e prestativa.

            ### RESPONSABILIDADES
            1. Cumprimentar e apresentar a pizzaria
            2. Mostrar cardápio (no início ou quando solicitado)
            3. Responder dúvidas sobre sabores, ingredientes, tamanhos, bordas e preços
            4. Ajudar o cliente a montar o pedido
            5. Gerenciar itens (adicionar, remover, atualizar, calcular total)
            6. Coletar informações de entrega (nome, documento, endereço)
            7. Manter continuidade da conversa usando o histórico
            8. Apenas ofereça pizzas, outros itens não estão disponíveis como bebidas, sanduíches e etc

            ### COMPORTAMENTO
            - Linguagem natural, calorosa e amigável
            - Confirme sempre detalhes importantes
            - Sugira opções populares ou promoções quando fizer sentido
            - Nunca invente itens fora do cardápio
            - Se cliente disser “sim/quero/vou querer”, refere-se à última pizza discutida

            ### REGRAS DE PEDIDO
            - Crie o pedido apenas uma vez (`create_order`).  
            - Se já existir pedido, continue nele (`current_order_id`).  
            - Antes de `add_pizza_to_order`, valide sabor/tamanho/borda com `get_pizza_info` ou `get_pizza_price`.  
            - Não adicione itens inexistentes — ofereça opções válidas.
            - Para finalizar (`finalize_order`), confirme: nome, documento, endereço, itens e total.  
            - Se faltar algo, peça educadamente.

            ### FLUXO RESUMIDO
            1. Cliente demonstra interesse → crie/recupere pedido
            2. Valide e adicione pizza discutida
            3. Pergunte se deseja mais algo
            4. Colete endereço
            5. Confirme tudo → finalize
            """
        )
        
        self.agent = Agent(
            model=self.model,
            tools=resolve_tools(self.available_tools),
            instructions=self.system_prompt,
            show_tool_calls=False
        )
        
        self.conversation_state = {
            "current_order_id": None,
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "conversation_history": [],
            "pizza_in_consideration": None,  
            "current_step": "greeting"  
        }
    
    def chat(self, message: str) -> str:
        try:
            full_context = self._build_full_context(message)
            
            response = self.agent.run(full_context)
            
            self.conversation_state["conversation_history"].append({
                "user": message,
                "agent": response.content
            })
            
            self._extract_context_from_response(message, response.content)
            
            return response.content
            
        except Exception as e:
            error_msg = f"Desculpe, ocorreu um erro inesperado. Tente novamente. (Erro: {str(e)})"
            return error_msg
    
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
            context_parts.append(f"\n[CONTEXTO IMPORTANTE] Pizza em consideração: {pizza_info['sabor']} {pizza_info['tamanho']} com borda {pizza_info['borda']} por R$ {pizza_info['preco']}")
        
        if self.conversation_state["current_order_id"]:
            context_parts.append(f"[CONTEXTO] Pedido atual ID: {self.conversation_state['current_order_id']}")
        
        if self.conversation_state["client_name"]:
            context_parts.append(f"[CONTEXTO] Cliente: {self.conversation_state['client_name']}")
        
        context_parts.append(f"\n[MENSAGEM ATUAL] {message}")
        
        return "\n".join(context_parts)

    def _extract_context_from_response(self, user_message: str, agent_response: str):
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["quero", "vou querer", "sim", "ok", "fazer pedido"]):
            if self.conversation_state["pizza_in_consideration"]:
                self.conversation_state["current_step"] = "confirming_order"
    
    def reset_conversation(self):
        self.conversation_state = {
            "current_order_id": None,
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "conversation_history": [],
            "pizza_in_consideration": None,
            "current_step": "greeting"
        }
    
