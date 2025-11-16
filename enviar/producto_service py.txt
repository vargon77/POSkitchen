# services/producto_service.py
from services.database_service import PostgreSQLService
from typing import List, Dict

class ProductoService:
    def __init__(self, db_service: PostgreSQLService):
        self.db = db_service
    
    def obtener_categorias(self) -> List[str]:
        """Obtener lista de categorías únicas"""
        try:
            result = self.db.ejecutar_consulta(
                "SELECT DISTINCT categoria FROM productos WHERE activo = TRUE ORDER BY categoria"
            )
            return [row['categoria'] for row in result if row['categoria']]
        except Exception as e:
            print(f"Error obteniendo categorías: {e}")
            return []
    
    def obtener_productos_por_categoria(self, categoria: str) -> List[Dict]:
        """Obtener productos por categoría"""
        try:
            return self.db.ejecutar_consulta(
                """
                SELECT id, nombre, descripcion, precio, imagen_url, stock
                FROM productos 
                WHERE categoria = %s AND activo = TRUE
                ORDER BY nombre
                """,
                (categoria,)
            )
        except Exception as e:
            print(f"Error obteniendo productos: {e}")
            return []
    
    def obtener_todos_productos(self) -> List[Dict]:
        """Obtener todos los productos activos"""
        try:
            return self.db.ejecutar_consulta(
                "SELECT * FROM productos WHERE activo = TRUE ORDER BY categoria, nombre"
            )
        except Exception as e:
            print(f"Error obteniendo todos los productos: {e}")
            return []