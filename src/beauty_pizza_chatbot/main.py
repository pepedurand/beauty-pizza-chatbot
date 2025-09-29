import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Carrega .env padrão se existir

from beauty_pizza_chatbot import BeautyPizzaAgent


def main():
    """Função principal que executa o chatbot da Beauty Pizza."""
    
    print("🍕 Bem-vindo ao sistema da Beauty Pizza! 🍕")
    print("=" * 50)
    
    # Verificar se a API key do OpenAI está configurada
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Erro: OPENAI_API_KEY não configurada!")
        print("Por favor, configure sua chave da API do OpenAI no arquivo .env")
        return
    
    # Verificar configurações da Order API
    order_api_url = os.getenv('ORDER_API_URL', 'http://localhost:8000')
    print(f"🔗 Conectando com Order API: {order_api_url}")
    
    try:
        # Inicializar o agente
        print("🤖 Inicializando agente Bella...")
        agent = BeautyPizzaAgent(openai_api_key)
        print("✅ Agente inicializado com sucesso!")
        print("\nBella está pronta para atender! Digite 'sair' para encerrar.\n")
        
        # Loop principal de interação
        while True:
            try:
                user_input = input("Você: ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit', 'bye']:
                    print("\nBella: Obrigada por visitar a Beauty Pizza! Até logo! 👋")
                    break
                
                if user_input.lower() == 'reset':
                    agent.reset_conversation()
                    print("\nBella: Conversa reiniciada! Como posso ajudá-lo?\n")
                    continue
                
                if not user_input:
                    continue
                
                # Processar mensagem com o agente
                print("\nBella: ", end="", flush=True)
                start_time = time.time()
                
                response = agent.chat(user_input)
                
                end_time = time.time()
                print(response)
                print(f"\n⏱️  Resposta em {end_time - start_time:.2f}s")
                print()
                
            except KeyboardInterrupt:
                print("\n\nBella: Até logo! Obrigada por visitar a Beauty Pizza! 🍕")
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {str(e)}")
                print("Tente novamente ou digite 'sair' para encerrar.\n")
    
    except Exception as e:
        print(f"❌ Erro ao inicializar o sistema: {str(e)}")
        print("Verifique suas configurações e tente novamente.")


def check_dependencies():
    """Verifica se as dependências necessárias estão instaladas."""
    try:
        import agno
        import openai
        import requests
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: poetry install")
        return False


def show_help():
    """Mostra informações de ajuda."""
    help_text = """
🍕 Beauty Pizza Chatbot - Ajuda

COMANDOS ESPECIAIS:
  reset    - Reinicia a conversa atual
  sair     - Encerra o chatbot
  
VARIÁVEIS DE AMBIENTE NECESSÁRIAS (.env):
  OPENAI_API_KEY     - Sua chave da API do OpenAI
  ORDER_API_URL      - URL da Order API (padrão: http://localhost:8000)
  SQLITE_DB_PATH     - Caminho para o banco de dados SQLite
  
EXEMPLOS DE USO:
  "Olá, gostaria de ver o cardápio"
  "Quanto custa uma pizza margherita grande com borda catupiry?"
  "Quero fazer um pedido"
  
FUNCIONALIDADES:
  - Consulta de cardápio completo
  - Informações sobre ingredientes e preços
  - Criação e gerenciamento de pedidos
  - Coleta de endereço de entrega
  - Cálculo de totais
  
Para mais informações, consulte o README.md
"""
    print(help_text)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
        elif sys.argv[1] == '--check-deps':
            check_dependencies()
        else:
            print("Uso: python -m beauty_pizza_chatbot.main [--help|--check-deps]")
    else:
        if check_dependencies():
            main()