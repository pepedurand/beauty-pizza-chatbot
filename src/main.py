import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import os
import time
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  

from agent import BeautyPizzaAgent


def main():
    print("🍕 Bem-vindo ao sistema da Beauty Pizza! 🍕")
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("❌ Erro: OPENAI_API_KEY não configurada!")
        print("Por favor, configure sua chave da API do OpenAI no arquivo .env")
        return
    
    order_api_url = os.getenv('ORDER_API_URL', 'http://localhost:8000')
    print(f"🔗 Conectando com Order API: {order_api_url}")
    
    try:
        print("🤖 Inicializando agente Bella...")
        agent = BeautyPizzaAgent(openai_api_key)
        agent.reset_conversation()
        print("✅ Agente inicializado com sucesso!")
        print("\nBella está pronta para atender! Digite 'sair' para encerrar.\n")
        
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


if __name__ == '__main__':
    main()