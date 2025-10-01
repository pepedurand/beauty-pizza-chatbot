#!/usr/bin/env python3


import sys
from pathlib import Path

src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

if __name__ == '__main__':
    from main import main
    main()
    
