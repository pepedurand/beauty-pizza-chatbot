"""Utilitários para o Beauty Pizza Chatbot."""

import os
import sqlite3
from pathlib import Path


def setup_database():
    sql_script_path = Path(__file__).parent.parent.parent / 'candidates-case-order-api' / 'knowledge_base' / 'knowledge_base.sql'
    
    if not sql_script_path.exists():
        print(f"❌ Script SQL não encontrado em: {sql_script_path}")
        return False
    
    db_path = sql_script_path.with_suffix('.db')
    
    try:
        with open(sql_script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        conn = sqlite3.connect(str(db_path))
        conn.executescript(sql_script)
        conn.close()
        
        print(f"✅ Banco de dados criado em: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        return False


def test_api_connection():
    try:
        import requests
        
        api_url = os.getenv('ORDER_API_URL', 'http://localhost:8000')
        
        response = requests.get(f"{api_url}/api/", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Conexão com Order API OK: {api_url}")
            return True
        else:
            print(f"⚠️  Order API respondeu com status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Não foi possível conectar com Order API em: {api_url}")
        print("Certifique-se de que a API está rodando.")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar conexão com API: {e}")
        return False


def validate_environment():
    required_vars = ['OPENAI_API_KEY']
    optional_vars = {
        'ORDER_API_URL': 'http://localhost:8000',
        'ORDER_API_TIMEOUT': '30',
        'SQLITE_DB_PATH': '../candidates-case-order-api/knowledge_base/knowledge_base.sql'
    }
    
    print("🔍 Validando configuração do ambiente...")
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"❌ Variável obrigatória não configurada: {var}")
            all_good = False
        else:
            print(f"✅ {var} configurada")
    
    for var, default in optional_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"⚠️  {var} não configurada, usando padrão: {default}")
        else:
            print(f"✅ {var} configurada: {value}")
    
    return all_good


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🔧 Configuração do Beauty Pizza Chatbot")
    print("=" * 40)
    
    if validate_environment():
        print("\n📊 Testando conexões...")
        setup_database()
        test_api_connection()
    else:
        print("\n❌ Configure as variáveis de ambiente necessárias no arquivo .env")