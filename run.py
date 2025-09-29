#!/usr/bin/env python3
"""
Script de entrada principal para o Beauty Pizza Chatbot.
Execute com: python run.py
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

if __name__ == '__main__':
    from beauty_pizza_chatbot.main import main, show_help, check_dependencies
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
        elif sys.argv[1] == '--check-deps':
            check_dependencies()
        else:
            print("Uso: python run.py [--help|--check-deps]")
    else:
        main()