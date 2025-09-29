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
                         size: str, crust: str, quantity: int = 1) -> Dict:
        """
        Adiciona um item ao pedido.
        
        Args:
            order_id: ID do pedido
            pizza_flavor: Sabor da pizza
            size: Tamanho da pizza
            crust: Tipo de borda
            quantity: Quantidade
            
        Returns:
            Dados do item adicionado
        """
        data = {
            'pizza_flavor': pizza_flavor,
            'size': size,
            'crust': crust,
            'quantity': quantity
        }
        return self._make_request('POST', f'/api/orders/{order_id}/items/', data)
    
    def get_order_total(self, order_id: int) -> Dict:
        """
        Calcula o valor total do pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Informações do total do pedido
        """
        return self._make_request('GET', f'/api/orders/{order_id}/total/')
    
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
        return self._make_request('PATCH', f'/api/orders/{order_id}/address/', data)
    
    def get_order_items(self, order_id: int) -> List[Dict]:
        """
        Recupera todos os itens de um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Lista de itens do pedido
        """
        response = self._make_request('GET', f'/api/orders/{order_id}/items/')
        return response.get('items', [])
    
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
        return self._make_request('PUT', f'/api/orders/{order_id}/items/{item_id}/', data)