from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from .tools import resolve_tools


class BeautyPizzaAgent:
    ESTADO_INICIAL = "inicial"
    ESTADO_CONSULTANDO_CARDAPIO = "consultando_cardapio"
    ESTADO_ADD_PIZZAS_TEMPORARIAS = "adicionando_pizzas"  
    ESTADO_COLETANDO_DADOS = "coletando_dados"
    ESTADO_CRIANDO_PEDIDO = "criando_pedido"  
    ESTADO_FINALIZADO = "finalizado"
    
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
            "get_order",
            "create_order",
            "add_pizza_to_order",
            "update_delivery_address",
            "get_order_items",
            "get_order_total",
            "remove_item_from_order",
        ]
        
        self.agent = Agent(
            model=self.model,
            tools=resolve_tools(self.available_tools),
            instructions="",  
            show_tool_calls=False,
            add_history_to_messages=True,  
            num_history_responses=10,  
        )
        
        self.conversation_state = {
            "estado": self.ESTADO_INICIAL,
            "order_id": None,
            "client_name": None,
            "client_document": None,
            "pizzas_temporarias": [],  
            "endereco_temporario": None,
            "nome_temporario": None,
            "documento_temporario": None,
            "saudacao_feita": False,
        }
    
    def chat(self, message: str) -> str:
        try:
            print(f"[Bella] Estado atual: {self.conversation_state['estado']}")
            
            self._check_for_existing_order(message)
            
            instructions = self._get_dynamic_instructions()
            self.agent.instructions = instructions
            
            enriched_message = self._enrich_with_order_context(message)
            
            response = self.agent.run(enriched_message)
            
            self._update_state(message, response.content)
            
            return response.content
            
        except Exception as e:
            print(f"[Erro] {e}")
            return f"Desculpe, ocorreu um erro. Pode repetir por favor? (Erro: {str(e)})"
    
    def _check_for_existing_order(self, message: str):
        """Detecta se cliente mencionou um pedido existente"""
        import re
        
        patterns = [
            r'pedido\s+(?:#)?(\d+)',
            r'código\s+(?:#)?(\d+)',
            r'número\s+(?:#)?(\d+)',
            r'#(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                order_id = int(match.group(1))
                print(f"[Bella] Cliente mencionou pedido existente: #{order_id}")
                self.conversation_state["order_id"] = order_id
                # Se mencionou pedido existente, vai para estado de criação/finalização
                self.conversation_state["estado"] = self.ESTADO_CRIANDO_PEDIDO
                break
    
    def _get_dynamic_instructions(self) -> str:
        """Gera instruções específicas para cada estado do fluxo"""
        estado = self.conversation_state["estado"]
        order_id = self.conversation_state["order_id"]
        
        base = "Você é Bella, atendente virtual da pizzaria Beauty Pizza. Seja simpática e natural.\n\n"
        
        if estado == self.ESTADO_INICIAL:
            return base + dedent("""
            ESTADO: Saudação Inicial
            
            AÇÕES:
            1. Cumprimente o cliente de forma amigável
            2. Pergunte se ele já sabe o que vai pedir ou se quer ver o cardápio
            3. Se ele quiser o cardápio ou não souber o que quer, ajude-o com a tool get_menu()
            4. Se ele já souber qual pizza quer, use o get_pizza_info(sabor)
            
            NÃO peça informações pessoais ainda.
            """)
        
        elif estado == self.ESTADO_CONSULTANDO_CARDAPIO:
            return base + dedent("""
            ESTADO: Consultando Cardápio
            
            AÇÕES:
            1. Use get_menu() para mostrar as opções
            2. Responda dúvidas sobre pizzas usando get_pizza_info(sabor)
            3. Informe preços com get_pizza_price(sabor, tamanho, borda)
            4. Quando o cliente decidir o que quer, avance para próximo estado
                                 
            ⚠️ NÃO use create_order() ainda! Espere a confirmação final.
            """)
        
        if estado == self.ESTADO_ADD_PIZZAS_TEMPORARIAS:
            pizzas_temp = self.conversation_state.get("pizzas_temporarias", [])
            resumo_pizzas = "\n".join([f"- {p['sabor']} ({p['tamanho']}, {p['borda']}) x{p['quantidade']}" for p in pizzas_temp]) if pizzas_temp else "Nenhuma pizza adicionada ainda"
            
            return base + dedent(f"""
            ESTADO: Adicionando Pizzas ao Pedido #{order_id}
            
            PEDIDO ATUAL: #{order_id}
            PIZZAS TEMPORÁRIAS:
            {resumo_pizzas}
            
            AÇÕES:
            1. Para cada pizza que o cliente escolher:
               - Use get_pizza_info(sabor) para validar
               - Use get_pizza_price(sabor, tamanho, borda) para confirmar o preço
               - Anote mentalmente a pizza (sabor, tamanho, borda, quantidade, preço)
               - Mostre o preço ao cliente
            2. Pergunte se deseja adicionar mais pizzas
            3. Quando o cliente já tiver escolhido e não quiser mais, avance para a coleta de dados do cliente
            
            ⚠️ NÃO use create_order() ou add_pizza_to_order() ainda!
            ⚠️ Apenas valide as pizzas e anote as escolhas no estado pizzas_temporarias.
            """)

        if estado == self.ESTADO_COLETANDO_DADOS:
            return base + dedent("""
            ESTADO: Coletando Nome, CPF e Pizzas do Cliente
            
            AÇÕES:
            1. IMPORTANTE: NÃO crie o pedido ainda!
            2. Pergunte o nome cliente
            3. Pergunte o Documento (CPF ou RG)
            4. Pergunte o endereço de entrega: Rua, Número, Complemento, Referência
            5. Mostre o resumo das pizzas escolhidas com os preços
            6. Quando cliente confirmar todas as pizzas
            7. Avance para criar o pedido

            ⚠️ NÃO use create_order() ou add_pizza_to_order() ainda!
            ⚠️ Apenas valide as pizzas e anote as escolhas.
            """)

        elif estado == self.ESTADO_CRIANDO_PEDIDO:
            return base + dedent(f"""
            ESTADO: Criando Pedido Completo
            
            AGORA SIM! Chegou a hora de criar o pedido com todas as informações.
            
            AÇÕES:
            1. Use create_order(nome, cpf) para criar o pedido
            2. IMPORTANTE: Guarde o order_id retornado
            3. Para cada pizza da lista, use add_pizza_to_order(order_id, sabor, tamanho, borda, quantidade)
            4. Use update_delivery_address(order_id, rua, numero, complemento, referencia)
            5. Use get_order(order_id) para buscar o pedido completo
            6. Confirme os detalhes com o cliente
            7. Caso necessário, ajuste o pedido (adicione/remova itens/altere endereço)
            8. Avance para finalizado
            """)
        
        elif estado == self.ESTADO_FINALIZADO:
            return base + dedent(f"""
            ESTADO: Pedido Finalizado
            
            PEDIDO: #{order_id}
            
            O pedido está completo e confirmado!
            Agradeça o cliente e informe que o pedido será entregue em breve.
            """)
        
        return base
    
    def _enrich_with_order_context(self, message: str) -> str:
        """Adiciona contexto do pedido à mensagem"""
        context_parts = []
        
        if self.conversation_state["order_id"]:
            context_parts.append(f"[PEDIDO ATIVO: #{self.conversation_state['order_id']}]")
        
        if self.conversation_state["client_name"]:
            context_parts.append(f"[CLIENTE: {self.conversation_state['client_name']}]")
        
        if context_parts:
            return f"{' | '.join(context_parts)}\n\n{message}"
        return message
    
    def _update_state(self, user_message: str, agent_response: str):
        """Atualiza o estado do fluxo baseado no contexto"""
        estado_atual = self.conversation_state["estado"]
        import re
        
        if estado_atual == self.ESTADO_INICIAL:
            if "cardápio" in user_message.lower() or "menu" in user_message.lower():
                self.conversation_state["estado"] = self.ESTADO_CONSULTANDO_CARDAPIO
                print("[Bella] Cliente pediu cardápio. Avançando para CONSULTANDO_CARDAPIO...")
            elif any(word in user_message.lower() for word in ["quero", "vou", "gostaria", "pizza", "calabresa", "margherita", "portuguesa"]):
                self.conversation_state["estado"] = self.ESTADO_ADD_PIZZAS_TEMPORARIAS
                print("[Bella] Cliente já sabe o que quer. Avançando para ADD_PIZZAS_TEMPORARIAS...")
        
        elif estado_atual == self.ESTADO_CONSULTANDO_CARDAPIO:
            if any(word in user_message.lower() for word in ["quero", "vou pedir", "escolhi", "decidir", "essa", "essa pizza"]):
                self.conversation_state["estado"] = self.ESTADO_ADD_PIZZAS_TEMPORARIAS
                print("[Bella] Cliente decidiu. Avançando para ADD_PIZZAS_TEMPORARIAS...")
        
        elif estado_atual == self.ESTADO_ADD_PIZZAS_TEMPORARIAS:
            if any(word in user_message.lower() for word in ["só isso", "só", "apenas isso", "sim", "é isso", "finalizar", "confirmar"]):
                self.conversation_state["estado"] = self.ESTADO_COLETANDO_DADOS
                print("[Bella] Pizzas finalizadas! Avançando para COLETANDO_DADOS...")
        
        elif estado_atual == self.ESTADO_COLETANDO_DADOS:
            has_numbers = bool(re.search(r'\d{6,}', user_message))
            
            has_address = any(word in user_message.lower() for word in ["rua", "avenida", "av", "número", "n°", "nº"])
            
            if self.conversation_state.get("nome_temporario") and (has_numbers or has_address):
                if any(word in user_message.lower() for word in ["sim", "correto", "confirma", "pode", "finaliza", "tudo certo", "isso mesmo"]):
                    self.conversation_state["estado"] = self.ESTADO_CRIANDO_PEDIDO
                    print("[Bella] Todos os dados coletados! Avançando para CRIANDO_PEDIDO...")
            elif len(user_message.split(',')) >= 2 or (len(user_message.split()) >= 2 and has_numbers):
                words = user_message.split(',')
                if len(words) >= 2:
                    self.conversation_state["nome_temporario"] = words[0].strip()
                    self.conversation_state["documento_temporario"] = re.sub(r'\D', '', words[1].strip())
                    print(f"[Bella] Nome e documento salvos temporariamente: {self.conversation_state['nome_temporario']}")
        
        elif estado_atual == self.ESTADO_CRIANDO_PEDIDO:
            if "pedido" in agent_response.lower() and "#" in agent_response:
                match = re.search(r'#(\d+)', agent_response)
                if match:
                    self.conversation_state["order_id"] = int(match.group(1))
                    self.conversation_state["estado"] = self.ESTADO_FINALIZADO
                    print(f"[Bella] Pedido #{self.conversation_state['order_id']} finalizado com sucesso!")
    
    def reset_conversation(self):
        """Reinicia a conversa"""
        self.conversation_state = {
            "estado": self.ESTADO_INICIAL,
            "order_id": None,
            "client_name": None,
            "client_document": None,
            "pizzas_temporarias": [],
            "endereco_temporario": None,
            "nome_temporario": None,
            "documento_temporario": None,
            "saudacao_feita": False,
        }
        print("[Bella] Conversa reiniciada!")