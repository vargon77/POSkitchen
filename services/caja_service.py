# services/caja_service.py
import psycopg2
from typing import List, Dict, Optional
from datetime import datetime, date

class CajaService:
    def __init__(self, db_service):
        self.db = db_service
        self.caja_abierta = False
        self.cierre_actual = None
    
    def verificar_caja_abierta(self) -> bool:
        """Verificar si hay caja abierta hoy"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT COUNT(*) 
                FROM movimientos_caja 
                WHERE tipo = 'apertura' 
                AND DATE(created_at) = CURRENT_DATE
            """)
            
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            
            self.caja_abierta = count > 0
            return self.caja_abierta
            
        except Exception as e:
            print(f"❌ Error verificando caja: {e}")
            return False
    
    def abrir_caja(self, empleado_id: int, fondo_inicial: float) -> bool:
        """Abrir caja con fondo inicial"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Registrar apertura
            cur.execute("""
                INSERT INTO movimientos_caja 
                (tipo, empleado_id, monto, detalles)
                VALUES (%s, %s, %s, %s)
            """, ('apertura', empleado_id, fondo_inicial, f'Apertura de caja - Fondo: ${fondo_inicial:.2f}'))
            
            # Crear registro de cierre para el día
            cur.execute("""
                INSERT INTO cierres_caja 
                (empleado_id, fondo_inicial, total_ventas)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (empleado_id, fondo_inicial, 0))
            
            cierre_id = cur.fetchone()[0]
            self.cierre_actual = cierre_id
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.caja_abierta = True
            print(f"✅ Caja abierta con fondo: ${fondo_inicial:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ Error abriendo caja: {e}")
            return False
    
    def registrar_pago(self, pedido_id: int, empleado_id: int, monto: float, 
                      metodo_pago: str = 'efectivo') -> bool:
        """Registrar pago de un pedido"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Registrar movimiento de caja
            cur.execute("""
                INSERT INTO movimientos_caja 
                (tipo, empleado_id, pedido_id, monto, metodo_pago, detalles)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('venta', empleado_id, pedido_id, monto, metodo_pago, 
                  f'Pago pedido #{pedido_id} - {metodo_pago}'))
            
            # Actualizar totales en cierre actual
            cur.execute("""
                UPDATE cierres_caja 
                SET total_ventas = total_ventas + %s,
                    total_efectivo = total_efectivo + CASE WHEN %s = 'efectivo' THEN %s ELSE 0 END,
                    total_tarjeta = total_tarjeta + CASE WHEN %s = 'tarjeta' THEN %s ELSE 0 END,
                    total_transferencia = total_transferencia + CASE WHEN %s = 'transferencia' THEN %s ELSE 0 END
                WHERE fecha = CURRENT_DATE
            """, (monto, metodo_pago, monto, metodo_pago, monto, metodo_pago, monto))
            
            # Cambiar estado del pedido a "pagado"
            cur.execute("""
                UPDATE pedidos 
                SET estado = 'entregado', total = %s
                WHERE id = %s
            """, (monto, pedido_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Pago registrado: Pedido #{pedido_id} - ${monto:.2f} ({metodo_pago})")
            return True
            
        except Exception as e:
            print(f"❌ Error registrando pago: {e}")
            return False
    
    def obtener_ventas_dia(self) -> Dict:
        """Obtener resumen de ventas del día actual"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    COUNT(*) as total_ventas,
                    COALESCE(SUM(monto), 0) as total_monto,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'efectivo' THEN monto ELSE 0 END), 0) as efectivo,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'tarjeta' THEN monto ELSE 0 END), 0) as tarjeta,
                    COALESCE(SUM(CASE WHEN metodo_pago = 'transferencia' THEN monto ELSE 0 END), 0) as transferencia
                FROM movimientos_caja 
                WHERE tipo = 'venta' 
                AND DATE(created_at) = CURRENT_DATE
            """)
            
            resultado = cur.fetchone()
            cur.close()
            conn.close()
            
            return {
                'total_ventas': resultado[0],
                'total_monto': float(resultado[1]),
                'efectivo': float(resultado[2]),
                'tarjeta': float(resultado[3]),
                'transferencia': float(resultado[4])
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo ventas: {e}")
            return {'total_ventas': 0, 'total_monto': 0, 'efectivo': 0, 'tarjeta': 0, 'transferencia': 0}
    
    def obtener_pedidos_pendientes_pago(self) -> List[Dict]:
        """Obtener pedidos listos para pagar (estado: listo)"""
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
                            'precio', ip.precio_unitario
                        )
                    ) as items
                FROM pedidos p
                JOIN empleados e ON p.empleado_id = e.id
                JOIN items_pedido ip ON p.id = ip.pedido_id
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE p.estado = 'listo'
                GROUP BY p.id, p.mesa, p.total, p.created_at, e.nombre
                ORDER BY p.created_at ASC
            """)
            
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
            print(f"❌ Error obteniendo pedidos pendientes: {e}")
            return []
    
    def cerrar_caja(self, empleado_id: int, observaciones: str = "") -> bool:
        """Cerrar caja y generar reporte - CORREGIDO"""
        try:
            # Obtener totales actualizados
            ventas = self.obtener_ventas_dia()
            
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Calcular total de cierre (fondo inicial + ventas efectivo)
            cur.execute("""
                SELECT fondo_inicial 
                FROM cierres_caja 
                WHERE fecha = CURRENT_DATE
            """)
            fondo_inicial_result = cur.fetchone()
            
            if not fondo_inicial_result:
                print("❌ No se encontró cierre para hoy")
                return False
                
            # Convertir Decimal a float explícitamente
            fondo_inicial = float(fondo_inicial_result[0])
            total_cierre = fondo_inicial + ventas['efectivo']
            
            # Actualizar cierre con totales finales
            cur.execute("""
                UPDATE cierres_caja 
                SET total_ventas = %s,
                    total_efectivo = %s,
                    total_tarjeta = %s,
                    total_transferencia = %s,
                    total_cierre = %s,
                    observaciones = %s
                WHERE fecha = CURRENT_DATE
            """, (
                float(ventas['total_monto']), 
                float(ventas['efectivo']), 
                float(ventas['tarjeta']), 
                float(ventas['transferencia']), 
                float(total_cierre), 
                observaciones
            ))
            
            # Registrar movimiento de cierre
            cur.execute("""
                INSERT INTO movimientos_caja 
                (tipo, empleado_id, monto, detalles)
                VALUES (%s, %s, %s, %s)
            """, ('cierre', empleado_id, float(total_cierre), f'Cierre de caja - Total: ${total_cierre:.2f}'))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.caja_abierta = False
            print(f"✅ Caja cerrada - Total: ${total_cierre:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ Error cerrando caja: {e}")
            return False    
    def obtener_cierre_actual(self):

        """Obtener información del cierre actual del día"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, fondo_inicial, total_ventas, total_efectivo, 
                    total_tarjeta, total_transferencia, total_cierre
                FROM cierres_caja 
                WHERE fecha = CURRENT_DATE
            """)
            
            resultado = cur.fetchone()
            cur.close()
            conn.close()
            
            if resultado:
                return {
                    'id': resultado[0],
                    'fondo_inicial': float(resultado[1]),
                    'total_ventas': float(resultado[2]),
                    'total_efectivo': float(resultado[3]),
                    'total_tarjeta': float(resultado[4]),
                    'total_transferencia': float(resultado[5]),
                    'total_cierre': float(resultado[6])
                }
            return None
            
        except Exception as e:
            print(f"❌ Error obteniendo cierre actual: {e}")
            return None
        
    def generar_reporte_cierre(self, empleado_id: int) -> Dict:
        """Generar reporte detallado para el cierre de caja"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Obtener información del cierre actual
            cur.execute("""
                SELECT 
                    cc.fondo_inicial,
                    cc.total_ventas,
                    cc.total_efectivo,
                    cc.total_tarjeta,
                    cc.total_transferencia,
                    cc.total_cierre,
                    e.nombre as empleado
                FROM cierres_caja cc
                JOIN empleados e ON cc.empleado_id = e.id
                WHERE cc.fecha = CURRENT_DATE
            """)
            
            cierre_info = cur.fetchone()
            
            if not cierre_info:
                return {"error": "No hay cierre para hoy"}
            
            # Obtener ventas por categoría
            cur.execute("""
                SELECT 
                    p.categoria,
                    COUNT(*) as cantidad,
                    SUM(ip.cantidad * ip.precio_unitario) as total
                FROM items_pedido ip
                JOIN productos p ON ip.producto_id = p.id
                JOIN pedidos ped ON ip.pedido_id = ped.id
                JOIN movimientos_caja mc ON ped.id = mc.pedido_id
                WHERE DATE(mc.created_at) = CURRENT_DATE
                AND mc.tipo = 'venta'
                GROUP BY p.categoria
                ORDER BY total DESC
            """)
            
            ventas_categoria = []
            for row in cur.fetchall():
                ventas_categoria.append({
                    'categoria': row[0],
                    'cantidad': row[1],
                    'total': float(row[2])
                })
            
            # Obtener productos más vendidos
            cur.execute("""
                SELECT 
                    p.nombre,
                    SUM(ip.cantidad) as total_vendido,
                    SUM(ip.cantidad * ip.precio_unitario) as ingreso
                FROM items_pedido ip
                JOIN productos p ON ip.producto_id = p.id
                JOIN pedidos ped ON ip.pedido_id = ped.id
                JOIN movimientos_caja mc ON ped.id = mc.pedido_id
                WHERE DATE(mc.created_at) = CURRENT_DATE
                AND mc.tipo = 'venta'
                GROUP BY p.id, p.nombre
                ORDER BY total_vendido DESC
                LIMIT 10
            """)
            
            productos_top = []
            for row in cur.fetchall():
                productos_top.append({
                    'nombre': row[0],
                    'cantidad': row[1],
                    'ingreso': float(row[2])
                })
            
            # Obtener resumen por método de pago
            cur.execute("""
                SELECT 
                    metodo_pago,
                    COUNT(*) as transacciones,
                    SUM(monto) as total
                FROM movimientos_caja
                WHERE tipo = 'venta'
                AND DATE(created_at) = CURRENT_DATE
                GROUP BY metodo_pago
            """)
            
            resumen_pagos = {}
            for row in cur.fetchall():
                resumen_pagos[row[0]] = {
                    'transacciones': row[1],
                    'total': float(row[2])
                }
            
            cur.close()
            conn.close()
            
            return {
                'fondo_inicial': float(cierre_info[0]),
                'total_ventas': float(cierre_info[1]),
                'total_efectivo': float(cierre_info[2]),
                'total_tarjeta': float(cierre_info[3]),
                'total_transferencia': float(cierre_info[4]),
                'total_cierre': float(cierre_info[5]),
                'empleado': cierre_info[6],
                'ventas_por_categoria': ventas_categoria,
                'productos_top': productos_top,
                'resumen_pagos': resumen_pagos,
                'fecha': datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return {"error": str(e)}

    def obtener_historial_cierres(self, dias: int = 7) -> List[Dict]:
        """Obtener historial de cierres de caja"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    cc.fecha,
                    e.nombre as empleado,
                    cc.fondo_inicial,
                    cc.total_ventas,
                    cc.total_efectivo,
                    cc.total_tarjeta,
                    cc.total_transferencia,
                    cc.total_cierre,
                    cc.observaciones
                FROM cierres_caja cc
                JOIN empleados e ON cc.empleado_id = e.id
                WHERE cc.fecha >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY cc.fecha DESC
            """, (dias,))
            
            historial = []
            for row in cur.fetchall():
                historial.append({
                    'fecha': row[0].strftime("%d/%m/%Y"),
                    'empleado': row[1],
                    'fondo_inicial': float(row[2]),
                    'total_ventas': float(row[3]),
                    'total_efectivo': float(row[4]),
                    'total_tarjeta': float(row[5]),
                    'total_transferencia': float(row[6]),
                    'total_cierre': float(row[7]),
                    'observaciones': row[8] or ""
                })
            
            cur.close()
            conn.close()
            
            return historial
            
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            return []
        
    def calcular_efectivo_teorico(self) -> Dict:
        """Calcular el efectivo teórico que debería haber en caja"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Obtener fondo inicial del día
            cur.execute("""
                SELECT fondo_inicial 
                FROM cierres_caja 
                WHERE fecha = CURRENT_DATE
            """)
            fondo_inicial_result = cur.fetchone()
            fondo_inicial = float(fondo_inicial_result[0]) if fondo_inicial_result else 0.0
            
            # Obtener ventas en efectivo del día
            cur.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM movimientos_caja 
                WHERE tipo = 'venta' 
                AND metodo_pago = 'efectivo'
                AND DATE(created_at) = CURRENT_DATE
            """)
            ventas_efectivo = float(cur.fetchone()[0])
            
            # Obtener devoluciones en efectivo (si las hay)
            cur.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM movimientos_caja 
                WHERE tipo = 'devolucion'
                AND metodo_pago = 'efectivo'
                AND DATE(created_at) = CURRENT_DATE
            """)
            devoluciones_efectivo = float(cur.fetchone()[0])
            
            cur.close()
            conn.close()
            
            # Cálculo del efectivo teórico
            efectivo_teorico = fondo_inicial + ventas_efectivo - devoluciones_efectivo
            
            return {
                'fondo_inicial': fondo_inicial,
                'ventas_efectivo': ventas_efectivo,
                'devoluciones_efectivo': devoluciones_efectivo,
                'efectivo_teorico': efectivo_teorico,
                'fecha': datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
        except Exception as e:
            print(f"❌ Error calculando efectivo teórico: {e}")
            return {'efectivo_teorico': 0.0, 'error': str(e)}

    def registrar_arqueo(self, empleado_id: int, efectivo_fisico: float, 
                        observaciones: str = "") -> Dict:
        """Registrar arqueo de caja y calcular diferencias"""
        try:
            # Calcular efectivo teórico
            teorico_data = self.calcular_efectivo_teorico()
            
            if 'error' in teorico_data:
                return {'success': False, 'error': teorico_data['error']}
            
            efectivo_teorico = teorico_data['efectivo_teorico']
            diferencia = efectivo_fisico - efectivo_teorico
            
            # Determinar estado
            if abs(diferencia) <= 0.10:  # Menos de 10 centavos de diferencia
                estado = "cuadrado"
                color_estado = "success"
            elif diferencia > 0:
                estado = "sobrante"
                color_estado = "warning"
            else:
                estado = "faltante" 
                color_estado = "error"
            
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            # Registrar arqueo en base de datos
            cur.execute("""
                INSERT INTO arqueos_caja 
                (empleado_id, efectivo_teorico, efectivo_fisico, diferencia, estado, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (empleado_id, efectivo_teorico, efectivo_fisico, diferencia, estado, observaciones))
            
            arqueo_id, created_at = cur.fetchone()
            
            # Actualizar el cierre actual con la información del arqueo
            cur.execute("""
                UPDATE cierres_caja 
                SET diferencia_arqueo = %s,
                    estado_arqueo = %s
                WHERE fecha = CURRENT_DATE
            """, (diferencia, estado))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'success': True,
                'arqueo_id': arqueo_id,
                'efectivo_teorico': efectivo_teorico,
                'efectivo_fisico': efectivo_fisico,
                'diferencia': diferencia,
                'estado': estado,
                'color_estado': color_estado,
                'fecha': created_at.strftime("%d/%m/%Y %H:%M")
            }
            
        except Exception as e:
            print(f"❌ Error registrando arqueo: {e}")
            return {'success': False, 'error': str(e)}

    def obtener_historial_arqueos(self, dias: int = 7) -> List[Dict]:
        """Obtener historial de arqueos"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    a.created_at,
                    e.nombre as empleado,
                    a.efectivo_teorico,
                    a.efectivo_fisico,
                    a.diferencia,
                    a.estado,
                    a.observaciones
                FROM arqueos_caja a
                JOIN empleados e ON a.empleado_id = e.id
                WHERE a.created_at >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY a.created_at DESC
            """, (dias,))
            
            historial = []
            for row in cur.fetchall():
                # Determinar color según estado
                if row[5] == "cuadrado":
                    color = (0.2, 0.6, 0.2, 1)  # Verde
                elif row[5] == "sobrante":
                    color = (0.8, 0.5, 0.1, 1)  # Naranja
                else:
                    color = (0.8, 0.2, 0.2, 1)  # Rojo
                    
                historial.append({
                    'fecha': row[0].strftime("%d/%m/%Y %H:%M"),
                    'empleado': row[1],
                    'efectivo_teorico': float(row[2]),
                    'efectivo_fisico': float(row[3]),
                    'diferencia': float(row[4]),
                    'estado': row[5],
                    'color_estado': color,
                    'observaciones': row[6] or ""
                })
            
            cur.close()
            conn.close()
            
            return historial
            
        except Exception as e:
            print(f"❌ Error obteniendo historial de arqueos: {e}")
            return []