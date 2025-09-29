import os
import requests
from typing import Dict, List, Optional
import json
from datetime import datetime


class OrderAPI:
    """Classe para interagir com a Order API do Django."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Inicializa o cliente da Order API.
        
        Args:
            base_url: URL base da API. Se None, pega do .env
            timeout: Timeout para requisições em segundos
        """
        self.base_url = base_url or os.getenv('ORDER_API_URL', 'http://localhost:8000')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Faz uma requisição HTTP para a API.
        
        Args:
            method: Método HTTP (GET, POST, PUT, PATCH, DELETE)
            endpoint: Endpoint da API
            data: Dados para enviar no corpo da requisição
            
        Returns:
            Resposta da API como dicionário
            
        Raises:
            requests.RequestException: Em caso de erro na requisição
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.RequestException as e:
            raise requests.RequestException(f"Erro na requisição para {url}: {e}")
    
    def create_order(self, client_name: str, client_document: str, 
                    delivery_date: str) -> Dict:
        """
        Cria um novo pedido.
        
        Args:
            client_name: Nome do cliente
            client_document: Documento do cliente
            delivery_date: Data de entrega (formato YYYY-MM-DD)
            
        Returns:
            Dados do pedido criado
        """
        data = {
            'client_name': client_name,
            'client_document': client_document,
            'delivery_date': delivery_date
        }
        return self._make_request('POST', '/api/orders/', data)
    
    def get_order(self, order_id: int) -> Dict:
        """
        Recupera um pedido pelo ID.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Dados do pedido
        """
        return self._make_request('GET', f'/api/orders/{order_id}/')
    
    def add_item_to_order(self, order_id: int, pizza_flavor: str, 
                         size: str, crust: str, quantity: int = 1, unit_price: float = 0.0) -> Dict:
        """
        Adiciona um item ao pedido.
        
        Args:
            order_id: ID do pedido
            pizza_flavor: Sabor da pizza
            size: Tamanho da pizza
            crust: Tipo de borda
            quantity: Quantidade
            unit_price: Preço unitário do item
            
        Returns:
            Dados do item adicionado
        """
        # Criar nome descritivo do item
        item_name = f"Pizza {pizza_flavor} {size}"
        if crust and crust.lower() != "tradicional":
            item_name += f" - Borda {crust}"
        
        item_data = {
            'name': item_name,
            'quantity': quantity,
            'unit_price': unit_price
        }
        
        data = {
            'items': [item_data]
        }
        
        return self._make_request('PATCH', f'/api/orders/{order_id}/add-items/', data)
    
    def get_order_total(self, order_id: int) -> Dict:
        """
        Calcula o valor total do pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Informações do total do pedido
        """
        # Não há endpoint específico para total, precisaremos buscar o pedido completo
        order = self._make_request('GET', f'/api/orders/{order_id}/')
        return {"total": order.get("total_price", "0.00")}
    
    def update_delivery_address(self, order_id: int, street_name: str, 
                               number: str, complement: str = None, 
                               reference_point: str = None) -> Dict:
        """
        Atualiza o endereço de entrega do pedido.
        
        Args:
            order_id: ID do pedido
            street_name: Nome da rua
            number: Número
            complement: Complemento (opcional)
            reference_point: Ponto de referência (opcional)
            
        Returns:
            Dados do endereço atualizado
        """
        address_data = {
            'street_name': street_name,
            'number': number
        }
        
        if complement:
            address_data['complement'] = complement
        if reference_point:
            address_data['reference_point'] = reference_point
        
        data = {'delivery_address': address_data}
        return self._make_request('PATCH', f'/api/orders/{order_id}/update-address/', data)
    
    def get_order_items(self, order_id: int) -> List[Dict]:
        """
        Recupera todos os itens de um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Lista de itens do pedido
        """
        # Não há endpoint específico para listar itens, precisaremos buscar o pedido completo
        order = self._make_request('GET', f'/api/orders/{order_id}/')
        return order.get('items', [])
    
    def delete_order_item(self, order_id: int, item_id: int) -> Dict:
        """
        Remove um item do pedido.
        
        Args:
            order_id: ID do pedido
            item_id: ID do item
            
        Returns:
            Confirmação da remoção
        """
        return self._make_request('DELETE', f'/api/orders/{order_id}/items/{item_id}/')
    
    def update_order_item(self, order_id: int, item_id: int, 
                         quantity: int) -> Dict:
        """
        Atualiza a quantidade de um item no pedido.
        
        Args:
            order_id: ID do pedido
            item_id: ID do item
            quantity: Nova quantidade
            
        Returns:
            Dados do item atualizado
        """
        data = {'quantity': quantity}
        # Não há endpoint específico para atualizar item individual
        # Seria necessário implementar via atualização do pedido completo
        return {"erro": "Endpoint de atualização de item individual não disponível na API"}
    
    def filter_orders_by_document(self, client_document: str, delivery_date: str = None) -> List[Dict]:
        """
        Filtra pedidos pelo documento do cliente.
        
        Args:
            client_document: Documento do cliente
            delivery_date: Data de entrega (opcional, formato YYYY-MM-DD)
            
        Returns:
            Lista de pedidos do cliente
        """
        params = {'client_document': client_document}
        if delivery_date:
            params['delivery_date'] = delivery_date
        
        # Construir URL com parâmetros de query
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        endpoint = f'/api/orders/filter/?{query_string}'
        
        try:
            return self._make_request('GET', endpoint)
        except Exception as e:
            return {"erro": f"Não foi possível filtrar pedidos: {str(e)}"}
    
    def get_status_order(self, order_id: int) -> Dict:
        """
        Recupera o status de um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Dados do pedido
        """
        order = self._make_request('GET', f'/api/orders/{order_id}/')
        return {"status": order.get("status", "não encontrado")}