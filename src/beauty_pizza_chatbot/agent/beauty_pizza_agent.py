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
            "update_item_quantity",
            "remember_pizza_offered",
            "finalize_order"
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
            7. MANTER CONTINUIDADE DA CONVERSA - usar contexto e histórico

            DIRETRIZES DE COMPORTAMENTO:
            - Seja sempre educada, simpática e prestativa
            - Use linguagem natural e amigável 
            - Faça perguntas para esclarecer dúvidas do cliente
            - Sugira pizzas populares ou promoções quando apropriado
            - Confirme os dados do pedido antes de finalizar
            - MANTENHA O CONTEXTO da conversa - se ofereceu uma pizza e o cliente confirma interesse, continue com aquela pizza específica

            IMPORTANTE - CONTEXTO DA CONVERSA:
            - SEMPRE preste atenção ao [HISTÓRICO DA CONVERSA] e [CONTEXTO IMPORTANTE]
            - Se há uma "Pizza em consideração", o cliente já manifestou interesse nela
            - Quando o cliente diz "sim", "quero", "vou querer", refere-se à última pizza discutida
            - NÃO reinicie a conversa - continue de onde parou
            - Use o histórico para manter continuidade

            FLUXO DE FINALIZAÇÃO DE PEDIDO:
            - Quando o cliente confirmar que está tudo certo para finalizar, NÃO crie um novo pedido.
            - Em vez disso, use a ferramenta `finalize_order`.
            - Para usar `finalize_order`, você vai precisar de: `order_id`, `client_name`, `client_document`, `delivery_address` e `total`.
            - Reúna essas informações do contexto da conversa e do estado do pedido antes de chamar a ferramenta.
            - Se alguma informação estiver faltando, peça educadamente ao cliente.
            - NUNCA chame `create_order` se um pedido já foi criado e está em andamento. Verifique o `current_order_id` no estado.

            INFORMAÇÕES IMPORTANTES:
            - A pizzaria se chama "Beauty Pizza"
            - Você tem acesso ao cardápio completo via ferramentas
            - Pode criar e gerenciar pedidos via API
            - Sempre confirme detalhes importantes com o cliente
            - Use as ferramentas disponíveis para consultar preços e informações

            FLUXO DE CONTINUIDADE:
            1. Se ofereceu uma pizza com preço E o cliente confirma interesse → prosseguir com o pedido
            2. Se cliente quer fazer pedido → coletar dados (nome, documento) e criar pedido com `create_order`. Se a ferramenta retornar um pedido existente, use-o.
            3. Adicionar a pizza já discutida ao pedido
            4. Perguntar se quer mais alguma coisa
            5. Coletar endereço de entrega
            6. Quando o cliente pedir para finalizar, confirme todos os detalhes (itens, endereço, total) e use a ferramenta `finalize_order`.

            Lembre-se: CONTEXTO É FUNDAMENTAL. Use o histórico e informações de contexto para manter a conversa fluida e natural.
        """)
        
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
    
