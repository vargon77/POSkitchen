# views/cocina/cocina_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton
from kivy.properties import (ListProperty, NumericProperty, StringProperty, 
                            ObjectProperty, DictProperty)
from kivy.clock import Clock
from kivy.metrics import dp, sp
from datetime import datetime
from themes.design_system import ds_color, ds_spacing, ds_is_mobile
from kivymd.app import MDApp

class CocinaScreen(MDScreen):
    pedidos = ListProperty([])
    pedidos_filtrados = ListProperty([])
    total_pedidos = NumericProperty(0)
    filtro_actual = StringProperty("todos")
    estadisticas = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cocina_service = None
        self.actualizar_event = None
        self.dialog = None
    
    def on_enter(self):
        """Cuando se muestra la pantalla"""
        print("👨‍🍳 Entrando a Vista Cocina")
        self.inicializar_servicios()
        self.cargar_pedidos()
        
        # Actualizar automáticamente cada 15 segundos
        if self.actualizar_event:
            self.actualizar_event.cancel()
        self.actualizar_event = Clock.schedule_interval(
            lambda dt: self.cargar_pedidos(), 15
        )
    
    def on_leave(self):
        """Cuando se sale de la pantalla"""
        if self.actualizar_event:
            self.actualizar_event.cancel()
            print("⏹️ Actualización automática detenida")

    # ========== MÉTODOS PARA TOPAPPBAR ==========
    def ir_a_menu(self, *args):
        """Volver al menú principal"""
        app = MDApp.get_running_app()
        if hasattr(app, 'cambiar_pantalla'):
            app.cambiar_pantalla("menu")
        else:
            self.manager.current = "menu"
    # ========== FIN MÉTODOS TOPAPPBAR ==========
    
    def inicializar_servicios(self):
        """Inicializar servicios de cocina"""
        if not self.cocina_service:
            try:
                from services.database_service import PostgreSQLService
                from services.cocina_service import CocinaService
                
                db = PostgreSQLService()
                self.cocina_service = CocinaService(db)
                print("✅ Servicios de cocina inicializados")
            except Exception as e:
                print(f"❌ Error inicializando servicios: {e}")
    
    def cargar_pedidos(self, *args):
        """Cargar pedidos activos para cocina"""
        if not self.cocina_service:
            print("❌ No hay servicio de cocina")
            return
        
        try:
            print("🔄 Cargando pedidos para cocina...")
            
            self.pedidos = self.cocina_service.obtener_pedidos_activos()
            self.total_pedidos = len(self.pedidos)
            
            self.calcular_estadisticas()
            self.filtrar_pedidos(self.filtro_actual)
            
            print(f"✅ {len(self.pedidos)} pedidos cargados")
            
        except Exception as e:
            print(f"❌ Error cargando pedidos: {e}")
            self.mostrar_error("Error al cargar pedidos")
    
    def calcular_estadisticas(self):
        """Calcular estadísticas de pedidos"""
        stats = {
            'pendiente': 0,
            'preparacion': 0,
            'listo': 0,
            'tiempo_promedio': 0
        }
        
        tiempos = []
        
        for pedido in self.pedidos:
            estado = pedido.get('estado', 'pendiente')
            if estado in stats:
                stats[estado] += 1
            
            created_at = pedido.get('created_at')
            if created_at:
                tiempo_min = self._calcular_minutos_espera(created_at)
                tiempos.append(tiempo_min)
        
        if tiempos:
            stats['tiempo_promedio'] = sum(tiempos) // len(tiempos)
        
        self.estadisticas = stats
        self.actualizar_estadisticas_ui()
    
    def actualizar_estadisticas_ui(self):
        """Actualizar UI de estadísticas"""
        if not hasattr(self, 'ids'):
            return
        
        if 'label_pendientes' in self.ids:
            self.ids.label_pendientes.text = str(self.estadisticas.get('pendiente', 0))
        
        if 'label_preparando' in self.ids:
            self.ids.label_preparando.text = str(self.estadisticas.get('preparacion', 0))
        
        if 'label_listos' in self.ids:
            self.ids.label_listos.text = str(self.estadisticas.get('listo', 0))
        
        if 'label_tiempo_prom' in self.ids:
            tiempo = self.estadisticas.get('tiempo_promedio', 0)
            self.ids.label_tiempo_prom.text = f"{tiempo} min"
    
    def filtrar_pedidos(self, filtro):
        """Filtrar pedidos por estado"""
        self.filtro_actual = filtro
        
        if filtro == 'todos':
            self.pedidos_filtrados = self.pedidos.copy()
        else:
            self.pedidos_filtrados = [
                p for p in self.pedidos 
                if p.get('estado') == filtro
            ]
        
        self.actualizar_chips_filtro(filtro)
        self.actualizar_grid_pedidos()
        
        print(f"🔍 Filtro: {filtro} - {len(self.pedidos_filtrados)} pedidos")
    
    def actualizar_chips_filtro(self, filtro_activo):
        """Actualizar estado visual de chips de filtro"""
        if not hasattr(self, 'ids'):
            return
        
        chips = {
            'todos': 'chip_todos',
            'pendiente': 'chip_pendientes',
            'preparacion': 'chip_preparacion',
            'listo': 'chip_listos_filtro'
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
    
    def actualizar_grid_pedidos(self):
        """Actualizar grid con cards de pedidos"""
        if not hasattr(self, 'ids') or 'grid_pedidos' not in self.ids:
            return
        
        self.ids.grid_pedidos.clear_widgets()
        
        if not self.pedidos_filtrados:
            empty_state = CocinaEmptyState()
            self.ids.grid_pedidos.add_widget(empty_state)
            return
        
        for pedido in self.pedidos_filtrados:
            card = PedidoCocinaCard(
                pedido_id=pedido['id'],
                mesa=pedido['mesa'],
                estado=pedido['estado'],
                tiempo_espera=self._formato_tiempo_espera(pedido['created_at']),
                items_text=self._formato_items(pedido['items']),
                mesero=pedido['mesero'],
                cocina_screen=self
            )
            self.ids.grid_pedidos.add_widget(card)
    
    def cambiar_estado_pedido(self, pedido_id, nuevo_estado):
        """Cambiar estado de un pedido"""
        print(f"🔄 Cambiando pedido {pedido_id} a {nuevo_estado}")
        
        if self.cocina_service and self.cocina_service.cambiar_estado_pedido(pedido_id, nuevo_estado):
            Clock.schedule_once(lambda dt: self.cargar_pedidos(), 0.5)
            self.mostrar_info(f"✅ Pedido {pedido_id} → {nuevo_estado.upper()}")
        else:
            self.mostrar_error("Error cambiando estado")
    
    def ver_detalle_pedido(self, pedido_id):
        """Ver detalle completo de un pedido"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        
        if not pedido:
            return
        
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(300)
        )
        
        content.add_widget(MDLabel(
            text=f"PEDIDO #{pedido['id']} - Mesa {pedido['mesa']}",
            font_style="H6",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(30)
        ))
        
        content.add_widget(MDLabel(
            text=f"⏱️ {self._formato_tiempo_espera(pedido['created_at'])}",
            font_style="Subtitle1",
            halign="center",
            size_hint_y=None,
            height=dp(25)
        ))
        
        scroll = ScrollView(size_hint_y=None, height=dp(150))
        items_box = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8),
            padding=dp(10)
        )
        items_box.bind(minimum_height=items_box.setter('height'))
        
        for item in pedido['items']:
            item_text = f"• {item['nombre']} x{item['cantidad']}"
            if item.get('notas'):
                item_text += f"\n  📝 {item['notas']}"
            
            items_box.add_widget(MDLabel(
                text=item_text,
                font_style="Body2",
                size_hint_y=None,
                height=dp(40) if item.get('notas') else dp(25)
            ))
        
        scroll.add_widget(items_box)
        content.add_widget(scroll)
        
        content.add_widget(MDLabel(
            text=f"Mesero: {pedido['mesero']}",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(20)
        ))
        
        self.dialog = MDDialog(
            title="Detalle del Pedido",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="CERRAR",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def ver_alertas(self, *args):
        """Ver pedidos con tiempo excedido"""
        pedidos_urgentes = [
            p for p in self.pedidos 
            if self._calcular_minutos_espera(p['created_at']) > 15
        ]
        
        if not pedidos_urgentes:
            self.mostrar_info("✅ No hay pedidos urgentes")
            return
        
        mensaje = f"⚠️ {len(pedidos_urgentes)} pedido(s) con más de 15 minutos:\n\n"
        for p in pedidos_urgentes[:5]:
            tiempo = self._calcular_minutos_espera(p['created_at'])
            mensaje += f"• Pedido #{p['id']} - Mesa {p['mesa']}: {tiempo} min\n"
        
        self.mostrar_info(mensaje)
    
    def _calcular_minutos_espera(self, created_at):
        """Calcular minutos desde creación"""
        try:
            if isinstance(created_at, str):
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            
            ahora = datetime.now()
            diferencia = ahora - created_at
            return int(diferencia.total_seconds() / 60)
        except:
            return 0
    
    def _formato_tiempo_espera(self, created_at):
        """Formatear tiempo de espera"""
        minutos = self._calcular_minutos_espera(created_at)
        
        if minutos < 1:
            return "Recién llegado"
        elif minutos < 5:
            return f"{minutos} min"
        elif minutos < 10:
            return f"{minutos} min ⚠️"
        else:
            return f"{minutos} min 🔴"
    
    def _formato_items(self, items):
        """Formatear lista de items para mostrar"""
        if not items:
            return "Sin items"
        
        texto = ""
        for item in items:
            texto += f"• {item['nombre']} x{item['cantidad']}\n"
            if item.get('notas'):
                texto += f"  📝 {item['notas']}\n"
        
        return texto.strip()
    
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

class PedidoCocinaCard(MDCard):
    """Card profesional para pedido en cocina"""
    pedido_id = NumericProperty(0)
    mesa = StringProperty("")
    estado = StringProperty("pendiente")
    tiempo_espera = StringProperty("")
    items_text = StringProperty("")
    mesero = StringProperty("")
    cocina_screen = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(280)
        self.padding = 0
        self.spacing = 0
        self.elevation = 3
        self.radius = dp(12)
        self.md_bg_color = ds_color('white')
    
    @property
    def color_estado(self):
        """Color según estado del pedido"""
        colores = {
            'pendiente': ds_color('warning'),
            'confirmado': ds_color('warning'),
            'preparacion': ds_color('info'),
            'listo': ds_color('success')
        }
        return colores.get(self.estado, ds_color('gray'))
    
    @property
    def color_estado_light(self):
        """Color claro para fondo"""
        colores = {
            'pendiente': (*ds_color('warning')[:3], 0.1),
            'confirmado': (*ds_color('warning')[:3], 0.1),
            'preparacion': (*ds_color('info')[:3], 0.1),
            'listo': (*ds_color('success')[:3], 0.1)
        }
        return colores.get(self.estado, (*ds_color('gray')[:3], 0.1))
    
    @property
    def color_tiempo(self):
        """Color según tiempo de espera"""
        if "🔴" in self.tiempo_espera:
            return ds_color('error')
        elif "⚠️" in self.tiempo_espera:
            return ds_color('warning')
        else:
            return ds_color('success')
    
    @property
    def texto_boton_principal(self):
        """Texto del botón según estado"""
        textos = {
            'pendiente': 'INICIAR',
            'confirmado': 'INICIAR',
            'preparacion': 'MARCAR LISTO',
            'listo': 'ENTREGADO'
        }
        return textos.get(self.estado, 'ACCIÓN')
    
    @property
    def icono_boton_principal(self):
        """Ícono del botón según estado"""
        iconos = {
            'pendiente': 'play',
            'confirmado': 'play',
            'preparacion': 'check',
            'listo': 'check-all'
        }
        return iconos.get(self.estado, 'check')
    
    @property
    def color_boton_principal(self):
        """Color del botón según estado"""
        colores = {
            'pendiente': ds_color('warning'),
            'confirmado': ds_color('warning'),
            'preparacion': ds_color('success'),
            'listo': ds_color('info')
        }
        return colores.get(self.estado, ds_color('primary'))
    
    def accion_principal(self):
        """Ejecutar acción principal según estado"""
        estados_sig = {
            'pendiente': 'preparacion',
            'confirmado': 'preparacion',
            'preparacion': 'listo',
            'listo': 'entregado'
        }
        
        nuevo_estado = estados_sig.get(self.estado)
        if nuevo_estado and self.cocina_screen:
            self.cocina_screen.cambiar_estado_pedido(self.pedido_id, nuevo_estado)
    
    def ver_detalle(self):
        """Ver detalle del pedido"""
        if self.cocina_screen:
            self.cocina_screen.ver_detalle_pedido(self.pedido_id)


class CocinaEmptyState(MDBoxLayout):
    """Estado vacío para cocina"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(40)
        self.spacing = dp(20)