# views/pedidos/cierre_cuenta_screen.py - VERSIÓN PROFESIONAL
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.properties import (NumericProperty, DictProperty, ListProperty, 
                            StringProperty, BooleanProperty, ObjectProperty)
from kivy.clock import Clock
from kivy.metrics import dp
import psycopg2
from typing import Dict, List
from themes.design_system import ds_color, ds_spacing
from kivymd.app import MDApp

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
    pedidos_mesa = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pedido_service = None
        self.caja_service = None
        self.ticket_service = None
        self.dialog = None
    
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
            
            db = PostgreSQLService()
            self.pedido_service = PedidoService(db)
            self.caja_service = CajaService(db)
            self.ticket_service = TicketService(db)
            print("✅ Servicios de cierre inicializados")
        except Exception as e:
            print(f"❌ Error inicializando servicios: {e}")
    
    def cargar_mesas_con_pedidos(self):
        """Cargar mesas que tienen pedidos abiertos"""
        try:
            conn = psycopg2.connect(**self.pedido_service.db.conn_params)
            cur = conn.cursor()
            
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
                    f"Mesa {mesa} - {num_pedidos}p - ${total:.2f}"
                )
            
            cur.close()
            conn.close()
            
            print(f"🏷️ {len(self.mesas_disponibles)} mesas con pedidos")
            
        except Exception as e:
            print(f"❌ Error cargando mesas: {e}")
            self.mesas_disponibles = []
    
    def cargar_pedidos_mesa(self, texto_mesa):
        """Cargar todos los pedidos de una mesa"""
        if not texto_mesa or "Seleccionar" in texto_mesa:
            return
        
        try:
            # Extraer número de mesa
            mesa = texto_mesa.split()[1]
            self.mesa_seleccionada = mesa
            
            conn = psycopg2.connect(**self.pedido_service.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    p.id,
                    p.total,
                    p.estado,
                    COUNT(ip.id) as num_items
                FROM pedidos p
                LEFT JOIN items_pedido ip ON p.id = ip.pedido_id
                WHERE p.mesa = %s 
                AND p.estado IN ('pendiente', 'preparacion', 'listo')
                GROUP BY p.id, p.total, p.estado
                ORDER BY p.created_at ASC
            """, (mesa,))
            
            self.pedidos_mesa = []
            for row in cur.fetchall():
                self.pedidos_mesa.append({
                    'id': row[0],
                    'total': float(row[1]),
                    'estado': row[2],
                    'num_items': row[3]
                })
            
            cur.close()
            conn.close()
            
            print(f"📋 {len(self.pedidos_mesa)} pedidos en Mesa {mesa}")
            
            # Actualizar UI
            self.actualizar_lista_pedidos()
            self.actualizar_info_mesa()
            
        except Exception as e:
            print(f"❌ Error cargando pedidos: {e}")
            self.mostrar_error("Error cargando pedidos")
    
    def actualizar_info_mesa(self):
        """Actualizar info rápida de la mesa"""
        if hasattr(self, 'ids') and 'info_mesa_rapida' in self.ids:
            if self.pedidos_mesa:
                total = sum(p['total'] for p in self.pedidos_mesa)
                self.ids.info_mesa_rapida.text = f"{len(self.pedidos_mesa)} pedidos - ${total:.2f}"
    
    def actualizar_lista_pedidos(self):
        """Actualizar lista visual de pedidos"""
        if not hasattr(self, 'ids') or 'lista_pedidos' not in self.ids:
            return
        
        self.ids.lista_pedidos.clear_widgets()
        
        if not self.pedidos_mesa:
            empty_label = MDLabel(
                text="Sin pedidos",
                halign="center",
                theme_text_color="Secondary",
                italic=True
            )
            self.ids.lista_pedidos.add_widget(empty_label)
            return
        
        for pedido in self.pedidos_mesa:
            card = PedidoItemCompact(
                pedido_id=pedido['id'],
                pedido_total=pedido['total'],
                pedido_estado=pedido['estado'],
                num_items=pedido['num_items']
            )
            card.bind(on_press=lambda instance, p=pedido: self.seleccionar_pedido(p['id']))
            self.ids.lista_pedidos.add_widget(card)
        
        # Actualizar contador
        if 'label_count_pedidos' in self.ids:
            self.ids.label_count_pedidos.text = f"{len(self.pedidos_mesa)} pedidos"
    
    def seleccionar_pedido(self, pedido_id):
        """Seleccionar un pedido para ver detalle"""
        self.pedido_id = pedido_id
        self.cargar_detalle_pedido()
    
    def cargar_detalle_pedido(self):
        """Cargar detalle completo del pedido"""
        try:
            conn = psycopg2.connect(**self.pedido_service.db.conn_params)
            cur = conn.cursor()
            
            # Info del pedido
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
            
            # Items del pedido
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
            """, (self.pedido_id,))
            
            self.items_pedido = []
            for row in cur.fetchall():
                self.items_pedido.append({
                    'nombre': row[0],
                    'cantidad': row[1],
                    'precio_unitario': float(row[2]),
                    'subtotal': float(row[3])
                })
            
            cur.close()
            conn.close()
            
            self.total_original = self.pedido_data['total']
            self.total_con_descuento = self.total_original
            
            # Actualizar UI
            self.actualizar_ui_detalle()
            
            print(f"📋 Pedido #{self.pedido_id} cargado: {len(self.items_pedido)} items")
            
        except Exception as e:
            print(f"❌ Error cargando detalle: {e}")
            self.mostrar_error("Error al cargar detalle")
    
    def actualizar_ui_detalle(self):
        """Actualizar UI del detalle del pedido"""
        if not hasattr(self, 'ids'):
            return
        
        # Header info
        if 'label_pedido_info' in self.ids:
            self.ids.label_pedido_info.text = f"Pedido #{self.pedido_data['id']} - Mesa {self.pedido_data['mesa']}"
        
        if 'label_total_pedido' in self.ids:
            self.ids.label_total_pedido.text = f"${self.pedido_data['total']:.2f}"
        
        if 'label_total_final' in self.ids:
            self.ids.label_total_final.text = f"${self.total_con_descuento:.2f}"
        
        # Habilitar botones
        if 'btn_pagar_completo' in self.ids:
            self.ids.btn_pagar_completo.disabled = False
        
        if 'btn_confirmar_pago' in self.ids:
            self.ids.btn_confirmar_pago.disabled = (not self.metodo_pago)
        
        # Actualizar tabla de items
        self.actualizar_tabla_items()
    
    def actualizar_tabla_items(self):
        """Actualizar tabla de items del pedido"""
        if not hasattr(self, 'ids') or 'detalle_items' not in self.ids:
            return
        
        self.ids.detalle_items.clear_widgets()
        
        if not self.items_pedido:
            empty_label = MDLabel(
                text="Sin items",
                halign="center",
                theme_text_color="Secondary"
            )
            self.ids.detalle_items.add_widget(empty_label)
            return
        
        for item in self.items_pedido:
            fila = ItemFilaTabla(
                item_nombre=item['nombre'],
                item_cantidad=item['cantidad'],
                item_precio=item['precio_unitario'],
                item_subtotal=item['subtotal']
            )
            self.ids.detalle_items.add_widget(fila)
    
    def seleccionar_metodo(self, metodo):
        """Seleccionar método de pago"""
        self.metodo_pago = metodo
        print(f"💳 Método seleccionado: {metodo}")
        
        # Actualizar visual de chips
        if hasattr(self, 'ids'):
            chips = {
                'efectivo': 'chip_efectivo',
                'tarjeta': 'chip_tarjeta',
                'transferencia': 'chip_transfer'
            }
            
            for met, chip_id in chips.items():
                if chip_id in self.ids:
                    chip = self.ids[chip_id]
                    if met == metodo:
                        chip.md_bg_color = ds_color('primary')
                        chip.text_color = ds_color('white')
                    else:
                        chip.md_bg_color = ds_color('gray_light')
                        chip.text_color = ds_color('dark')
        
        # Habilitar botón confirmar
        if 'btn_confirmar_pago' in self.ids:
            self.ids.btn_confirmar_pago.disabled = False
    
    def aplicar_descuento(self):
        """Aplicar descuento al total"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(180)
        )
        
        content.add_widget(MDLabel(
            text="Aplicar Descuento",
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Tabs para tipo de descuento
        tipo_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        from kivymd.uix.button import MDRectangleFlatButton
        btn_porcentaje = MDRectangleFlatButton(text="PORCENTAJE %")
        btn_monto = MDRectangleFlatButton(text="MONTO $")
        
        tipo_layout.add_widget(btn_porcentaje)
        tipo_layout.add_widget(btn_monto)
        content.add_widget(tipo_layout)
        
        input_valor = MDTextField(
            hint_text="Valor del descuento",
            mode="rectangle",
            input_filter="float",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_valor)
        
        self.dialog = MDDialog(
            title="Descuento",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="APLICAR",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: self._aplicar_descuento_confirm(input_valor.text, 'porcentaje')
                )
            ]
        )
        
        # Configurar tipo
        tipo_actual = ['porcentaje']
        
        def set_porcentaje(instance):
            tipo_actual[0] = 'porcentaje'
            btn_porcentaje.md_bg_color = ds_color('primary')
            btn_monto.md_bg_color = ds_color('gray_light')
        
        def set_monto(instance):
            tipo_actual[0] = 'monto'
            btn_monto.md_bg_color = ds_color('primary')
            btn_porcentaje.md_bg_color = ds_color('gray_light')
        
        btn_porcentaje.bind(on_press=set_porcentaje)
        btn_monto.bind(on_press=set_monto)
        
        # Configurar botón aplicar
        def aplicar_con_tipo(instance):
            self._aplicar_descuento_confirm(input_valor.text, tipo_actual[0])
        
        self.dialog.buttons[1].unbind(on_release=self.dialog.buttons[1].get_property_observers('on_release')[0])
        self.dialog.buttons[1].bind(on_release=aplicar_con_tipo)
        
        self.dialog.open()
    
    def _aplicar_descuento_confirm(self, valor_str, tipo):
        """Confirmar aplicación de descuento"""
        try:
            valor = float(valor_str)
            
            if tipo == 'porcentaje':
                if valor < 0 or valor > 100:
                    self.mostrar_error("El porcentaje debe estar entre 0 y 100")
                    return
                descuento = self.total_original * (valor / 100)
            else:
                descuento = valor
            
            if descuento > self.total_original:
                self.mostrar_error("El descuento no puede ser mayor al total")
                return
            
            self.total_con_descuento = self.total_original - descuento
            self.actualizar_ui_detalle()
            self.dialog.dismiss()
            
            print(f"💰 Descuento aplicado: ${descuento:.2f}")
            
        except ValueError:
            self.mostrar_error("Valor inválido")
    
    def pagar_pedido_completo(self):
        """Preparar pago del pedido completo"""
        if not self.metodo_pago:
            self.mostrar_error("Seleccione un método de pago")
            return
        
        self.procesar_pago_final()
    
    def procesar_pago_final(self):
        """Procesar el pago final"""
        if not self.metodo_pago:
            self.mostrar_error("Seleccione un método de pago")
            return
        
        try:
            empleado_id = self.obtener_empleado_actual()
            
            # Registrar pago
            if self.caja_service.registrar_pago(
                self.pedido_id,
                empleado_id,
                self.total_con_descuento,
                self.metodo_pago
            ):
                # Cambiar estado
                self.pedido_service.cambiar_estado_pedido(self.pedido_id, 'pagado')
                
                # Mostrar éxito
                self.mostrar_exito(f"✅ Pago procesado\nPedido #{self.pedido_id}")
                
                # Recargar datos
                Clock.schedule_once(lambda dt: self.refrescar_datos(), 1)
            else:
                self.mostrar_error("Error al registrar pago")
            
        except Exception as e:
            print(f"❌ Error procesando pago: {e}")
            self.mostrar_error("Error al procesar pago")
    
    def refrescar_datos(self):
        """Refrescar todos los datos"""
        self.limpiar_seleccion()
        self.cargar_mesas_con_pedidos()
        if self.mesa_seleccionada:
            # Recargar mesa actual
            self.cargar_pedidos_mesa(f"Mesa {self.mesa_seleccionada}")
    
    def ver_tickets_generados(self):
        """Ver tickets generados (placeholder)"""
        self.mostrar_info("Función en desarrollo")
    
    def limpiar_seleccion(self):
        """Limpiar toda la selección"""
        self.pedido_id = 0
        self.pedido_data = {}
        self.items_pedido = []
        self.total_original = 0.0
        self.total_con_descuento = 0.0
        self.metodo_pago = ""
        
        if hasattr(self, 'ids'):
            if 'detalle_items' in self.ids:
                self.ids.detalle_items.clear_widgets()
    
    def volver_al_menu(self):
        """Volver al menú"""
        self.manager.current = "menu"
    
    def obtener_empleado_actual(self):
        """Obtener ID del empleado actual"""
        app = MDApp.get_running_app()
        return getattr(app, 'usuario_actual', {}).get('id', 1)
    
    def mostrar_error(self, mensaje):
        """Mostrar diálogo de error"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Error",
            text=mensaje,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=ds_color('error'),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def mostrar_info(self, mensaje):
        """Mostrar diálogo informativo"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            text=mensaje,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def mostrar_exito(self, mensaje):
        """Mostrar diálogo de éxito"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            text=mensaje,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=ds_color('success'),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()


# ========== WIDGETS PERSONALIZADOS ==========

class PedidoItemCompact(MDCard):
    """Widget compacto para item de pedido en lista"""
    pedido_id = NumericProperty(0)
    pedido_total = NumericProperty(0.0)
    pedido_estado = StringProperty("")
    num_items = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(68)
        self.padding = dp(8)
        self.spacing = dp(4)
        self.radius = dp(8)
        self.elevation = 1
        self.ripple_behavior = True
        self.md_bg_color = ds_color('white')


class ItemFilaTabla(MDBoxLayout):
    """Fila de item en tabla"""
    item_nombre = StringProperty("")
    item_cantidad = NumericProperty(1)
    item_precio = NumericProperty(0.0)
    item_subtotal = NumericProperty(0.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(44)
        self.padding = [dp(8), dp(6)]
        self.spacing = dp(4)