# services/pedido_service.py
from typing import List, Dict, Optional
from datetime import datetime
from services.database_service import PostgreSQLService
import psycopg2

class PedidoService:
    def __init__(self, db_service: PostgreSQLService):
        self.db = db_service
        self.pedido_temporal = {
            'mesa': '1',
            'items': [],
            'total': 0.0,
            'notas': ''
        }
   
   # crear pedido
    def crear_pedido(self, mesa: str, empleado_id: int, notas: str = "") -> Optional[int]:
        """Crear pedido - VERSIÓN SIMPLE Y ROBUSTA"""
        try:
            print(f"📝 Creando pedido para mesa {mesa}...")
            
            # Conexión directa para evitar problemas
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute(
                "INSERT INTO pedidos (mesa, empleado_id, notas) VALUES (%s, %s, %s) RETURNING id",
                (mesa, empleado_id, notas)
            )
            
            # Obtener el ID - siempre es una tupla con un elemento
            resultado = cur.fetchone()
            pedido_id = resultado[0] if resultado else None
            
            conn.commit()
            cur.close()
            conn.close()
            
            if pedido_id:
                print(f"✅ Pedido creado con ID: {pedido_id}")
                return pedido_id
            else:
                print("❌ No se pudo obtener ID del pedido")
                return None
                
        except Exception as e:
            print(f"❌ Error creando pedido: {e}")
            return None
    
    def agregar_item_pedido(self, pedido_id: int, producto_id: int, 
                          cantidad: int, precio_unitario: float, 
                          notas: str = "") -> bool:
        """Agregar item al pedido - VERSIÓN SIMPLE Y ROBUSTA"""
        try:
            print(f"📦 Agregando item al pedido {pedido_id}...")
            
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute(
                """
                INSERT INTO items_pedido 
                (pedido_id, producto_id, cantidad, precio_unitario, notas)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (pedido_id, producto_id, cantidad, precio_unitario, notas)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Item {producto_id} agregado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando item: {e}")
            return False
   # SE AFECTA CON CIERRE DE CUENTAS  
    def _actualizar_total_pedido(self, pedido_id: int):
        """Actualizar total en base de datos"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute(
                """
                UPDATE pedidos 
                SET total = (
                    SELECT COALESCE(SUM(subtotal), 0) 
                    FROM items_pedido 
                    WHERE pedido_id = %s
                ),
                updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (pedido_id, pedido_id)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"💰 Total actualizado para pedido {pedido_id}")
            
        except Exception as e:
            print(f"❌ Error actualizando total: {e}")
    
    # Métodos para el pedido temporal (antes de guardar)
    def agregar_item_temporal(self, producto: dict, cantidad: int = 1, notas: str = ""):
        """Agregar item al pedido temporal"""
        item = {
            'producto_id': producto['id'],
            'nombre': producto['nombre'],
            'precio': float(producto['precio']),
            'cantidad': cantidad,
            'notas': notas,
            'subtotal': float(producto['precio']) * cantidad
        }
        
        # Verificar si ya existe
        for existing_item in self.pedido_temporal['items']:
            if (existing_item['producto_id'] == producto['id'] and 
                existing_item.get('notas', '') == notas):
                existing_item['cantidad'] += cantidad
                existing_item['subtotal'] = existing_item['cantidad'] * existing_item['precio']
                break
        else:
            self.pedido_temporal['items'].append(item)
        
        self._calcular_total_temporal()
        print(f"➕ Item temporal agregado: {producto['nombre']} x{cantidad}")
        
    def _calcular_total_temporal(self):
        """Calcular total del pedido temporal"""
        self.pedido_temporal['total'] = sum(item['subtotal'] for item in self.pedido_temporal['items'])
        print(f"🧮 Total temporal: ${self.pedido_temporal['total']:.2f}")
    
    def limpiar_pedido_temporal(self):
        """Limpiar pedido temporal"""
        self.pedido_temporal = {
            'mesa': '1',
            'items': [],
            'total': 0.0,
            'notas': ''
        }
        print("🧹 Pedido temporal limpiado")
    
    def obtener_pedidos_activos(self) -> List[Dict]:
        """Obtener pedidos en estado pendiente o preparación"""
        try:
            return self.db.ejecutar_consulta("""
                SELECT p.*, e.nombre as mesero
                FROM pedidos p
                JOIN empleados e ON p.empleado_id = e.id
                WHERE p.estado IN ('pendiente', 'confirmado', 'preparacion')
                ORDER BY p.created_at DESC
            """)
        except Exception as e:
            print(f"Error obteniendo pedidos activos: {e}")
            return []
    
   
    def obtener_estados_pedido(self):
        """Obtener todos los estados posibles"""
        return ['pendiente', 'preparacion', 'listo', 'entregado', 'pagado', 'cancelado']

    #PEDIDOS ABIERTOS
    def obtener_pedido_por_id(self, pedido_id: int) -> Optional[Dict]:
        """Obtener datos generales de un pedido por ID"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT p.id, p.mesa, p.total, e.nombre as mesero
                FROM pedidos p
                JOIN empleados e ON p.empleado_id = e.id
                WHERE p.id = %s
            """, (pedido_id,))
            
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'mesa': row[1],
                    'total': float(row[2]),
                    'mesero': row[3]
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo pedido: {e}")
            return None
    
    def obtener_items_pedido(self, pedido_id: int) -> List[Dict]:
        """Obtener productos de un pedido por ID"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT pr.nombre, ip.cantidad, ip.precio_unitario,
                    (ip.cantidad * ip.precio_unitario) as subtotal
                FROM items_pedido ip
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE ip.pedido_id = %s
            """, (pedido_id,))
            
            items = []
            for row in cur.fetchall():
                items.append({
                    'nombre': row[0],
                    'cantidad': row[1],
                    'precio': float(row[2]),
                    'subtotal': float(row[3])
                })
            
            cur.close()
            conn.close()
            return items
            
        except Exception as e:
            print(f"❌ Error obteniendo items del pedido: {e}")
            return []
    
    def cambiar_estado_pedido(self, pedido_id: int, nuevo_estado: str, empleado_id: int = None) -> bool:
        """Cambiar estado de un pedido con auditoría"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Actualizar estado del pedido
            cur.execute("""
                UPDATE pedidos 
                SET estado = %s
                WHERE id = %s
                RETURNING id
            """, (nuevo_estado, pedido_id))
            
            if not cur.fetchone():
                return False
            
            # Registrar en historial si hay empleado
            if empleado_id:
                cur.execute("""
                    INSERT INTO historial_estados_pedidos 
                    (pedido_id, empleado_id, estado_anterior, estado_nuevo)
                    VALUES (%s, %s, 
                        (SELECT estado FROM pedidos WHERE id = %s),
                        %s
                    )
                """, (pedido_id, empleado_id, pedido_id, nuevo_estado))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Pedido #{pedido_id} cambió a estado: {nuevo_estado}")
            return True
            
        except Exception as e:
            print(f"❌ Error cambiando estado: {e}")
            return False

    def agregar_productos_pedido_abierto(self, pedido_id: int, productos: List[Dict]) -> bool:
        """Agregar más productos a un pedido abierto"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Verificar que el pedido está abierto (no pagado)
            cur.execute("SELECT estado FROM pedidos WHERE id = %s", (pedido_id,))
            resultado = cur.fetchone()
            
            if not resultado or resultado[0] == 'pagado':
                return False
            
            # Agregar nuevos productos
            for producto in productos:
                cur.execute("""
                    INSERT INTO items_pedido 
                    (pedido_id, producto_id, cantidad, precio_unitario, notas)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    pedido_id, 
                    producto['id'], 
                    producto['cantidad'],
                    producto['precio'],
                    producto.get('notas', '')
                ))
            
            # Recalcular total
            cur.execute("""
                UPDATE pedidos 
                SET total = (
                    SELECT SUM(cantidad * precio_unitario) 
                    FROM items_pedido 
                    WHERE pedido_id = %s
                )
                WHERE id = %s
            """, (pedido_id, pedido_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ {len(productos)} productos agregados al pedido #{pedido_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando productos: {e}")
            return False

    def obtener_pedidos_por_estado(self, estado: str) -> List[Dict]:
        """Obtener pedidos por estado específico"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    p.id,
                    p.mesa,
                    p.total,
                    p.created_at,
                    e.nombre as mesero,
                    JSON_AGG(
                        JSON_BUILD_OBJECT(
                            'nombre', pr.nombre,
                            'cantidad', ip.cantidad,
                            'precio_unitario', ip.precio_unitario,
                            'notas', ip.notas
                        )
                    ) as items
                FROM pedidos p
                JOIN empleados e ON p.empleado_id = e.id
                JOIN items_pedido ip ON p.id = ip.pedido_id
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE p.estado = %s
                GROUP BY p.id, p.mesa, p.total, p.created_at, e.nombre
                ORDER BY p.created_at ASC
            """, (estado,))
            
            pedidos = []
            for row in cur.fetchall():
                pedido = {
                    'id': row[0],
                    'mesa': row[1],
                    'total': float(row[2]),
                    'created_at': row[3],
                    'mesero': row[4],
                    'items': row[5] if row[5] else []
                }
                pedidos.append(pedido)
            
            cur.close()
            conn.close()
            return pedidos
            
        except Exception as e:
            print(f"❌ Error obteniendo pedidos por estado: {e}")
            return []

