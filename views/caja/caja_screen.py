# views/caja/caja_screen.py - VERSIÓN PROFESIONAL
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.properties import (BooleanProperty, StringProperty, NumericProperty, 
                            ListProperty, ObjectProperty)
from kivy.clock import Clock
from kivy.metrics import dp, sp
from datetime import datetime
from themes.design_system import ds_color, ds_spacing
from kivymd.app import MDApp

class CajaScreen(MDScreen):
    # Estado de caja
    caja_abierta = BooleanProperty(False)
    estado_caja = StringProperty("Verificando...")
    
    # Estadísticas
    total_ventas = NumericProperty(0.0)
    total_efectivo = NumericProperty(0.0)
    total_tarjeta = NumericProperty(0.0)
    total_transferencia = NumericProperty(0.0)
    
    # Pedidos
    pedidos_pendientes = ListProperty([])
    filtro_actual = StringProperty("todos")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.caja_service = None
        self.ticket_service = None
        self.dialog = None
        self.usuario_actual = None

    def on_enter(self):
        """Al entrar a la pantalla"""
        print("💰 Entrando a Módulo Caja")
        self.inicializar_servicios()
        self.verificar_estado_caja()
        self.cargar_pedidos_pendientes()

    def inicializar_servicios(self):
        """Inicializar servicios"""
        if not self.caja_service:
            try:
                from services.database_service import PostgreSQLService
                from services.caja_service import CajaService
                from services.ticket_service_caja import TicketServiceCaja
                from services.config_service import ConfigService
                
                app = MDApp.get_running_app()
                self.usuario_actual = app.usuario_actual
                
                db = PostgreSQLService()
                self.caja_service = CajaService(db)
                
                config_service = ConfigService(db)
                self.ticket_service = TicketServiceCaja(db, config_service)
                
                print("✅ Servicios de caja inicializados")
            except Exception as e:
                print(f"❌ Error inicializando servicios: {e}")

    def verificar_estado_caja(self):
        """Verificar estado de la caja"""
        if self.caja_service:
            self.caja_abierta = self.caja_service.verificar_caja_abierta()
            self.estado_caja = "ABIERTA ✅" if self.caja_abierta else "CERRADA 🔒"
            
            if self.caja_abierta:
                self.actualizar_estadisticas()

    def actualizar_estadisticas(self):
        """Actualizar estadísticas de ventas"""
        if self.caja_service:
            ventas = self.caja_service.obtener_ventas_dia()
            
            self.total_ventas = ventas['total_monto']
            self.total_efectivo = ventas['efectivo']
            self.total_tarjeta = ventas['tarjeta']
            self.total_transferencia = ventas['transferencia']
            
            print(f"📊 Estadísticas: Total ${self.total_ventas:.2f}")

    def cargar_pedidos_pendientes(self):
        """Cargar pedidos listos para pagar"""
        if self.caja_service and self.caja_abierta:
            self.pedidos_pendientes = self.caja_service.obtener_pedidos_pendientes_pago()
            print(f"📦 {len(self.pedidos_pendientes)} pedidos pendientes")
            self.actualizar_ui_pedidos()

    def filtrar_pedidos(self, filtro):
        """Filtrar pedidos"""
        self.filtro_actual = filtro
        self.actualizar_chips_filtro(filtro)
        # Aquí podrías filtrar realmente si tuvieras más estados

    def actualizar_chips_filtro(self, filtro_activo):
        """Actualizar chips de filtro"""
        if not hasattr(self, 'ids'):
            return
        
        chips = {
            'todos': 'chip_todos_pedidos',
            'listo': 'chip_listos'
        }
        
        for estado, chip_id in chips.items():
            if chip_id in self.ids:
                chip = self.ids[chip_id]
                if estado == filtro_activo:
                    chip.md_bg_color = ds_color('primary')
                    chip.text_color = ds_color('white')
                else:
                    chip.md_bg_color = ds_color('gray_light')
                    chip.text_color = ds_color('dark')

    def actualizar_ui_pedidos(self):
        """Actualizar UI con pedidos"""
        if not hasattr(self, 'ids') or 'contenedor_pedidos' not in self.ids:
            return
        
        self.ids.contenedor_pedidos.clear_widgets()
        
        # Actualizar contador
        if 'label_count_pedidos' in self.ids:
            self.ids.label_count_pedidos.text = f"{len(self.pedidos_pendientes)} pedidos"
        
        if not self.pedidos_pendientes:
            # Estado vacío
            self.ids.contenedor_pedidos.add_widget(CajaEmptyState())
            return
        
        # Crear cards
        for pedido in self.pedidos_pendientes:
            card = PedidoPagoCard(
                pedido_id=pedido['id'],
                mesa=pedido['mesa'],
                total=pedido['total'],
                num_items=len(pedido['items']),
                mesero=pedido['mesero'],
                tiempo=self._formato_tiempo(pedido['created_at']),
                caja_screen=self
            )
            self.ids.contenedor_pedidos.add_widget(card)

    def abrir_caja(self):
        """Abrir caja con fondo inicial"""
        if not self.usuario_actual:
            self.mostrar_error("No hay usuario logueado")
            return
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(150)
        )
        
        content.add_widget(MDLabel(
            text="FONDO INICIAL DE CAJA",
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        ))
        
        input_fondo = MDTextField(
            hint_text="Ej: 1000.00",
            mode="rectangle",
            input_filter="float",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_fondo)
        
        self.dialog = MDDialog(
            title="Abrir Caja",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ABRIR",
                    md_bg_color=ds_color('success'),
                    on_release=lambda x: self._confirmar_abrir(input_fondo.text)
                )
            ]
        )
        self.dialog.open()

    def _confirmar_abrir(self, fondo_str):
        """Confirmar apertura de caja"""
        try:
            fondo = float(fondo_str)
            if fondo <= 0:
                self.mostrar_error("El fondo debe ser mayor a 0")
                return
            
            if self.caja_service.abrir_caja(self.usuario_actual['id'], fondo):
                self.verificar_estado_caja()
                self.mostrar_info(f"✅ Caja abierta\nFondo: ${fondo:.2f}")
                self.dialog.dismiss()
            else:
                self.mostrar_error("Error abriendo caja")
        except ValueError:
            self.mostrar_error("Monto inválido")

    def procesar_pago(self, pedido_id, monto, metodo_pago):
        """Procesar pago de un pedido"""
        if not self.caja_abierta:
            self.mostrar_error("La caja debe estar abierta")
            return
        
        # Verificar permisos
        app = MDApp.get_running_app()
        if not app.auth_service.puede_cerrar_pedidos(app.usuario_actual):
            self.mostrar_error("No tienes permisos para procesar pagos")
            return
        
        if metodo_pago == 'efectivo':
            self.mostrar_popup_cambio(pedido_id, monto)
        else:
            if self._procesar_pago_directo(pedido_id, monto, metodo_pago):
                self.mostrar_info(f"✅ Pago procesado\n${monto:.2f} - {metodo_pago.upper()}")
                Clock.schedule_once(lambda dt: self.forzar_actualizacion(), 0.5)

    def mostrar_popup_cambio(self, pedido_id, monto):
        """Popup para calcular cambio"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(220)
        )
        
        content.add_widget(MDLabel(
            text=f"TOTAL: ${monto:.2f}",
            font_style="H5",
            bold=True,
            halign="center",
            theme_text_color="Custom",
            text_color=ds_color('success'),
            size_hint_y=None,
            height=dp(35)
        ))
        
        content.add_widget(MDLabel(
            text="MONTO RECIBIDO:",
            font_style="Subtitle1",
            halign="center",
            size_hint_y=None,
            height=dp(25)
        ))
        
        input_monto = MDTextField(
            hint_text=f"Ingrese monto...",
            mode="rectangle",
            input_filter="float",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_monto)
        
        label_cambio = MDLabel(
            text="Cambio: $0.00",
            font_style="H6",
            bold=True,
            halign="center",
            theme_text_color="Custom",
            text_color=ds_color('success'),
            size_hint_y=None,
            height=dp(35)
        )
        content.add_widget(label_cambio)
        
        self.dialog = MDDialog(
            title="Pago en Efectivo",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    id='btn_confirmar_cambio',
                    text="CONFIRMAR",
                    md_bg_color=ds_color('success'),
                    disabled=True,
                    on_release=lambda x: self._confirmar_pago_efectivo(pedido_id, monto, input_monto.text)
                )
            ]
        )
        
        def calcular_cambio(instance, value):
            try:
                recibido = float(value)
                cambio = recibido - monto
                
                if cambio < 0:
                    label_cambio.text = f"FALTAN: ${abs(cambio):.2f}"
                    label_cambio.text_color = ds_color('error')
                    self.dialog.buttons[1].disabled = True
                else:
                    label_cambio.text = f"Cambio: ${cambio:.2f}"
                    label_cambio.text_color = ds_color('success')
                    self.dialog.buttons[1].disabled = False
            except ValueError:
                label_cambio.text = "Monto inválido"
                label_cambio.text_color = ds_color('error')
                self.dialog.buttons[1].disabled = True
        
        input_monto.bind(text=calcular_cambio)
        self.dialog.open()

    def _confirmar_pago_efectivo(self, pedido_id, monto, recibido_str):
        """Confirmar pago en efectivo"""
        try:
            recibido = float(recibido_str)
            cambio = recibido - monto
            
            if cambio < 0:
                self.mostrar_error("Monto insuficiente")
                return
            
            if self._procesar_pago_directo(pedido_id, monto, 'efectivo'):
                mensaje = f"✅ Pago en EFECTIVO\n"
                mensaje += f"Total: ${monto:.2f}\n"
                mensaje += f"Recibido: ${recibido:.2f}\n"
                mensaje += f"Cambio: ${cambio:.2f}"
                
                self.mostrar_info(mensaje)
                self.dialog.dismiss()
                Clock.schedule_once(lambda dt: self.forzar_actualizacion(), 0.5)
            else:
                self.mostrar_error("Error procesando pago")
        except ValueError:
            self.mostrar_error("Monto inválido")

    def _procesar_pago_directo(self, pedido_id, monto, metodo_pago):
        """Procesar pago directamente"""
        if self.caja_service:
            return self.caja_service.registrar_pago(
                pedido_id,
                self.usuario_actual['id'],
                monto,
                metodo_pago
            )
        return False

    def cerrar_caja(self):
        """Cerrar caja con reporte"""
        if not self.caja_abierta:
            self.mostrar_error("La caja ya está cerrada")
            return
        
        # Generar reporte primero
        reporte = self.caja_service.generar_reporte_cierre(self.usuario_actual['id'])
        
        if 'error' in reporte:
            self.mostrar_error(f"Error: {reporte['error']}")
            return
        
        self.mostrar_reporte_cierre(reporte)

    def mostrar_reporte_cierre(self, reporte):
        """Mostrar reporte de cierre"""
        from kivy.uix.scrollview import ScrollView
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(400)
        )
        
        # Título
        content.add_widget(MDLabel(
            text="📊 REPORTE DE CIERRE",
            font_style="H5",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        ))
        
        # Scroll con datos
        scroll = ScrollView(size_hint_y=None, height=dp(250))
        info_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=self.minimum_height,
            spacing=dp(8),
            padding=dp(10)
        )
        
        datos = [
            ("Empleado:", reporte['empleado']),
            ("Fondo Inicial:", f"${reporte['fondo_inicial']:.2f}"),
            ("Total Ventas:", f"${reporte['total_ventas']:.2f}"),
            ("Efectivo:", f"${reporte['total_efectivo']:.2f}"),
            ("Tarjeta:", f"${reporte['total_tarjeta']:.2f}"),
            ("Transferencia:", f"${reporte['total_transferencia']:.2f}"),
            ("TOTAL CIERRE:", f"${reporte['total_cierre']:.2f}")
        ]
        
        for label, valor in datos:
            row = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
            row.add_widget(MDLabel(text=label, bold=True, size_hint_x=0.6))
            row.add_widget(MDLabel(text=valor, halign="right", size_hint_x=0.4))
            info_box.add_widget(row)
        
        scroll.add_widget(info_box)
        content.add_widget(scroll)
        
        # Observaciones
        input_obs = MDTextField(
            hint_text="Observaciones (opcional)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(60)
        )
        content.add_widget(input_obs)
        
        self.dialog = MDDialog(
            title="Cierre de Caja",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="CONFIRMAR CIERRE",
                    md_bg_color=ds_color('error'),
                    on_release=lambda x: self._confirmar_cierre(input_obs.text)
                )
            ]
        )
        self.dialog.open()

    def _confirmar_cierre(self, observaciones):
        """Confirmar cierre de caja"""
        if self.caja_service.cerrar_caja(self.usuario_actual['id'], observaciones):
            self.verificar_estado_caja()
            self.mostrar_info("✅ Caja cerrada exitosamente")
            self.dialog.dismiss()
        else:
            self.mostrar_error("Error cerrando caja")

    def realizar_arqueo(self):
        """Realizar arqueo de caja"""
        if not self.caja_abierta:
            self.mostrar_error("La caja debe estar abierta")
            return
        
        teorico_data = self.caja_service.calcular_efectivo_teorico()
        
        if 'error' in teorico_data:
            self.mostrar_error("Error calculando efectivo teórico")
            return
        
        # Aquí mostrarías un diálogo similar al de cierre pero para arqueo
        self.mostrar_info(f"Efectivo teórico: ${teorico_data['efectivo_teorico']:.2f}")

    def ver_historial_cierres(self):
        """Ver historial de cierres"""
        historial = self.caja_service.obtener_historial_cierres(7)
        
        if not historial:
            self.mostrar_info("No hay historial disponible")
            return
        
        # Aquí mostrarías el historial en un diálogo con scroll
        mensaje = "📅 ÚLTIMOS CIERRES:\n\n"
        for cierre in historial[:5]:
            mensaje += f"• {cierre['fecha']}: ${cierre['total_cierre']:.2f}\n"
        
        self.mostrar_info(mensaje)

    def forzar_actualizacion(self):
        """Forzar actualización manual"""
        print("🔄 Actualizando datos...")
        self.verificar_estado_caja()
        self.cargar_pedidos_pendientes()

    def _formato_tiempo(self, created_at):
        """Formatear tiempo transcurrido"""
        try:
            if isinstance(created_at, str):
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            
            ahora = datetime.now()
            diferencia = ahora - created_at
            minutos = int(diferencia.total_seconds() / 60)
            
            if minutos < 60:
                return f"{minutos} min"
            else:
                horas = minutos // 60
                return f"{horas}h {minutos % 60}min"
        except:
            return "N/A"

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


# ========== WIDGETS PERSONALIZADOS ==========

class EstadisticaCard(MDCard):
    """Card de estadística"""
    titulo = StringProperty("")
    valor = StringProperty("")
    icono = StringProperty("")
    color_fondo = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(8)
        self.spacing = dp(4)
        self.elevation = 0
        self.radius = dp(8)


class PedidoPagoCard(MDCard):
    """Card de pedido para pago"""
    pedido_id = NumericProperty(0)
    mesa = StringProperty("")
    total = NumericProperty(0.0)
    num_items = NumericProperty(0)
    mesero = StringProperty("")
    tiempo = StringProperty("")
    caja_screen = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = 0
        self.spacing = 0
        self.elevation = 2
        self.radius = dp(12)
        self.md_bg_color = ds_color('white')
    
    def pagar_efectivo(self):
        if self.caja_screen:
            self.caja_screen.procesar_pago(self.pedido_id, self.total, 'efectivo')
    
    def pagar_tarjeta(self):
        if self.caja_screen:
            self.caja_screen.procesar_pago(self.pedido_id, self.total, 'tarjeta')
    
    def pagar_transferencia(self):
        if self.caja_screen:
            self.caja_screen.procesar_pago(self.pedido_id, self.total, 'transferencia')
    
    def ver_detalle(self):
        if self.caja_screen:
            self.caja_screen.mostrar_info(f"Detalle del pedido #{self.pedido_id}\nFunción en desarrollo")


class CajaEmptyState(MDBoxLayout):
    """Estado vacío"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(40)
        self.spacing = dp(20)