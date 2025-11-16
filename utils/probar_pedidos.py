# utils/probar_pedidos.py
from services.database_service import PostgreSQLService
from services.pedido_service import PedidoService
from services.producto_service import ProductoService

def probar_servicios():
    print("🧪 Probando servicios de pedidos...")
    
    db = PostgreSQLService()
    pedido_service = PedidoService(db)
    producto_service = ProductoService(db)
    
    # Probar categorías
    categorias = producto_service.obtener_categorias()
    print(f"📂 Categorías: {categorias}")
    
    # Probar productos
    if categorias:
        productos = producto_service.obtener_productos_por_categoria(categorias[0])
        print(f"📦 Productos en {categorias[0]}: {len(productos)}")
        
        # Probar agregar producto temporal
        if productos:
            pedido_service.agregar_item_temporal(productos[0], 2)
            print(f"🛒 Pedido temporal: {len(pedido_service.pedido_temporal['items'])} items")
            print(f"💰 Total: ${pedido_service.pedido_temporal['total']}")
    
    print("✅ Prueba completada")

if __name__ == "__main__":
    probar_servicios()