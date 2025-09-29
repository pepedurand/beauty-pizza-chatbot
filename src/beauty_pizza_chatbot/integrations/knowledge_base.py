import sqlite3
import os
from typing import List, Dict, Optional
from pathlib import Path


class KnowledgeBase:
    """Classe para acessar a base de conhecimento das pizzas no SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa a conexão com a base de dados SQLite.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados.
                     Se None, usa o caminho do .env ou o padrão.
        """
        if db_path is None:
            db_path = os.getenv('SQLITE_DB_PATH', 
                              '../candidates-case-order-api/knowledge_base/knowledge_base.sql')
        
        # Ajustar o caminho relativo se necessário
        if not os.path.isabs(db_path):
            current_dir = Path(__file__).parent.parent.parent.parent
            db_path = current_dir / db_path
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados executando o script SQL se necessário."""
        db_dir = os.path.dirname(self.db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        # Se o arquivo tem extensão .sql, significa que é o script
        if self.db_path.endswith('.sql'):
            script_path = self.db_path
            self.db_path = self.db_path.replace('.sql', '.db')
            
            # Se o .db não existe, cria executando o script
            if not os.path.exists(self.db_path):
                with open(script_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                
                conn = sqlite3.connect(self.db_path)
                conn.executescript(sql_script)
                conn.close()
    
    def get_all_pizzas(self) -> List[Dict]:
        """Retorna todas as pizzas disponíveis."""
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
        """Retorna uma pizza específica pelo sabor."""
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
        """Retorna todos os tamanhos disponíveis."""
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
        """Retorna todos os tipos de borda disponíveis."""
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
        """Retorna o preço de uma pizza específica."""
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
        """Retorna informações completas da pizza incluindo preço."""
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