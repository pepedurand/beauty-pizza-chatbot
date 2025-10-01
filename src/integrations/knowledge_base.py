import sqlite3
import os
from typing import List, Dict, Optional
from difflib import SequenceMatcher


class KnowledgeBase:
    
    def __init__(self, db_path: Optional[str] = None):
        db_path = db_path or os.getenv('SQLITE_DB_PATH')
        if not db_path or not os.path.isabs(db_path):
            raise ValueError("Caminho do banco de dados não definido corretamente na variável de ambiente SQLITE_DB_PATH.")
        self.db_path = db_path
        self._init_database()
    
    def _find_best_match(self, search_term: str, candidates: List[Dict], 
                         key_field: str, threshold: float = 0.7, 
                         context: str = "") -> Optional[Dict]:
       
        best_match = None
        best_ratio = 0.0
        
        for candidate in candidates:
            candidate_value = str(candidate[key_field]).lower()
            search_lower = search_term.lower()
            
            ratio = SequenceMatcher(None, search_lower, candidate_value).ratio()
            
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = candidate
        
        if best_match and best_ratio < 1.0:  
            match_value = best_match[key_field]
            print(f"[KnowledgeBase] Match aproximado ({context}): '{search_term}' → '{match_value}' ({best_ratio:.0%})")
        
        return best_match
    
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
            WHERE LOWER(sabor) = LOWER(?)
            LIMIT 1
        """, (sabor,))
        
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                SELECT id, sabor, descricao, ingredientes 
                FROM pizzas
            """)
            
            all_pizzas = [
                {
                    'id': r[0],
                    'sabor': r[1],
                    'descricao': r[2],
                    'ingredientes': r[3]
                }
                for r in cursor.fetchall()
            ]
            
            best_match = self._find_best_match(
                search_term=sabor,
                candidates=all_pizzas,
                key_field='sabor',
                threshold=0.7,
                context='sabor'
            )
            
            conn.close()
            return best_match
        
        conn.close()
        
        return {
            'id': row[0],
            'sabor': row[1],
            'descricao': row[2],
            'ingredientes': row[3]
        }
    
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
        pizza = self.get_pizza_by_flavor(sabor)
        if not pizza:
            return None
        
        sizes = self.get_sizes()
        crusts = self.get_crusts()
        
        best_size = self._find_best_match(
            search_term=tamanho,
            candidates=sizes,
            key_field='tamanho',
            threshold=0.7,
            context='tamanho'
        )
        
        best_crust = self._find_best_match(
            search_term=borda,
            candidates=crusts,
            key_field='tipo',
            threshold=0.6,
            context='borda'
        )
        
        if not best_size or not best_crust:
            return None
        
        preco = self.get_price(pizza['id'], best_size['id'], best_crust['id'])
        
        if preco:
            return {
                'pizza_id': pizza['id'],
                'sabor': pizza['sabor'],
                'descricao': pizza['descricao'],
                'ingredientes': pizza['ingredientes'],
                'tamanho_id': best_size['id'],
                'tamanho': best_size['tamanho'],
                'borda_id': best_crust['id'],
                'borda': best_crust['tipo'],
                'preco': preco
            }
        return None