# views/pedidos/toma_pedidos_screen.py - VERSIÓN MEJORADA
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from themes.design_system import ds_color, ds_spacing, ds_font, ds_button_height

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

    def on_enter(self):
        """Carga optimizada con manejo de estado"""
        if not self._cargando:
            self._cargando = True
            Clock.schedule_once(self._inicializar_pantalla, 0.1)

    def _inicializar_pantalla(self, dt):
        """Inicialización asíncrona"""
        try:
            self.inicializar_servicios()
            self.cargar_categorias()
            self.cargar_categorias_ui()
            # Cargar primera categoría por defecto
            if self.categorias:
                self.categoria_activa = self.categorias[0]
                self.on_categoria_seleccionada(self.categoria_activa)
        finally:
            self._cargando = False

    def inicializar_servicios(self):
        """Inicialización lazy de servicios"""
        if not self.pedido_service or not self.producto_service:
            from services.database_service import PostgreSQLService
            from services.pedido_service import PedidoService
            from services.producto_service import ProductoService
            
            db = PostgreSQLService()
            self.pedido_service = PedidoService(db)
            self.producto_service = ProductoService(db)

    # MÉTODOS MEJORADOS PARA UI
    def cargar_categorias_ui(self):
        """Cargar categorías con diseño moderno"""
        if not hasattr(self, 'ids') or 'contenedor_categorias' not in self.ids:
            return
            
        self.ids.contenedor_categorias.clear_widgets()
        
        for categoria in self.categorias:
            from mis_widgets.category_chip import CategoryChip
            chip = CategoryChip(
                text=categoria.upper(),
                categoria=categoria,
                selected=(categoria == self.categoria_activa)
            )
            chip.bind(on_press=self._on_chip_pressed)
            self.ids.contenedor_categorias.add_widget(chip)

    def _on_chip_pressed(self, chip):
        """Manejo eficiente de selección de categorías"""
        self.categoria_activa = chip.categoria
        self.on_categoria_seleccionada(chip.categoria)
        
        # Actualizar estado visual de todos los chips
        for child in self.ids.contenedor_categorias.children:
            if hasattr(child, 'selected'):
                child.selected = (child.categoria == self.categoria_activa)

    def cargar_productos_ui(self):
        """Cargar productos con cards responsivas"""
        if not hasattr(self, 'ids') or 'grid_productos' not in self.ids:
            return
            
        self.ids.grid_productos.clear_widgets()
        
        for producto in self.productos:
            from mis_widgets.product_card import ProductCard
            card = ProductCard(
                nombre=producto['nombre'],
                precio=producto['precio'],
                product_id=producto['id'],
                size_hint=(None, None),
                size=("160dp", "120dp")
            )
            card.bind(on_press=lambda instance, prod=producto: self.mostrar_dialogo_producto(prod))
            self.ids.grid_productos.add_widget(card)

    # GESTIÓN MEJORADA DE PEDIDOS
    def agregar_producto_al_pedido(self, producto, cantidad=1, notas=""):
        """Agregar producto con validación y feedback"""
        try:
            if not self.pedido_service:
                self.mostrar_snackbar("Error: Servicio no disponible")
                return False
            
            success = self.pedido_service.agregar_item_temporal(
                producto, cantidad, notas
            )
            
            if success:
                self.actualizar_ui_pedido()
                self.mostrar_snackbar(f"✅ {producto['nombre']} agregado")
                return True
            else:
                self.mostrar_snackbar("❌ Error al agregar producto")
                return False
                
        except Exception as e:
            self.mostrar_snackbar(f"Error: {str(e)}")
            return False

    def actualizar_ui_pedido(self):
        """Actualización optimizada de la UI del pedido"""
        if not self.pedido_service:
            return
            
        self.total_pedido = self.pedido_service.pedido_temporal['total']
        
        # Actualizar total
        if hasattr(self, 'ids') and 'label_total' in self.ids:
            self.ids.label_total.text = f"${self.total_pedido:.2f}"
        
        # Actualizar items con widget personalizado
        self._actualizar_lista_items()

    def _actualizar_lista_items(self):
        """Actualizar lista de items con OrderItem personalizado"""
        if not hasattr(self, 'ids') or 'lista_items' not in self.ids:
            return
            
        self.ids.lista_items.clear_widgets()
        
        if not self.pedido_service.pedido_temporal['items']:
            from mis_widgets.responsive_widgets import EmptyStateWidget
            empty_widget = EmptyStateWidget(
                message="No hay productos en el pedido",
                icon="🛒"
            )
            self.ids.lista_items.add_widget(empty_widget)
        else:
            for item in self.pedido_service.pedido_temporal['items']:
                from mis_widgets.order_item import OrderItem
                order_item = OrderItem(
                    item_data=item,
                    pedido_screen=self,
                    size_hint_y=None,
                    height=ds_button_height('lg')
                )
                self.ids.lista_items.add_widget(order_item)

    # MÉTODOS DE NAVEGACIÓN MEJORADOS
    def solicitar_cierre_cuenta(self):
        """Navegación optimizada a cierre de cuenta"""
        try:
            if not self.pedido_service.pedido_temporal['items']:
                self.mostrar_snackbar("Agrega productos al pedido primero")
                return
            
            # Crear pedido y navegar
            empleado_id = self.obtener_empleado_actual()
            pedido_id = self.pedido_service.crear_pedido(
                self.mesa_actual, empleado_id, ""
            )
            
            if pedido_id:
                # Guardar items
                for item in self.pedido_service.pedido_temporal['items']:
                    self.pedido_service.agregar_item_pedido(
                        pedido_id, item['producto_id'], 
                        item['cantidad'], item['precio'], item.get('notas', '')
                    )
                
                self.pedido_service._actualizar_total_pedido(pedido_id)
                self.limpiar_pedido()
                self._navegar_a_cierre_cuenta(pedido_id)
            else:
                self.mostrar_snackbar("Error al crear pedido")
                
        except Exception as e:
            self.mostrar_snackbar(f"Error: {str(e)}")

    def _navegar_a_cierre_cuenta(self, pedido_id):
        """Navegación robusta a cierre de cuenta"""
        app = MDApp.get_running_app()
        
        # Configurar datos antes de navegar
        if 'cierre_cuenta' in app.root.ids.screen_manager.screen_names:
            cierre_screen = app.root.ids.screen_manager.get_screen('cierre_cuenta')
            cierre_screen.pedido_id = pedido_id
            cierre_screen.mesa_seleccionada = self.mesa_actual
            
        app.cambiar_pantalla('cierre_cuenta')

    # UTILIDADES MEJORADAS
    def mostrar_snackbar(self, mensaje):
        """Mostrar mensajes temporales modernos"""
        from kivymd.uix.snackbar import Snackbar
        Snackbar(
            text=mensaje,
            duration=2
        ).open()

    def obtener_empleado_actual(self):
        """Obtener empleado actual de forma segura"""
        app = MDApp.get_running_app()
        return getattr(app, 'usuario_actual', {}).get('id', 1)

    def limpiar_pedido(self):
        """Limpieza completa del pedido"""
        if self.pedido_service:
            self.pedido_service.limpiar_pedido_temporal()
            self.actualizar_ui_pedido()
            self.mesa_actual = "1"

    # MÉTODOS EXISTENTES MANTENIDOS PERO OPTIMIZADOS
    def on_categoria_seleccionada(self, categoria):
        if categoria and self.producto_service:
            self.productos = self.producto_service.obtener_productos_por_categoria(categoria)
            self.cargar_productos_ui()

    def confirmar_pedido(self):
        """Confirmar pedido con validaciones mejoradas"""
        if not self.pedido_service or not self.pedido_service.pedido_temporal['items']:
            self.mostrar_snackbar("Agrega productos al pedido primero")
            return
        
        # Lógica de confirmación existente pero optimizada
        super().confirmar_pedido()