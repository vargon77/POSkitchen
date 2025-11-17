# views/pedidos/toma_pedidos_screen.py - VERSIÓN PROFESIONAL
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.properties import BooleanProperty, ObjectProperty, DictProperty
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivymd.app import MDApp
from themes.design_system import ds_color, ds_spacing, ds_font, ds_button_height
from kivy.graphics import Color, RoundedRectangle

class TomaPedidoScreen(MDScreen):
    mesa_actual = StringProperty("1")
    categorias = ListProperty([])
    productos = ListProperty([])
    total_pedido = NumericProperty(0.0)
    categoria_activa = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pedido_service = None
        self.producto_service = None
        self._cargando = False
        self.dialog = None

    def on_enter(self):
        """Carga optimizada"""
        if not self._cargando:
            self._cargando = True
            Clock.schedule_once(self._inicializar_pantalla, 0.1)

    def _inicializar_pantalla(self, dt):
        """Inicialización asíncrona"""
        try:
            self.inicializar_servicios()
            self.cargar_categorias()
            self.cargar_categorias_ui()
            
            if self.categorias:
                self.categoria_activa = self.categorias[0]
                self.on_categoria_seleccionada(self.categoria_activa)
            
            print(f"✅ Pantalla de pedidos inicializada - Mesa {self.mesa_actual}")
        except Exception as e:
            print(f"❌ Error inicializando: {e}")
            self.mostrar_dialogo_error("Error al cargar datos")
        finally:
            self._cargando = False

    def inicializar_servicios(self):
        """Inicialización de servicios"""
        if not self.pedido_service or not self.producto_service:
            from services.database_service import PostgreSQLService
            from services.pedido_service import PedidoService
            from services.producto_service import ProductoService
            
            db = PostgreSQLService()
            self.pedido_service = PedidoService(db)
            self.producto_service = ProductoService(db)
            print("✅ Servicios inicializados")

    def cargar_categorias(self):
        """Cargar categorías desde BD"""
        if self.producto_service:
            self.categorias = self.producto_service.obtener_categorias()
            print(f"📂 {len(self.categorias)} categorías cargadas")

    def cargar_categorias_ui(self):
        """Cargar categorías con chips profesionales"""
        if not hasattr(self, 'ids') or 'contenedor_categorias' not in self.ids:
            return
            
        self.ids.contenedor_categorias.clear_widgets()
        
        for categoria in self.categorias:
            chip = CategoryChipPro(
                text=categoria.upper(),
                categoria=categoria,
                selected=(categoria == self.categoria_activa)
            )
            chip.bind(on_press=self._on_chip_pressed)
            self.ids.contenedor_categorias.add_widget(chip)

    def _on_chip_pressed(self, chip):
        """Manejo de selección de categorías"""
        self.categoria_activa = chip.categoria
        self.on_categoria_seleccionada(chip.categoria)
        
        # Actualizar visual de chips
        for child in self.ids.contenedor_categorias.children:
            if hasattr(child, 'selected'):
                child.selected = (child.categoria == self.categoria_activa)

    def on_categoria_seleccionada(self, categoria):
        """Cargar productos de la categoría"""
        if categoria and self.producto_service:
            self.productos = self.producto_service.obtener_productos_por_categoria(categoria)
            print(f"🍽️ {len(self.productos)} productos en {categoria}")
            self.cargar_productos_ui()

    def cargar_productos_ui(self):
        """Cargar productos con cards profesionales"""
        if not hasattr(self, 'ids') or 'grid_productos' not in self.ids:
            return
            
        self.ids.grid_productos.clear_widgets()
        
        if not self.productos:
            self.ids.grid_productos.add_widget(MDLabel(
                text="No hay productos\nen esta categoría",
                halign="center",
                theme_text_color="Secondary",
                italic=True
            ))
            return
        
        for producto in self.productos:
            card = ProductCardPro(
                producto_nombre=producto['nombre'],
                producto_precio=float(producto['precio']),
                producto_id=producto['id']
            )
            card.bind(on_press=lambda instance, prod=producto: self.mostrar_dialogo_producto(prod))
            self.ids.grid_productos.add_widget(card)

    def mostrar_dialogo_producto(self, producto):
        """Diálogo mejorado para agregar producto"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(220)
        )
        
        # Nombre y precio
        content.add_widget(MDLabel(
            text=producto['nombre'],
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        ))
        
        content.add_widget(MDLabel(
            text=f"${float(producto['precio']):.2f}",
            font_style="H5",
            halign="center",
            theme_text_color="Custom",
            text_color=ds_color('success'),
            size_hint_y=None,
            height=dp(35)
        ))
        
        # Cantidad con controles
        cantidad_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        cantidad_layout.add_widget(MDLabel(text="Cantidad:", size_hint_x=0.4))
        
        input_cantidad = MDTextField(
            text="1",
            mode="rectangle",
            input_filter="int",
            size_hint_x=0.6,
            size_hint_y=None,
            height=dp(48)
        )
        cantidad_layout.add_widget(input_cantidad)
        content.add_widget(cantidad_layout)
        
        # Notas
        input_notas = MDTextField(
            hint_text="Notas especiales (opcional)",
            mode="rectangle",
            multiline=False,
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_notas)
        
        self.dialog = MDDialog(
            title="Agregar Producto",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="AGREGAR",
                    md_bg_color=ds_color('success'),
                    on_release=lambda x: self._agregar_desde_dialogo(
                        producto, input_cantidad.text, input_notas.text
                    )
                )
            ]
        )
        self.dialog.open()

    def _agregar_desde_dialogo(self, producto, cantidad_str, notas):
        """Agregar producto desde el diálogo"""
        try:
            cantidad = int(cantidad_str) if cantidad_str else 1
            if cantidad < 1:
                cantidad = 1
            
            if cantidad > 99:
                self.mostrar_dialogo_info("La cantidad máxima es 99")
                return
            
            self.agregar_producto_al_pedido(producto, cantidad, notas)
            self.dialog.dismiss()
        except ValueError:
            self.mostrar_dialogo_info("Cantidad inválida")

    def agregar_producto_al_pedido(self, producto, cantidad=1, notas=""):
        """Agregar producto al pedido temporal"""
        try:
            if not self.pedido_service:
                self.mostrar_dialogo_error("Servicio no disponible")
                return False
            
            self.pedido_service.agregar_item_temporal(producto, cantidad, notas)
            self.actualizar_ui_pedido()
            self.mostrar_dialogo_info(f"✅ {producto['nombre']} x{cantidad}")
            return True
                
        except Exception as e:
            print(f"❌ Error agregando producto: {e}")
            self.mostrar_dialogo_error("Error al agregar producto")
            return False

    def actualizar_ui_pedido(self):
        """Actualizar UI del resumen de pedido"""
        if not self.pedido_service:
            return
            
        self.total_pedido = self.pedido_service.pedido_temporal['total']
        
        # Actualizar contador de items
        if hasattr(self, 'ids') and 'label_items_count' in self.ids:
            count = len(self.pedido_service.pedido_temporal['items'])
            self.ids.label_items_count.text = f"{count} item{'s' if count != 1 else ''}"
        
        # Actualizar lista de items
        self._actualizar_lista_items()

    def _actualizar_lista_items(self):
        """Actualizar lista de items del pedido"""
        if not hasattr(self, 'ids') or 'lista_items' not in self.ids:
            return
            
        self.ids.lista_items.clear_widgets()
        
        if not self.pedido_service.pedido_temporal['items']:
            # Estado vacío
            empty_box = MDBoxLayout(
                orientation='vertical',
                padding=dp(20),
                spacing=dp(10)
            )
            empty_box.add_widget(MDLabel(
                text="🛒",
                font_size=sp(48),
                halign="center",
                size_hint_y=None,
                height=dp(60)
            ))
            empty_box.add_widget(MDLabel(
                text="Sin productos",
                font_style="Subtitle1",
                halign="center",
                theme_text_color="Secondary"
            ))
            self.ids.lista_items.add_widget(empty_box)
        else:
            for item in self.pedido_service.pedido_temporal['items']:
                order_item = OrderItemPro(
                    item_nombre=item['nombre'],
                    item_cantidad=item['cantidad'],
                    item_precio=item['precio'],
                    item_subtotal=item['subtotal'],
                    item_data=item,
                    pedido_screen=self
                )
                self.ids.lista_items.add_widget(order_item)

    def incrementar_item(self, item_data):
        """Incrementar cantidad de un item"""
        if item_data in self.pedido_service.pedido_temporal['items']:
            item_data['cantidad'] += 1
            item_data['subtotal'] = item_data['cantidad'] * item_data['precio']
            self.pedido_service._calcular_total_temporal()
            self.actualizar_ui_pedido()

    def decrementar_item(self, item_data):
        """Decrementar cantidad de un item"""
        if item_data in self.pedido_service.pedido_temporal['items']:
            if item_data['cantidad'] > 1:
                item_data['cantidad'] -= 1
                item_data['subtotal'] = item_data['cantidad'] * item_data['precio']
                self.pedido_service._calcular_total_temporal()
                self.actualizar_ui_pedido()
            else:
                self.eliminar_item_pedido(item_data)

    def eliminar_item_pedido(self, item_data):
        """Eliminar item del pedido"""
        if self.pedido_service:
            items = self.pedido_service.pedido_temporal['items']
            if item_data in items:
                items.remove(item_data)
                self.pedido_service._calcular_total_temporal()
                self.actualizar_ui_pedido()

    def cambiar_mesa(self):
        """Diálogo para cambiar mesa"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None,
            height=dp(120)
        )
        
        input_mesa = MDTextField(
            hint_text="Número de mesa",
            text=self.mesa_actual,
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_mesa)
        
        self.dialog = MDDialog(
            title="Cambiar Mesa",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="CAMBIAR",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: self._cambiar_mesa_confirm(input_mesa.text)
                )
            ]
        )
        self.dialog.open()

    def _cambiar_mesa_confirm(self, nueva_mesa):
        """Confirmar cambio de mesa"""
        if nueva_mesa and nueva_mesa.strip():
            self.mesa_actual = nueva_mesa.strip()
            print(f"🔄 Mesa cambiada a: {self.mesa_actual}")
            self.dialog.dismiss()

    def confirmar_pedido(self):
        """Confirmar y guardar pedido"""
        if not self.pedido_service or not self.pedido_service.pedido_temporal['items']:
            self.mostrar_dialogo_info("Agrega productos al pedido")
            return
        
        try:
            empleado_id = self.obtener_empleado_actual()
            
            # Crear pedido
            pedido_id = self.pedido_service.crear_pedido(
                self.mesa_actual, 
                empleado_id, 
                ""
            )
            
            if not pedido_id:
                self.mostrar_dialogo_error("Error al crear pedido")
                return
            
            # Agregar items
            for item in self.pedido_service.pedido_temporal['items']:
                self.pedido_service.agregar_item_pedido(
                    pedido_id,
                    item['producto_id'],
                    item['cantidad'],
                    item['precio'],
                    item.get('notas', '')
                )
            
            # Actualizar total
            self.pedido_service._actualizar_total_pedido(pedido_id)
            
            # Limpiar y confirmar
            self.limpiar_pedido()
            self.mostrar_dialogo_info(f"✅ Pedido #{pedido_id} creado\nMesa {self.mesa_actual}")
            
            print(f"✅ Pedido #{pedido_id} confirmado - Mesa {self.mesa_actual}")
            
        except Exception as e:
            print(f"❌ Error confirmando pedido: {e}")
            self.mostrar_dialogo_error("Error al confirmar")

    def limpiar_pedido(self):
        """Limpiar pedido temporal"""
        if self.pedido_service:
            self.pedido_service.limpiar_pedido_temporal()
            self.actualizar_ui_pedido()

    def mostrar_dialogo_info(self, mensaje):
        """Diálogo informativo simple"""
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

    def mostrar_dialogo_error(self, mensaje):
        """Diálogo de error"""
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

    def obtener_empleado_actual(self):
        """Obtener empleado actual"""
        app = MDApp.get_running_app()
        return getattr(app, 'usuario_actual', {}).get('id', 1)


