# views/pedidos/cierre_cuenta_screen.py
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty, DictProperty, ListProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
import psycopg2
from typing import Dict, List, Optional

class CierreCuentaScreen(MDScreen):
    # Propiedades
    pedido_id = NumericProperty(0)
    pedido_data = DictProperty({})
    items_pedido = ListProperty([])
    total_original = NumericProperty(0.0)
    total_con_descuento = NumericProperty(0.0)
    metodo_pago = StringProperty("")
    mesa_seleccionada = StringProperty("")
    mesas_disponibles = ListProperty([])
    modo_division = BooleanProperty(False)
    items_seleccionados = ListProperty([])  # Para división de cuenta
    tickets_generados = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pedido_service = None
        self.caja_service = None
        self.ticket_service = None
        self.config_service = None
        self.pedidos_mesa = []  # Lista de pedidos de la mesa actual
    
    def on_enter(self):
        """Al entrar a la pantalla"""
        print("💰 Entrando a Cierre de Cuenta")
        self.inicializar_servicios()
        self.cargar_mesas_con_pedidos()
        self.limpiar_seleccion()
    
    def inicializar_servicios(self):
        """Inicializar servicios necesarios"""
        try:
            from services.database_service import PostgreSQLService
            from services.pedido_service import PedidoService
            from services.caja_service import CajaService
            from services.ticket_service import TicketService
            from services.config_service import ConfigService
            
            db = PostgreSQLService()
            self.pedido_service = PedidoService(db)
            self.caja_service = CajaService(db)
            self.config_service = ConfigService(db)
            # ✅ CORREGIDO: Tu TicketService ya tiene config integrado
            self.ticket_service = TicketService(db)
            print("✅ Servicios inicializados")
        except Exception as e:
            print(f"❌ Error inicializando servicios: {e}")
    
    def cargar_mesas_con_pedidos(self):
        """Cargar mesas que tienen pedidos abiertos"""
        try:
            empleado_id = self.obtener_empleado_actual()
            
            conn = psycopg2.connect(**self.pedido_service.db.conn_params)
            cur = conn.cursor()
            
            # Obtener mesas con pedidos abiertos y contar pedidos
            cur.execute("""
                SELECT 
                    p.mesa,
                    COUNT(DISTINCT p.id) as num_pedidos,
                    SUM(p.total) as total_mesa
                FROM pedidos p
                WHERE p.estado IN ('pendiente', 'preparacion', 'listo')
                GROUP BY p.mesa
                ORDER BY p.mesa
            """)
            
            self.mesas_disponibles = []
            for row in cur.fetchall():
                mesa = row[0]
                num_pedidos = row[1]
                total = float(row[2])
                self.mesas_disponibles.append(
                    f"Mesa {mesa} ({num_pedidos} pedidos - ${total:.2f})"
                )
            
            cur.close()
            conn.close()
            
            print(f"🏷️ {len(self.mesas_disponibles)} mesas con pedidos")
            
        except Exception as e:
            print(f"❌ Error cargando mesas: {e}")
            self.mesas_disponibles = []
    
    def cargar_pedidos_mesa(self, texto_mesa):
        """Cargar todos los pedidos de una mesa"""
        if not texto_mesa or texto_mesa == "Seleccionar Mesa":
            return
        
        try:
            # Extraer número de mesa del texto
            mesa = texto_mesa.split()[1]
            self.mesa_seleccionada = mesa
            
            conn = psycopg2.connect(**self.pedido_service.db.conn_params)
            cur = conn.cursor()
            
            # Obtener todos los pedidos de la mesa
            cur.execute("""
                SELECT 
                    p.id,
                    p.total,
                    p.estado,
                    p.created_at,
                    COUNT(ip.id) as num_items
                FROM pedidos p
                LEFT JOIN items_pedido ip ON p.id = ip.pedido_id
                WHERE p.mesa = %s 
                AND p.estado IN ('pendiente', 'preparacion', 'listo')
                GROUP BY p.id, p.total, p.estado, p.created_at
                ORDER BY p.created_at ASC
            """, (mesa,))
            
            self.pedidos_mesa = []
            for row in cur.fetchall():
                self.pedidos_mesa.append({
                    'id': row[0],
                    'total': float(row[1]),
                    'estado': row[2],
                    'fecha': row[3],
                    'num_items': row[4]
                })
            
            cur.close()
            conn.close()
            
            print(f"📋 {len(self.pedidos_mesa)} pedidos en Mesa {mesa}")
            
            # Actualizar UI con lista de pedidos
            self.actualizar_lista_pedidos()
            
            # Actualizar info de la mesa
            if hasattr(self, 'ids') and 'label_info_mesa' in self.ids:
                total_mesa = sum(p['total'] for p in self.pedidos_mesa)
                self.ids.label_info_mesa.text = f"{len(self.pedidos_mesa)} pedidos - Total: ${total_mesa:.2f}"
            
        except Exception as e:
            print(f"❌ Error cargando pedidos de mesa: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_lista_pedidos(self):
        """Actualizar lista visual de pedidos"""
        if not hasattr(self, 'ids') or 'lista_pedidos' not in self.ids:
            return
        
        self.ids.lista_pedidos.clear_widgets()
        
        for pedido in self.pedidos_mesa:
            # Color según estado
            estado_colors = {
                'pendiente': (0.9, 0.6, 0.1, 1),
                'preparacion': (0.1, 0.6, 0.9, 1),
                'listo': (0.2, 0.7, 0.3, 1)
            }
            
            btn = Button(
                text=f"Pedido #{pedido['id']}\n"
                     f"${pedido['total']:.2f} - {pedido['num_items']} items\n"
                     f"{pedido['estado'].upper()}",
                size_hint_y=None,
                height=80,
                background_color=estado_colors.get(pedido['estado'], (0.5, 0.5, 0.5, 1)),
                background_normal='',
                font_size='12sp'
            )
            btn.bind(on_press=lambda instance, p=pedido: self.seleccionar_pedido(p['id']))
            self.ids.lista_pedidos.add_widget(btn)
    
    def seleccionar_pedido(self, pedido_id):
        """Seleccionar un pedido para ver su detalle"""
        self.pedido_id = pedido_id
        self.cargar_detalle_pedido()
    
    def cargar_detalle_pedido(self):
        """Cargar detalle completo del pedido seleccionado"""
        try:
            conn = psycopg2.connect(**self.pedido_service.db.conn_params)
            cur = conn.cursor()
            
            # Obtener info del pedido
            cur.execute("""
                SELECT id, mesa, total, estado
                FROM pedidos 
                WHERE id = %s
            """, (self.pedido_id,))
            
            pedido_info = cur.fetchone()
            if not pedido_info:
                return
            
            self.pedido_data = {
                'id': pedido_info[0],
                'mesa': pedido_info[1],
                'total': float(pedido_info[2]),
                'estado': pedido_info[3]
            }
            
            # Obtener items del pedido
            cur.execute("""
                SELECT 
                    ip.id,
                    pr.nombre,
                    ip.cantidad,
                    ip.precio_unitario,
                    (ip.cantidad * ip.precio_unitario) as subtotal,
                    ip.notas
                FROM items_pedido ip
                JOIN productos pr ON ip.producto_id = pr.id
                WHERE ip.pedido_id = %s
                ORDER BY pr.nombre
            """, (self.pedido_id,))
            
            self.items_pedido = []
            for row in cur.fetchall():
                self.items_pedido.append({
                    'id': row[0],
                    'nombre': row[1],
                    'cantidad': row[2],
                    'precio_unitario': float(row[3]),
                    'subtotal': float(row[4]),
                    'notas': row[5] or '',
                    'cantidad_seleccionada': 0  # Para división
                })
            
            cur.close()
            conn.close()
            
            self.total_original = self.pedido_data['total']
            self.total_con_descuento = self.total_original
            
            # Actualizar UI
            self.actualizar_detalle_items()
            self.actualizar_info_pedido()
            
            print(f"📋 Pedido #{self.pedido_id} cargado: {len(self.items_pedido)} items")
            
        except Exception as e:
            print(f"❌ Error cargando detalle: {e}")
            import traceback
            traceback.print_exc()
    
    def actualizar_detalle_items(self):
        """Actualizar lista visual de items"""
        if not hasattr(self, 'ids') or 'detalle_items' not in self.ids:
            return
        
        self.ids.detalle_items.clear_widgets()
        
        for item in self.items_pedido:
            item_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=35,
                spacing=5,
                padding=[5, 2]
            )
            
            # Checkbox (solo visible en modo división)
            checkbox_container = BoxLayout(size_hint_x=0.08)
            if self.modo_division:
                cb = CheckBox(size_hint=(None, None), size=(25, 25))
                cb.bind(active=lambda instance, value, it=item: self.toggle_item_seleccion(it, value))
                checkbox_container.add_widget(cb)
            item_layout.add_widget(checkbox_container)
            
            # Nombre
            lbl_nombre = Label(
                text=item['nombre'],
                size_hint_x=0.42,
                text_size=(None, None),
                halign='left',
                valign='middle',
                font_size='11sp'
            )
            item_layout.add_widget(lbl_nombre)
            
            # Cantidad (editable en modo división)
            if self.modo_division:
                txt_cant = TextInput(
                    text=str(item['cantidad']),
                    size_hint_x=0.15,
                    multiline=False,
                    input_filter='int',
                    font_size='11sp'
                )
                txt_cant.bind(text=lambda instance, value, it=item: self.actualizar_cantidad_seleccionada(it, value))
                item_layout.add_widget(txt_cant)
            else:
                lbl_cant = Label(
                    text=str(item['cantidad']),
                    size_hint_x=0.15,
                    halign='center',
                    font_size='11sp'
                )
                item_layout.add_widget(lbl_cant)
            
            # Precio unitario
            lbl_precio = Label(
                text=f"${item['precio_unitario']:.2f}",
                size_hint_x=0.15,
                halign='center',
                font_size='11sp'
            )
            item_layout.add_widget(lbl_precio)
            
            # Subtotal
            lbl_subtotal = Label(
                text=f"${item['subtotal']:.2f}",
                size_hint_x=0.2,
                halign='right',
                font_size='11sp',
                bold=True
            )
            item_layout.add_widget(lbl_subtotal)
            
            self.ids.detalle_items.add_widget(item_layout)
    
    def actualizar_info_pedido(self):
        """Actualizar info del pedido en el header"""
        if not hasattr(self, 'ids'):
            return
        
        if 'label_pedido_actual' in self.ids:
            self.ids.label_pedido_actual.text = f"Pedido #{self.pedido_data['id']} - Mesa {self.pedido_data['mesa']}"
        
        if 'label_total_pedido' in self.ids:
            self.ids.label_total_pedido.text = f"Total: ${self.pedido_data['total']:.2f}"
        
        if 'label_total_final' in self.ids:
            self.ids.label_total_final.text = f"${self.total_con_descuento:.2f}"
        
        # Habilitar botones
        if 'btn_pagar_todo' in self.ids:
            self.ids.btn_pagar_todo.disabled = False
    
    def cambiar_modo_division(self, state):
        """Cambiar entre modo normal y modo división"""
        self.modo_division = (state == 'down')
        print(f"🔄 Modo división: {self.modo_division}")
        
        # Actualizar UI
        self.actualizar_detalle_items()
        
        # Habilitar/deshabilitar botón de ticket
        if hasattr(self, 'ids') and 'btn_generar_ticket' in self.ids:
            self.ids.btn_generar_ticket.disabled = not self.modo_division
    
    def toggle_item_seleccion(self, item, activo):
        """Marcar/desmarcar item para división"""
        if activo:
            if item not in self.items_seleccionados:
                self.items_seleccionados.append(item)
        else:
            if item in self.items_seleccionados:
                self.items_seleccionados.remove(item)
        
        # Recalcular total
        self.recalcular_total_seleccion()
    
    def actualizar_cantidad_seleccionada(self, item, valor):
        """Actualizar cantidad seleccionada para división"""
        try:
            cantidad = int(valor) if valor else 0
            if cantidad > item['cantidad']:
                cantidad = item['cantidad']
            item['cantidad_seleccionada'] = cantidad
            self.recalcular_total_seleccion()
        except ValueError:
            pass
    
    def recalcular_total_seleccion(self):
        """Recalcular total basado en items seleccionados"""
        if not self.modo_division:
            self.total_con_descuento = self.total_original
        else:
            total = 0
            for item in self.items_seleccionados:
                cant = item.get('cantidad_seleccionada', item['cantidad'])
                total += cant * item['precio_unitario']
            self.total_con_descuento = total
        
        if hasattr(self, 'ids') and 'label_total_final' in self.ids:
            self.ids.label_total_final.text = f"${self.total_con_descuento:.2f}"
    
    def aplicar_descuento(self, tipo):
        """Aplicar descuento (porcentaje o monto)"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text=f"DESCUENTO POR {tipo.upper()}",
            font_size='16sp',
            bold=True
        ))
        
        input_valor = TextInput(
            hint_text='10' if tipo == 'porcentaje' else '50.00',
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=40
        )
        content.add_widget(input_valor)
        
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        btn_cancelar = Button(text='CANCELAR', background_color=(0.8, 0.3, 0.3, 1))
        btn_aplicar = Button(text='APLICAR', background_color=(0.2, 0.7, 0.2, 1))
        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_aplicar)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Descuento', content=content, size_hint=(0.5, 0.3))
        
        def aplicar(instance):
            try:
                valor = float(input_valor.text)
                if tipo == 'porcentaje':
                    if valor > 100:
                        valor = 100
                    descuento = self.total_con_descuento * (valor / 100)
                else:
                    descuento = valor
                
                self.total_con_descuento -= descuento
                self.actualizar_info_pedido()
                popup.dismiss()
            except ValueError:
                pass
        
        btn_cancelar.bind(on_press=popup.dismiss)
        btn_aplicar.bind(on_press=aplicar)
        popup.open()
    
    def dividir_entre_personas(self):
        """Dividir cuenta entre N personas"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(text="¿Entre cuántas personas?", bold=True))
        
        input_personas = TextInput(
            hint_text='2, 3, 4...',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=40
        )
        content.add_widget(input_personas)
        
        lbl_resultado = Label(text="", font_size='14sp', bold=True)
        content.add_widget(lbl_resultado)
        
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        btn_cancelar = Button(text='CANCELAR', background_color=(0.8, 0.3, 0.3, 1))
        btn_calcular = Button(text='CALCULAR', background_color=(0.2, 0.7, 0.2, 1))
        btn_layout.add_widget(btn_cancelar)
        btn_layout.add_widget(btn_calcular)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Dividir Cuenta', content=content, size_hint=(0.5, 0.4))
        
        def calcular(instance):
            try:
                personas = int(input_personas.text)
                if personas > 0:
                    por_persona = self.total_con_descuento / personas
                    lbl_resultado.text = f"Por persona: ${por_persona:.2f}"
            except ValueError:
                pass
        
        btn_cancelar.bind(on_press=popup.dismiss)
        btn_calcular.bind(on_press=calcular)
        popup.open()
    
    def pagar_pedido_completo(self):
        """Pagar el pedido completo"""
        if not self.metodo_pago:
            self.mostrar_mensaje("Seleccione un método de pago")
            return
        
        # Confirmar pago
        self.confirmar_pago_final(self.pedido_id, self.items_pedido, self.total_con_descuento)
    
    def generar_ticket_parcial(self):
        """Generar ticket parcial con items seleccionados"""
        if not self.items_seleccionados:
            self.mostrar_mensaje("Seleccione items para el ticket")
            return
        
        if not self.metodo_pago:
            self.mostrar_mensaje("Seleccione un método de pago")
            return
        
        # Crear ticket parcial
        try:
            conn = psycopg2.connect(**self.pedido_service.db.conn_params)
            cur = conn.cursor()
            
            # Crear ticket
            numero_ticket = len(self.tickets_generados) + 1
            cur.execute("""
                INSERT INTO tickets (pedido_id, numero_ticket, total, metodo_pago, empleado_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (self.pedido_id, numero_ticket, self.total_con_descuento, 
                  self.metodo_pago, self.obtener_empleado_actual()))
            
            ticket_id = cur.fetchone()[0]
            
            # Agregar items al ticket
            for item in self.items_seleccionados:
                cant = item.get('cantidad_seleccionada', item['cantidad'])
                subtotal = cant * item['precio_unitario']
                
                cur.execute("""
                    INSERT INTO items_ticket (ticket_id, item_pedido_id, cantidad_asignada, subtotal)
                    VALUES (%s, %s, %s, %s)
                """, (ticket_id, item['id'], cant, subtotal))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.tickets_generados.append({
                'id': ticket_id,
                'numero': numero_ticket,
                'total': self.total_con_descuento
            })
            
            # Actualizar UI
            if hasattr(self, 'ids') and 'label_tickets_info' in self.ids:
                total_tickets = sum(t['total'] for t in self.tickets_generados)
                self.ids.label_tickets_info.text = f"Tickets generados: {len(self.tickets_generados)} - Total: ${total_tickets:.2f}"
            
            self.mostrar_mensaje(f"✅ Ticket #{numero_ticket} generado")
            
            # Limpiar selección
            self.items_seleccionados = []
            self.modo_division = False
            self.cargar_detalle_pedido()
            
        except Exception as e:
            print(f"❌ Error generando ticket: {e}")
            self.mostrar_mensaje("Error al generar ticket")
    
    def confirmar_pago_final(self, pedido_id, items, total):
        """Confirmar y procesar pago final"""
        # Registrar pago
        if self.caja_service.registrar_pago(
            pedido_id,
            self.obtener_empleado_actual(),
            total,
            self.metodo_pago
        ):
            # Cambiar estado
            self.pedido_service.cambiar_estado_pedido(pedido_id, 'pagado')
            
            # Imprimir ticket
            self.imprimir_ticket_final()
            
            self.mostrar_mensaje("✅ Pago procesado exitosamente")
            
            # Recargar mesas
            Clock.schedule_once(lambda dt: self.cargar_mesas_con_pedidos(), 1)
            Clock.schedule_once(lambda dt: self.limpiar_seleccion(), 1.5)
    
    def imprimir_ticket_final(self):
        """Imprimir ticket final"""
        try:
            ticket_data = self.ticket_service.generar_ticket_pago(self.pedido_id)
            ticket_text = self.ticket_service.formatear_ticket_texto(ticket_data)
            self.ticket_service.imprimir_ticket(ticket_text)
        except Exception as e:
            print(f"❌ Error imprimiendo: {e}")
    
    def limpiar_seleccion(self):
        """Limpiar toda la selección"""
        self.pedido_id = 0
        self.pedido_data = {}
        self.items_pedido = []
        self.items_seleccionados = []
        self.tickets_generados = []
        self.modo_division = False
        self.total_original = 0.0
        self.total_con_descuento = 0.0
        self.metodo_pago = ""
        
        if hasattr(self, 'ids'):
            if 'detalle_items' in self.ids:
                self.ids.detalle_items.clear_widgets()
            if 'label_pedido_actual' in self.ids:
                self.ids.label_pedido_actual.text = "Seleccione un pedido"
            if 'label_total_final' in self.ids:
                self.ids.label_total_final.text = "$0.00"
    
    def volver_al_menu(self):
        """Volver al menú"""
        self.manager.current = "menu"
    
    def obtener_empleado_actual(self):
        """Obtener ID del empleado actual"""
        return 1  # Temporal
    
    def mostrar_mensaje(self, mensaje):
        """Mostrar mensaje simple"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=10)
        content.add_widget(Label(text=mensaje))
        btn = Button(text='OK', size_hint_y=None, height=40)
        content.add_widget(btn)
        popup = Popup(title='', content=content, size_hint=(0.4, 0.2))
        btn.bind(on_press=popup.dismiss)
        popup.open()