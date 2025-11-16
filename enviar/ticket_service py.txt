# services/ticket_service.py - SERVICIO PARA MANEJO DE TICKETS PARCIALES
import psycopg2
from typing import List, Dict, Optional

class TicketService:
    def __init__(self, db_service):
        self.db = db_service
    
    def crear_ticket_parcial(self, pedido_id: int, items: List[Dict], 
                           metodo_pago: str, empleado_id: int) -> Optional[int]:
        """Crear un ticket parcial para división de cuenta"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Obtener número de ticket (cuántos ya existen para este pedido)
            cur.execute("""
                SELECT COALESCE(MAX(numero_ticket), 0) + 1
                FROM tickets
                WHERE pedido_id = %s
            """, (pedido_id,))
            numero_ticket = cur.fetchone()[0]
            
            # Calcular total del ticket
            total = sum(item['cantidad'] * item['precio_unitario'] for item in items)
            
            # Crear ticket
            cur.execute("""
                INSERT INTO tickets (pedido_id, numero_ticket, total, metodo_pago, empleado_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (pedido_id, numero_ticket, total, metodo_pago, empleado_id))
            
            ticket_id = cur.fetchone()[0]
            
            # Insertar items del ticket
            for item in items:
                cur.execute("""
                    INSERT INTO items_ticket 
                    (ticket_id, item_pedido_id, cantidad_asignada, subtotal)
                    VALUES (%s, %s, %s, %s)
                """, (
                    ticket_id,
                    item['item_pedido_id'],
                    item['cantidad'],
                    item['cantidad'] * item['precio_unitario']
                ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Ticket #{numero_ticket} creado para pedido #{pedido_id}")
            return ticket_id
            
        except Exception as e:
            print(f"❌ Error creando ticket parcial: {e}")
            return None
    
    def obtener_tickets_pedido(self, pedido_id: int) -> List[Dict]:
        """Obtener todos los tickets de un pedido"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    t.id,
                    t.numero_ticket,
                    t.total,
                    t.metodo_pago,
                    t.estado,
                    t.created_at,
                    e.nombre as empleado
                FROM tickets t
                JOIN empleados e ON t.empleado_id = e.id
                WHERE t.pedido_id = %s
                ORDER BY t.numero_ticket
            """, (pedido_id,))
            
            tickets = []
            for row in cur.fetchall():
                tickets.append({
                    'id': row[0],
                    'numero': row[1],
                    'total': float(row[2]),
                    'metodo_pago': row[3],
                    'estado': row[4],
                    'fecha': row[5],
                    'empleado': row[6]
                })
            
            cur.close()
            conn.close()
            return tickets
            
        except Exception as e:
            print(f"❌ Error obteniendo tickets: {e}")
            return []
    
    def obtener_items_ticket(self, ticket_id: int) -> List[Dict]:
        """Obtener items de un ticket específico"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    pr.nombre,
                    it.cantidad_asignada,
                    ip.precio_unitario,
                    it.subtotal
                FROM items_ticket it
                JOIN items_pedido ip ON it.item_pedido_id = ip.id
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE it.ticket_id = %s
            """, (ticket_id,))
            
            items = []
            for row in cur.fetchall():
                items.append({
                    'nombre': row[0],
                    'cantidad': row[1],
                    'precio_unitario': float(row[2]),
                    'subtotal': float(row[3])
                })
            
            cur.close()
            conn.close()
            return items
            
        except Exception as e:
            print(f"❌ Error obteniendo items de ticket: {e}")
            return []
    
    def marcar_ticket_pagado(self, ticket_id: int) -> bool:
        """Marcar un ticket como pagado"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE tickets
                SET estado = 'pagado'
                WHERE id = %s
            """, (ticket_id,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Ticket #{ticket_id} marcado como pagado")
            return True
            
        except Exception as e:
            print(f"❌ Error marcando ticket: {e}")
            return False
    
    def verificar_pedido_completamente_pagado(self, pedido_id: int) -> bool:
        """Verificar si todos los items del pedido han sido pagados"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Contar items del pedido
            cur.execute("""
                SELECT SUM(cantidad) as total_items
                FROM items_pedido
                WHERE pedido_id = %s
            """, (pedido_id,))
            total_items_pedido = cur.fetchone()[0] or 0
            
            # Contar items asignados a tickets
            cur.execute("""
                SELECT SUM(it.cantidad_asignada) as items_asignados
                FROM items_ticket it
                JOIN tickets t ON it.ticket_id = t.id
                WHERE t.pedido_id = %s AND t.estado = 'pagado'
            """, (pedido_id,))
            items_pagados = cur.fetchone()[0] or 0
            
            cur.close()
            conn.close()
            
            return items_pagados >= total_items_pedido
            
        except Exception as e:
            print(f"❌ Error verificando pedido: {e}")
            return False
    
    def obtener_saldo_pendiente_pedido(self, pedido_id: int) -> Dict:
        """Obtener información del saldo pendiente de un pedido"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Total del pedido
            cur.execute("SELECT total FROM pedidos WHERE id = %s", (pedido_id,))
            total_pedido = float(cur.fetchone()[0])
            
            # Total pagado en tickets
            cur.execute("""
                SELECT COALESCE(SUM(total), 0)
                FROM tickets
                WHERE pedido_id = %s AND estado = 'pagado'
            """, (pedido_id,))
            total_pagado = float(cur.fetchone()[0])
            
            cur.close()
            conn.close()
            
            return {
                'total_pedido': total_pedido,
                'total_pagado': total_pagado,
                'saldo_pendiente': total_pedido - total_pagado,
                'porcentaje_pagado': (total_pagado / total_pedido * 100) if total_pedido > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error calculando saldo: {e}")
            return {
                'total_pedido': 0,
                'total_pagado': 0,
                'saldo_pendiente': 0,
                'porcentaje_pagado': 0
            }
    
    def generar_formato_ticket_impresion(self, ticket_id: int) -> str:
        """Generar formato de ticket para impresión"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Info del ticket
            cur.execute("""
                SELECT 
                    t.numero_ticket,
                    t.total,
                    t.metodo_pago,
                    t.created_at,
                    p.mesa,
                    e.nombre
                FROM tickets t
                JOIN pedidos p ON t.pedido_id = p.id
                JOIN empleados e ON t.empleado_id = e.id
                WHERE t.id = %s
            """, (ticket_id,))
            
            ticket_info = cur.fetchone()
            if not ticket_info:
                return ""
            
            # Items del ticket
            items = self.obtener_items_ticket(ticket_id)
            
            cur.close()
            conn.close()
            
            # Formatear ticket
            ticket = "=" * 40 + "\n"
            ticket += "       TICKET DE CUENTA PARCIAL\n"
            ticket += "=" * 40 + "\n"
            ticket += f"Mesa: {ticket_info[4]}\n"
            ticket += f"Ticket No: {ticket_info[0]}\n"
            ticket += f"Atendido por: {ticket_info[5]}\n"
            ticket += f"Fecha: {ticket_info[3].strftime('%d/%m/%Y %H:%M')}\n"
            ticket += "-" * 40 + "\n"
            
            for item in items:
                ticket += f"{item['nombre'][:25]:<25}\n"
                ticket += f"  {item['cantidad']} x ${item['precio_unitario']:.2f}"
                ticket += f" = ${item['subtotal']:.2f}\n"
            
            ticket += "-" * 40 + "\n"
            ticket += f"{'TOTAL:':<30}${ticket_info[1]:.2f}\n"
            ticket += f"Método de pago: {ticket_info[2].upper()}\n"
            ticket += "=" * 40 + "\n"
            ticket += "      ¡Gracias por su preferencia!\n"
            ticket += "=" * 40 + "\n"
            
            return ticket
            
        except Exception as e:
            print(f"❌ Error generando formato: {e}")
            return ""