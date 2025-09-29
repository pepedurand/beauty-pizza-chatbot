# 🍕 Beauty Pizza Chatbot

Um chatbot inteligente para a pizzaria "Beauty Pizza" desenvolvido com **Agno** que se comunica com a API `candidates-case-order-api` para gerenciar pedidos de forma completa e inteligente.

## 📋 Descrição

O Beauty Pizza Chatbot é um assistente virtual chamado **Bella** que simula um atendente de pizzaria. Ele é capaz de:

- 🤖 Interagir naturalmente com clientes
- 📜 Apresentar o cardápio completo
- ❓ Responder perguntas sobre ingredientes, sabores e preços
- 🛒 Gerenciar pedidos completos (criar, adicionar itens, calcular totais)
- 📍 Coletar endereços de entrega
- 💾 Manter histórico da conversa

## 🏗️ Arquitetura

O projeto segue uma arquitetura modular baseada no framework **Agno**:

```
beauty-pizza-chatbot/
├── src/beauty_pizza_chatbot/
│   ├── agent/                 # Agente principal e ferramentas
│   │   ├── beauty_pizza_agent.py
│   │   └── tools.py
│   ├── integrations/          # Integrações com APIs e BD
│   │   ├── knowledge_base.py
│   │   └── order_api.py
│   ├── utils/                 # Utilitários
│   │   └── setup.py
│   └── main.py               # Ponto de entrada principal
├── run.py                    # Script de execução
├── pyproject.toml           # Configurações Poetry
└── .env.example             # Exemplo de variáveis de ambiente
```

## 🛠️ Tecnologias Utilizadas

- **[Agno](https://github.com/agno-framework/agno)** - Framework para agentes de IA
- **OpenAI GPT-4** - Modelo de linguagem
- **Python 3.12+** - Linguagem de programação
- **SQLite** - Base de conhecimento das pizzas
- **Django REST API** - API para gerenciamento de pedidos
- **Poetry** - Gerenciamento de dependências

## ⚙️ Pré-requisitos

1. **Python 3.12+** instalado
2. **Poetry** para gerenciar dependências
3. **Chave da API OpenAI**
4. **Order API** rodando (projeto `candidates-case-order-api`)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd beauty-pizza-chatbot
```

### 2. Instale as dependências

```bash
poetry install
```

### 3. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
ORDER_API_URL=http://localhost:8000
ORDER_API_TIMEOUT=30
SQLITE_DB_PATH=../candidates-case-order-api/knowledge_base/knowledge_base.sql
```

### 4. Execute a Order API (em outro terminal)

```bash
cd ../candidates-case-order-api
python manage.py runserver
```

## 🎮 Como Executar

### Execução Simples

```bash
python run.py
```

### Verificar Dependências

```bash
python run.py --check-deps
```

### Ver Ajuda

```bash
python run.py --help
```

### Usando Poetry

```bash
poetry run python run.py
```

## 💬 Como Usar

### Comandos Especiais

- `reset` - Reinicia a conversa atual
- `sair` - Encerra o chatbot

### Exemplo de Conversa

```
Você: Olá!

Bella: Olá! Bem-vindo à Beauty Pizza! 🍕 Sou a Bella e estou aqui para
ajudá-lo com seu pedido. Gostaria de ver nosso cardápio?

Você: Sim, por favor!

Bella: [Apresenta o cardápio completo com pizzas disponíveis]

Você: Quanto custa uma pizza margherita grande com borda catupiry?

Bella: [Consulta preço e fornece informações detalhadas]

Você: Quero fazer um pedido

Bella: Perfeito! Para começar, preciso de algumas informações...
```

## 🔧 Funcionalidades

### 🍕 Gestão de Cardápio

- Consulta de todas as pizzas disponíveis
- Informações sobre ingredientes e descrições
- Consulta de preços por tamanho e tipo de borda
- Busca de pizzas por sabor

### 📦 Gestão de Pedidos

- Criação de novos pedidos
- Adição de pizzas aos pedidos
- Cálculo automático de totais
- Atualização de quantidades
- Remoção de itens

### 📍 Gestão de Entrega

- Coleta de endereço completo
- Suporte a complemento e ponto de referência
- Atualização de endereços

### 🧠 Inteligência Conversacional

- Processamento de linguagem natural
- Manutenção do contexto da conversa
- Sugestões inteligentes
- Confirmações de segurança

## 🛠️ Desenvolvimento

### Estrutura do Código

#### Agente Principal (`beauty_pizza_agent.py`)

- Classe `BeautyPizzaAgent` que orquestra toda a interação
- Sistema de prompts otimizado para atendimento de pizzaria
- Gestão de estado da conversa
- Integração com ferramentas via Agno

#### Ferramentas (`tools.py`)

- `get_menu()` - Obtém cardápio completo
- `get_pizza_info(sabor)` - Informações de pizza específica
- `create_order()` - Cria novo pedido
- `add_pizza_to_order()` - Adiciona pizza ao pedido
- `get_order_total()` - Calcula total do pedido
- `update_delivery_address()` - Atualiza endereço

#### Integrações

- **KnowledgeBase** - Acesso ao SQLite com dados das pizzas
- **OrderAPI** - Cliente HTTP para comunicação com Django API

### Adicionando Novas Funcionalidades

1. **Nova Ferramenta**:

```python
@tool_register(
    name="nova_funcionalidade",
    description="Descrição da funcionalidade"
)
def nova_funcionalidade(parametro: str) -> Dict:
    # Implementação
    pass
```

2. **Registrar no Agente**:

```python
self.available_tools.append("nova_funcionalidade")
```

## 🧪 Testes

### Teste Manual

```bash
python src/beauty_pizza_chatbot/utils/setup.py
```

### Verificar Conexões

- Testa conectividade com Order API
- Valida configuração do banco de dados
- Verifica variáveis de ambiente

## 📊 Monitoramento

O chatbot inclui:

- Logs de tempo de resposta
- Tratamento de erros gracioso
- Feedback visual de operações
- Histórico de conversas

## ⚡ Performance

- Tempo médio de resposta: < 3 segundos
- Suporte a conversas longas
- Cache inteligente de consultas
- Otimização de prompts

## 🔒 Segurança

- Validação de entradas
- Sanitização de dados SQL
- Timeouts em requisições HTTP
- Tratamento seguro de erros

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Solução de Problemas

### Erro: "OPENAI_API_KEY não configurada"

- Configure sua chave da OpenAI no arquivo `.env`

### Erro: "Não foi possível conectar com Order API"

- Verifique se a Order API está rodando em `http://localhost:8000`
- Teste com: `curl http://localhost:8000/api/`

### Erro: "Banco de dados não encontrado"

- Verifique o caminho em `SQLITE_DB_PATH`
- Execute o script de setup: `python src/beauty_pizza_chatbot/utils/setup.py`

### Performance lenta

- Verifique sua conexão com internet (OpenAI API)
- Considere usar um modelo mais rápido (gpt-3.5-turbo)

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato com a equipe de desenvolvimento.

---

**Desenvolvido com ❤️ para a Beauty Pizza** 🍕
