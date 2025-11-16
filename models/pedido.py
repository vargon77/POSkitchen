# models/pedido.py
from datetime import datetime
from typing import List, Dict, Optional

class ItemPedido:
    def __init__(self, producto_id: int, cantidad: int, precio: float, notas: str = ""):
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio_unitario = precio
        self.notas = notas
        self.subtotal = cantidad * precio

class Pedido:
    def __init__(self):
        self.id: Optional[int] = None
        self.mesa: str = ""
        self.estado: str = "pendiente"  # pendiente, preparacion, listo, entregado, cancelado
        self.items: List[ItemPedido] = []
        self.total: float = 0.0
        self.created_at: datetime = datetime.now()
        self.tipo: str = "local"  # local, llevar, delivery
        
    def calcular_total(self):
        self.total = sum(item.subtotal for item in self.items)