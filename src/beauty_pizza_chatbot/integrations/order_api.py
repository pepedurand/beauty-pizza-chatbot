import os
import requests
from typing import Dict, List, Optional


class OrderAPI:
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url or os.getenv('ORDER_API_URL', 'http://localhost:8000')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
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
        data = {
            'client_name': client_name,
            'client_document': client_document,
            'delivery_date': delivery_date
        }
        return self._make_request('POST', '/api/orders/', data)
    
    def get_order(self, order_id: int) -> Dict:
        return self._make_request('GET', f'/api/orders/{order_id}/')
    
    def add_item_to_order(self, order_id: int, pizza_flavor: str, 
                         size: str, crust: str, quantity: int = 1, unit_price: float = 0.0) -> Dict:

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

        order = self._make_request('GET', f'/api/orders/{order_id}/')

        return {"total": order.get("total_price", "0.00")}
    
    def update_delivery_address(self, order_id: int, street_name: str, 
                               number: str, complement: str = None, 
                               reference_point: str = None) -> Dict:
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

        order = self._make_request('GET', f'/api/orders/{order_id}/')
        return order.get('items', [])
    
    def delete_order_item(self, order_id: int, item_id: int) -> Dict:
        return self._make_request('DELETE', f'/api/orders/{order_id}/items/{item_id}/')
    
    def filter_orders_by_document(self, client_document: str, delivery_date: str = None) -> List[Dict]:
        params = {'client_document': client_document}
        if delivery_date:
            params['delivery_date'] = delivery_date
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        endpoint = f'/api/orders/filter/?{query_string}'
        
        try:
            return self._make_request('GET', endpoint)
        except Exception as e:
            return {"erro": f"Não foi possível filtrar pedidos: {str(e)}"}
    
    def get_status_order(self, order_id: int) -> Dict:
        order = self._make_request('GET', f'/api/orders/{order_id}/')
        return {"status": order.get("status", "não encontrado")}