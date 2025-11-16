# services/cocina_service.py
import psycopg2
from typing import List, Dict

class CocinaService:
    def __init__(self, db_service):
        self.db = db_service
    
    def obtener_pedidos_activos(self) -> List[Dict]:
        """Obtener pedidos para cocina (pendientes y en preparación)"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Consulta simplificada para evitar problemas con JSON_AGG
            cur.execute("""
                SELECT 
                    p.id,
                    p.mesa,
                    p.estado,
                    p.created_at,
                    e.nombre as mesero
                FROM pedidos p
                JOIN empleados e ON p.empleado_id = e.id
                WHERE p.estado IN ('pendiente', 'confirmado', 'preparacion')
                ORDER BY p.created_at ASC
            """)
            
            pedidos = []
            for row in cur.fetchall():
                pedido = {
                    'id': row[0],
                    'mesa': row[1],
                    'estado': row[2],
                    'created_at': row[3],
                    'mesero': row[4],
                    'items': self._obtener_items_pedido(row[0])  # Obtener items separadamente
                }
                pedidos.append(pedido)
            
            cur.close()
            conn.close()
            
            print(f"📊 Obtenidos {len(pedidos)} pedidos activos para cocina")
            return pedidos
            
        except Exception as e:
            print(f"❌ Error obteniendo pedidos activos: {e}")
            return []
    
    def _obtener_items_pedido(self, pedido_id: int) -> List[Dict]:
        """Obtener items de un pedido específico"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    ip.producto_id,
                    pr.nombre,
                    ip.cantidad,
                    ip.notas
                FROM items_pedido ip
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE ip.pedido_id = %s
            """, (pedido_id,))
            
            items = []
            for row in cur.fetchall():
                item = {
                    'producto_id': row[0],
                    'nombre': row[1],
                    'cantidad': row[2],
                    'notas': row[3] or ''
                }
                items.append(item)
            
            cur.close()
            conn.close()
            
            return items
            
        except Exception as e:
            print(f"❌ Error obteniendo items del pedido {pedido_id}: {e}")
            return []
    
    def cambiar_estado_pedido(self, pedido_id: int, nuevo_estado: str) -> bool:
        """Cambiar estado de un pedido"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute(
                "UPDATE pedidos SET estado = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (nuevo_estado, pedido_id)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"🔄 Pedido {pedido_id} cambiado a estado: {nuevo_estado}")
            return True
            
        except Exception as e:
            print(f"❌ Error cambiando estado del pedido: {e}")
            return False
    
    def obtener_estadisticas_cocina(self) -> Dict:
        """Obtener estadísticas para la cocina"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Pedidos por estado
            cur.execute("""
                SELECT estado, COUNT(*) 
                FROM pedidos 
                WHERE estado IN ('pendiente', 'confirmado', 'preparacion', 'listo')
                GROUP BY estado
            """)
            
            stats = {'por_estado': {}}
            for row in cur.fetchall():
                stats['por_estado'][row[0]] = row[1]
            
            # Total pedidos activos
            stats['total_activos'] = sum(stats['por_estado'].values())
            
            cur.close()
            conn.close()
            
            return stats
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {'por_estado': {}, 'total_activos': 0}
        
    # Tiempos de espera 
def obtener_tiempo_espera(self, created_at):
    """Calcular tiempo de espera desde que se creó el pedido"""
    from datetime import datetime
    ahora = datetime.now()
    diferencia = ahora - created_at
    minutos = int(diferencia.total_seconds() / 60)
    
    if minutos < 1:
        return "Recién llegado"
    elif minutos < 5:
        return f"{minutos} min"
    else:
        return f"{minutos} min ⚠️"