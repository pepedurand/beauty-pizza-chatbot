import sqlite3
import os
from typing import List, Dict, Optional
from pathlib import Path


class KnowledgeBase:
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.getenv('SQLITE_DB_PATH', 
                              '../candidates-case-order-api/knowledge_base/knowledge_base.sql')
        
        if not os.path.isabs(db_path):
            current_dir = Path(__file__).parent.parent.parent.parent
            db_path = current_dir / db_path
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        if self.db_path.endswith('.sql'):
            script_path = self.db_path
            self.db_path = self.db_path.replace('.sql', '.db')
            
            if not os.path.exists(self.db_path):
                with open(script_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                
                conn = sqlite3.connect(self.db_path)
                conn.executescript(sql_script)
                conn.close()
    
    def get_all_pizzas(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, sabor, descricao, ingredientes 
            FROM pizzas 
            ORDER BY sabor
        """)
        
        pizzas = []
        for row in cursor.fetchall():
            pizzas.append({
                'id': row[0],
                'sabor': row[1],
                'descricao': row[2],
                'ingredientes': row[3]
            })
        
        conn.close()
        return pizzas
    
    def get_pizza_by_flavor(self, sabor: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, sabor, descricao, ingredientes 
            FROM pizzas 
            WHERE LOWER(sabor) LIKE LOWER(?) 
            LIMIT 1
        """, (f'%{sabor}%',))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'sabor': row[1],
                'descricao': row[2],
                'ingredientes': row[3]
            }
        return None
    
    def get_sizes(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, tamanho FROM tamanhos ORDER BY id")
        
        sizes = []
        for row in cursor.fetchall():
            sizes.append({
                'id': row[0],
                'tamanho': row[1]
            })
        
        conn.close()
        return sizes
    
    def get_crusts(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, tipo FROM bordas ORDER BY id")
        
        crusts = []
        for row in cursor.fetchall():
            crusts.append({
                'id': row[0],
                'tipo': row[1]
            })
        
        conn.close()
        return crusts
    
    def get_price(self, pizza_id: int, tamanho_id: int, borda_id: int) -> Optional[float]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT preco 
            FROM precos 
            WHERE pizza_id = ? AND tamanho_id = ? AND borda_id = ?
        """, (pizza_id, tamanho_id, borda_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_pizza_with_price(self, sabor: str, tamanho: str, borda: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id, p.sabor, p.descricao, p.ingredientes,
                t.id, t.tamanho,
                b.id, b.tipo,
                pr.preco
            FROM pizzas p
            JOIN precos pr ON p.id = pr.pizza_id
            JOIN tamanhos t ON pr.tamanho_id = t.id
            JOIN bordas b ON pr.borda_id = b.id
            WHERE LOWER(p.sabor) LIKE LOWER(?)
                AND LOWER(t.tamanho) LIKE LOWER(?)
                AND LOWER(b.tipo) LIKE LOWER(?)
            LIMIT 1
        """, (f'%{sabor}%', f'%{tamanho}%', f'%{borda}%'))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'pizza_id': row[0],
                'sabor': row[1],
                'descricao': row[2],
                'ingredientes': row[3],
                'tamanho_id': row[4],
                'tamanho': row[5],
                'borda_id': row[6],
                'borda': row[7],
                'preco': row[8]
            }
        return None