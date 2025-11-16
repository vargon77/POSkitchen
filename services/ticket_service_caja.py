# services/ticket_service.py 
import os
from datetime import datetime
from typing import Dict, List
import psycopg2

class TicketServiceCaja:
    def __init__(self, db_service, config_service):  # CAMBIAR: agregar config_service
        self.db = db_service
        self.config_service = config_service  # CAMBIAR: usar config_service
        print("✅ TicketService inicializado con ConfigService")
    
    def generar_ticket_pago(self, pedido_id: int) -> Dict:
        """Generar contenido para ticket de pago - USANDO CONFIG SERVICE"""
        try:
            # CAMBIAR: Obtener configuración dinámica
            empresa_config = self.config_service.obtener_config_empresa()
            print(f"🎫 Generando ticket con configuración: {empresa_config['nombre']}")
            
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Obtener información del pedido (SIN requerir movimiento de caja)
            cur.execute("""
                SELECT 
                    p.id,
                    p.mesa,
                    p.total,
                    p.created_at,
                    e.nombre as mesero,
                    p.estado
                FROM pedidos p
                JOIN empleados e ON p.empleado_id = e.id
                WHERE p.id = %s
            """, (pedido_id,))
            
            pedido_info = cur.fetchone()
            
            if not pedido_info:
                return {"error": "Pedido no encontrado"}
            
            # Obtener método de pago si existe
            cur.execute("""
                SELECT metodo_pago, created_at 
                FROM movimientos_caja 
                WHERE pedido_id = %s AND tipo = 'venta'
                LIMIT 1
            """, (pedido_id,))
            
            pago_info = cur.fetchone()
            metodo_pago = pago_info[0] if pago_info else "EFECTIVO"
            fecha_pago = pago_info[1] if pago_info else datetime.now()
            
            # Obtener items del pedido
            cur.execute("""
                SELECT 
                    pr.nombre,
                    ip.cantidad,
                    ip.precio_unitario,
                    (ip.cantidad * ip.precio_unitario) as subtotal
                FROM items_pedido ip
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE ip.pedido_id = %s
                ORDER BY pr.nombre
            """, (pedido_id,))
            
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
            
            # Calcular totales
            subtotal = sum(item['subtotal'] for item in items)
            iva = subtotal * 0.16  # 16% IVA
            total = subtotal + iva
            
            # Construir ticket - CAMBIAR: usar empresa_config dinámico
            ticket = {
                'empresa': empresa_config,  # CAMBIAR: no usar self.empresa_config
                'pedido': {
                    'id': pedido_info[0],
                    'mesa': pedido_info[1],
                    'total': float(pedido_info[2]),
                    'fecha_pedido': pedido_info[3].strftime("%d/%m/%Y %H:%M"),
                    'fecha_pago': fecha_pago.strftime("%d/%m/%Y %H:%M"),
                    'mesero': pedido_info[4],
                    'metodo_pago': metodo_pago,
                    'estado': pedido_info[5]
                },
                'items': items,
                'totales': {
                    'subtotal': subtotal,
                    'iva': iva,
                    'total': total
                },
                'codigo_qr': f"PEDIDO#{pedido_id}_{datetime.now().strftime('%Y%m%d')}"
            }
            
            return ticket
            
        except Exception as e:
            print(f"❌ Error generando ticket: {e}")
            return {"error": str(e)}
    
    def generar_ticket_cocina(self, pedido_id: int) -> str:
        """Generar ticket para cocina"""
        try:
            # CAMBIAR: Obtener configuración dinámica para cocina también
            empresa_config = self.config_service.obtener_config_empresa()
            
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Obtener información del pedido para cocina
            cur.execute("""
                SELECT 
                    p.id,
                    p.mesa,
                    p.created_at,
                    e.nombre as mesero
                FROM pedidos p
                JOIN empleados e ON p.empleado_id = e.id
                WHERE p.id = %s
            """, (pedido_id,))
            
            pedido_info = cur.fetchone()
            
            if not pedido_info:
                return "Error: Pedido no encontrado"
            
            # Obtener items para cocina
            cur.execute("""
                SELECT 
                    pr.nombre,
                    ip.cantidad,
                    COALESCE(ip.notas, '') as notas
                FROM items_pedido ip
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE ip.pedido_id = %s
                ORDER BY pr.categoria, pr.nombre
            """, (pedido_id,))
            
            items = cur.fetchall()
            
            cur.close()
            conn.close()
            
            # Formatear ticket de cocina - CAMBIAR: incluir nombre de empresa
            lines = []
            lines.append("=" * 40)
            lines.append(f"{empresa_config['nombre']:^40}")  # CAMBIAR: nombre dinámico
            lines.append(f"{'COCINA':^40}")
            lines.append(f"{'*** ORDEN ***':^40}")
            lines.append("=" * 40)
            lines.append(f"Pedido: #{pedido_info[0]}")
            lines.append(f"Mesa: {pedido_info[1]}")
            lines.append(f"Mesero: {pedido_info[3]}")
            lines.append(f"Hora: {pedido_info[2].strftime('%H:%M')}")
            lines.append("-" * 40)
            
            for item in items:
                line = f"{item[1]}x {item[0]}"
                if item[2] and item[2].strip():
                    line += f" - {item[2]}"
                lines.append(line)
            
            lines.append("=" * 40)
            lines.append(f"{'¡Buen provecho!':^40}")
            lines.append("=" * 40)
            
            return "\n".join(lines)
            
        except Exception as e:
            print(f"❌ Error generando ticket cocina: {e}")
            return f"Error: {e}"
    
    def formatear_ticket_texto(self, ticket_data: Dict) -> str:
        """Formatear ticket como texto para impresión"""
        if 'error' in ticket_data:
            return f"Error: {ticket_data['error']}"
        
        empresa = ticket_data['empresa']  # Esto ahora viene de config_service
        pedido = ticket_data['pedido']
        items = ticket_data['items']
        totales = ticket_data['totales']
        
        # Encabezado
        lines = []
        lines.append("=" * 40)
        lines.append(f"{empresa['nombre']:^40}")
        lines.append(f"{empresa['direccion']:^40}")
        lines.append(f"Tel: {empresa['telefono']:^40}")
        lines.append(f"RFC: {empresa['rfc']:^40}")
        lines.append("=" * 40)
        
        # Información del pedido
        lines.append(f"Ticket: #{pedido['id']}")
        lines.append(f"Fecha: {pedido['fecha_pago']}")
        lines.append(f"Mesa: {pedido['mesa']}")
        lines.append(f"Mesero: {pedido['mesero']}")
        lines.append(f"Pago: {pedido['metodo_pago'].upper()}")
        lines.append("-" * 40)
        
        # Items
        lines.append(f"{'CANT DESCRIPCION':<20} {'TOTAL':>20}")
        lines.append("-" * 40)
        
        for item in items:
            nombre = item['nombre'][:18]
            line = f"{item['cantidad']:>2} x {nombre:<15}"
            line += f"${item['subtotal']:>7.2f}"
            lines.append(line)
        
        lines.append("-" * 40)
        
        # Totales
        lines.append(f"{'Subtotal:':<30} ${totales['subtotal']:>7.2f}")
        lines.append(f"{'IVA (16%):':<30} ${totales['iva']:>7.2f}")
        lines.append(f"{'TOTAL:':<30} ${totales['total']:>7.2f}")
        lines.append("=" * 40)
        
        # Footer - CAMBIAR: usar leyenda dinámica
        lines.append(f"{empresa['leyenda_footer']:^40}")
        lines.append(f"{'*** COMPROBANTE DE PAGO ***':^40}")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def imprimir_ticket(self, ticket_text: str, impresora_nombre: str = None):
        """Imprimir ticket en impresora térmica"""
        try:
            # Guardar en archivo para pruebas
            archivo = self.guardar_ticket_archivo(ticket_text)
            
            # Mostrar en consola para debug
            print("\n" + "="*50)
            print("PREVIEW DEL TICKET:")
            print("="*50)
            print(ticket_text)
            print("="*50)
            print(f"✅ Ticket guardado en: {archivo}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error imprimiendo ticket: {e}")
            return False
    
    def guardar_ticket_archivo(self, ticket_text: str):
        """Guardar ticket en archivo para pruebas"""
        try:
            os.makedirs("tickets", exist_ok=True)
            filename = f"tickets/ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(ticket_text)
            return filename
        except Exception as e:
            print(f"❌ Error guardando ticket: {e}")
            return None