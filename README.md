# 🍕 Beauty Pizza Chatbot

Um chatbot inteligente para a pizzaria "Beauty Pizza", construído com Python e IA para fornecer uma experiência de atendimento automatizada e eficiente.

## 🤖 Como Funciona

O chatbot, chamado **Bella**, utiliza um agente de IA para compreender e responder às solicitações dos clientes. Ele é capaz de acessar uma base de conhecimento para consultar o cardápio e se integra a uma API externa para gerenciar os pedidos em tempo real.

O fluxo principal é:

1. O cliente envia uma mensagem.
2. O **Agente de IA** (usando a biblioteca `Agno` e um modelo da OpenAI) processa a mensagem.
3. Se necessário, o agente utiliza **ferramentas** para buscar informações (ex: preços no cardápio) ou realizar ações (ex: criar um pedido na API).
4. O agente gera uma resposta amigável e a envia para o cliente.

## ✨ Principais Funcionalidades

- **Consulta de Cardápio**: Informações sobre sabores, ingredientes, tamanhos e preços.
- **Gestão de Pedidos**: Criação de pedidos, adição/remoção de itens e cálculo de totais.
- **Coleta de Informações**: Obtenção de dados do cliente e endereço de entrega.
- **Conversa Contínua**: O chatbot mantém o contexto da conversa para uma interação mais fluida.

## 🛠️ Tecnologias

- **Python**
- **Agno**: Framework para desenvolvimento de agentes de IA.
- **OpenAI API**: Para o processamento de linguagem natural.
- **SQLite**: Como base de conhecimento para o cardápio.
- **Requests**: Para comunicação com a API de pedidos.
- **Poetry**: Para gerenciamento de dependências.

## 🚀 Como Executar

### Pré-requisitos

1. **Python 3.12+**
2. **Poetry** instalado.
3. Uma **chave da API da OpenAI**.
4. O serviço da **API de Pedidos** (`candidates-case-order-api`) deve estar em execução.

### Passos

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/pepedurand/beauty-pizza-chatbot
   cd beauty-pizza-chatbot
   ```

2. **Instale as dependências:**

   ```bash
   poetry install
   ```

3. **Configure as variáveis de ambiente:**

   - Copie o arquivo de exemplo: `cp .env.example .env`
   - Edite o arquivo `.env` com suas informações, principalmente a `OPENAI_API_KEY`.

4. **Inicie o chatbot:**
   ```bash
   python run.py
   ```

Após a inicialização, Bella estará pronta para atender no seu terminal!

## 📁 Estrutura do Projeto

```
.
├── src/beauty_pizza_chatbot/
│   ├── agent/          # Contém a lógica do agente de IA e suas ferramentas.
│   ├── integrations/   # Módulos para se comunicar com a API e a base de dados.
│   └── main.py         # Ponto de entrada da aplicação que inicia o chat.
├── run.py              # Script principal para executar o projeto.
├── pyproject.toml      # Define as dependências e configurações do projeto.
└── .env.example        # Arquivo de exemplo para as variáveis de ambiente.
```
