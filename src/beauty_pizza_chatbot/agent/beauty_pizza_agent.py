from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
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
        self.model = OpenAIChat(
            id="gpt-4o-mini",
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
            show_tool_calls=True
        )
        
        # Estado da conversa
        self.conversation_state = {
            "current_order_id": None,
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "conversation_history": [],
            "pizza_in_consideration": None,  # Pizza que o cliente está considerando
            "current_step": "greeting"  # greeting, browsing, ordering, confirmation
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
            # Construir contexto completo incluindo histórico
            full_context = self._build_full_context(message)
            
            # Processar com o agente
            response = self.agent.run(full_context)
            
            # Atualizar histórico
            self.conversation_state["conversation_history"].append({
                "user": message,
                "agent": response.content
            })
            
            # Analisar resposta para extrair informações importantes
            self._extract_context_from_response(message, response.content)
            
            return response.content
            
        except Exception as e:
            error_msg = f"Desculpe, ocorreu um erro inesperado. Tente novamente. (Erro: {str(e)})"
            return error_msg
    
    def _build_full_context(self, message: str) -> str:
        """Constrói contexto completo incluindo histórico e estado atual."""
        context_parts = []
        
        # Adicionar histórico recente (últimas 6 mensagens)
        history = self.conversation_state["conversation_history"]
        if history:
            context_parts.append("\n[HISTÓRICO DA CONVERSA]")
            recent_history = history[-3:] if len(history) > 3 else history
            for h in recent_history:
                context_parts.append(f"Cliente: {h['user']}")
                context_parts.append(f"Bella: {h['agent']}")
        
        # Adicionar estado atual
        if self.conversation_state["pizza_in_consideration"]:
            pizza_info = self.conversation_state["pizza_in_consideration"]
            context_parts.append(f"\n[CONTEXTO IMPORTANTE] Pizza em consideração: {pizza_info['sabor']} {pizza_info['tamanho']} com borda {pizza_info['borda']} por R$ {pizza_info['preco']}")
        
        if self.conversation_state["current_order_id"]:
            context_parts.append(f"[CONTEXTO] Pedido atual ID: {self.conversation_state['current_order_id']}")
        
        if self.conversation_state["client_name"]:
            context_parts.append(f"[CONTEXTO] Cliente: {self.conversation_state['client_name']}")
        
        # Adicionar mensagem atual
        context_parts.append(f"\n[MENSAGEM ATUAL] {message}")
        
        return "\n".join(context_parts)

    def _extract_context_from_response(self, user_message: str, agent_response: str):
        """Extrai informações importantes da resposta para manter contexto."""
        user_lower = user_message.lower()
        response_lower = agent_response.lower()
        
        # Detectar se uma pizza foi oferecida com preço
        if "r$" in response_lower and ("pizza" in response_lower or "margherita" in response_lower):
            # Extrair informações da pizza oferecida
            import re
            price_match = re.search(r'r\$\s*(\d+[,.]?\d*)', response_lower)
            if price_match:
                price_str = price_match.group(1).replace(',', '.')
                try:
                    price = float(price_str)
                    # Se mencionou margherita, média, cheddar
                    if "margherita" in response_lower and "média" in response_lower and "cheddar" in response_lower:
                        self.conversation_state["pizza_in_consideration"] = {
                            "sabor": "Margherita",
                            "tamanho": "Média",
                            "borda": "Recheada com Cheddar",
                            "preco": price
                        }
                        self.conversation_state["current_step"] = "pizza_offered"
                except ValueError:
                    pass
        
        # Detectar confirmação de interesse
        if any(word in user_lower for word in ["quero", "vou querer", "sim", "ok", "fazer pedido"]):
            if self.conversation_state["pizza_in_consideration"]:
                self.conversation_state["current_step"] = "confirming_order"
    
    def reset_conversation(self):
        """Reinicia o estado da conversa."""
        self.conversation_state = {
            "current_order_id": None,
            "client_name": None,
            "client_document": None,
            "delivery_address": None,
            "conversation_history": [],
            "pizza_in_consideration": None,
            "current_step": "greeting"
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

    def set_pizza_in_consideration(self, sabor: str, tamanho: str, borda: str, preco: float):
        """Define uma pizza que o cliente está considerando."""
        self.conversation_state["pizza_in_consideration"] = {
            "sabor": sabor,
            "tamanho": tamanho,
            "borda": borda,
            "preco": preco
        }
        self.conversation_state["current_step"] = "pizza_offered"

    def get_pizza_in_consideration(self):
        """Retorna a pizza que o cliente está considerando."""
        return self.conversation_state.get("pizza_in_consideration")
    
    def clear_pizza_in_consideration(self):
        """Limpa a pizza em consideração."""
        self.conversation_state["pizza_in_consideration"] = None
    
    def get_conversation_context_summary(self) -> str:
        """Retorna um resumo do contexto atual da conversa."""
        context = []
        
        if self.conversation_state.get("pizza_in_consideration"):
            pizza = self.conversation_state["pizza_in_consideration"]
            context.append(f"Pizza em consideração: {pizza['sabor']} {pizza['tamanho']} com borda {pizza['borda']} - R$ {pizza['preco']}")
        
        if self.conversation_state.get("current_order_id"):
            context.append(f"Pedido ativo: #{self.conversation_state['current_order_id']}")
            
        if self.conversation_state.get("client_name"):
            context.append(f"Cliente: {self.conversation_state['client_name']}")
        
        return " | ".join(context) if context else "Nenhum contexto especial"