# ========== WIDGETS PERSONALIZADOS ==========

class CategoryChipPro(MDChip):
    """Chip de categoría profesional"""
    categoria = StringProperty("")
    selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.height = dp(36)
        self.radius = dp(18)
        self.bind(selected=self._update_colors)
        self._update_colors()
    
    def _update_colors(self, *args):
        if self.selected:
            self.md_bg_color = ds_color('primary')
            self.text_color = ds_color('white')
        else:
            self.md_bg_color = ds_color('gray_light')
            self.text_color = ds_color('dark')
    
    def on_size(self, *args):
        self.width = max(self.texture_size[0] + dp(32), dp(80))


class ProductCardPro(MDCard):
    """Card de producto profesional"""
    producto_nombre = StringProperty("")
    producto_precio = NumericProperty(0.0)
    producto_id = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (dp(140), dp(160))
        self.padding = dp(8)
        self.spacing = dp(4)
        self.elevation = 2
        self.radius = dp(12)
        self.ripple_behavior = True
        self.md_bg_color = ds_color('white')


class OrderItemPro(MDCard):
    """Item de pedido profesional"""
    item_nombre = StringProperty("")
    item_cantidad = NumericProperty(1)
    item_precio = NumericProperty(0.0)
    item_subtotal = NumericProperty(0.0)
    item_data = DictProperty({})
    pedido_screen = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = dp(8)
        self.spacing = dp(8)
        self.elevation = 1
        self.radius = dp(8)
        self.md_bg_color = ds_color('white')