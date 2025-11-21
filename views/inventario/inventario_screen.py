# views/inventario/inventario_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.spinner import Spinner
from kivy.properties import ListProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.properties import ObjectProperty, DictProperty
from kivy.metrics import dp, sp
from themes.design_system import ds_color, ds_spacing, ds_is_mobile
import psycopg2

class InventarioScreen(MDScreen):
    productos = ListProperty([])
    categorias = ListProperty([])
    categoria_filtro = StringProperty("Todos")
    busqueda_texto = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_service = None
        self.dialog = None
    
    def on_enter(self):
        """Al entrar a la pantalla"""
        print("📦 Entrando a Módulo de Inventario")
        self.inicializar_servicios()
        self.cargar_categorias()
        self.cargar_productos()
    
    def inicializar_servicios(self):
        """Inicializar servicios"""
        if not self.db_service:
            try:
                from services.database_service import PostgreSQLService
                self.db_service = PostgreSQLService()
                print("✅ Servicio de BD inicializado")
            except Exception as e:
                print(f"❌ Error inicializando BD: {e}")
    
    def cargar_categorias(self):
        """Cargar categorías disponibles"""
        try:
            conn = psycopg2.connect(**self.db_service.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT DISTINCT categoria 
                FROM productos 
                WHERE activo = TRUE 
                ORDER BY categoria
            """)
            
            self.categorias = ['Todos'] + [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            print(f"📂 {len(self.categorias)} categorías cargadas")
            
        except Exception as e:
            print(f"❌ Error cargando categorías: {e}")
            self.categorias = ['Todos']
    
    def cargar_productos(self):
        """Cargar productos con filtros"""
        try:
            conn = psycopg2.connect(**self.db_service.conn_params)
            cur = conn.cursor()
            
            query = """
                SELECT id, nombre, categoria, precio, stock, 
                       descripcion, imagen_url, activo
                FROM productos 
                WHERE activo = TRUE
            """
            params = []
            
            # Aplicar filtro de categoría
            if self.categoria_filtro and self.categoria_filtro != "Todos":
                query += " AND categoria = %s"
                params.append(self.categoria_filtro)
            
            # Aplicar búsqueda
            if self.busqueda_texto and self.busqueda_texto.strip():
                query += " AND LOWER(nombre) LIKE LOWER(%s)"
                params.append(f"%{self.busqueda_texto}%")
            
            query += " ORDER BY categoria, nombre"
            
            cur.execute(query, params)
            
            self.productos = []
            for row in cur.fetchall():
                self.productos.append({
                    'id': row[0],
                    'nombre': row[1],
                    'categoria': row[2],
                    'precio': float(row[3]),
                    'stock': row[4],
                    'descripcion': row[5] or '',
                    'imagen_url': row[6] or '',
                    'activo': row[7]
                })
            
            cur.close()
            conn.close()
            
            print(f"📦 {len(self.productos)} productos cargados")
            self.actualizar_ui_productos()
            
        except Exception as e:
            print(f"❌ Error cargando productos: {e}")
            self.mostrar_error("Error al cargar productos")
    
    def actualizar_ui_productos(self):
        """Actualizar UI con productos"""
        if not hasattr(self, 'ids') or 'grid_productos' not in self.ids:
            return
        
        self.ids.grid_productos.clear_widgets()
        
        if not self.productos:
            # Estado vacío
            empty = MDBoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))
            empty.add_widget(MDLabel(
                text="📭",
                font_size=sp(64),
                halign="center",
                size_hint_y=None,
                height=dp(80)
            ))
            empty.add_widget(MDLabel(
                text="No hay productos",
                font_style="H6",
                halign="center",
                theme_text_color="Secondary"
            ))
            self.ids.grid_productos.add_widget(empty)
            return
        
        # Crear cards de productos
        for producto in self.productos:
            card = ProductoInventarioCard(
                producto_data=producto,
                inventario_screen=self
            )
            self.ids.grid_productos.add_widget(card)
        
        # Actualizar contador
        if 'label_count' in self.ids:
            self.ids.label_count.text = f"{len(self.productos)} productos"
    
    def filtrar_por_categoria(self, categoria):
        """Filtrar productos por categoría"""
        self.categoria_filtro = categoria
        print(f"🔍 Filtrando por: {categoria}")
        self.cargar_productos()
    
    def buscar_productos(self, texto):
        """Buscar productos por nombre"""
        self.busqueda_texto = texto
        # Debouncing - esperar 0.5s después de escribir
        if hasattr(self, '_busqueda_timer'):
            self._busqueda_timer.cancel()
        self._busqueda_timer = Clock.schedule_once(lambda dt: self.cargar_productos(), 0.5)
    
    def agregar_producto(self):
        """Diálogo para agregar nuevo producto"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=dp(420)
        )
        
        # Nombre
        input_nombre = MDTextField(
            hint_text="Nombre del producto *",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_nombre)
        
        # Categoría
        categoria_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        categoria_layout.add_widget(MDLabel(
            text="Categoría:",
            size_hint_x=0.3
        ))
        
        spinner_categoria = Spinner(
            text=self.categorias[0] if self.categorias else "Bebidas",
            values=[c for c in self.categorias if c != 'Todos'],
            size_hint_x=0.7
        )
        categoria_layout.add_widget(spinner_categoria)
        content.add_widget(categoria_layout)
        
        # Precio
        input_precio = MDTextField(
            hint_text="Precio *",
            mode="rectangle",
            input_filter="float",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_precio)
        
        # Stock inicial
        input_stock = MDTextField(
            hint_text="Stock inicial",
            text="0",
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_stock)
        
        # Peso
        input_peso = MDTextField(
            hint_text="Peso (gramos)",
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_peso)
        
        # Descripción
        input_descripcion = MDTextField(
            hint_text="Descripción",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(input_descripcion)
        
        self.dialog = MDDialog(
            title="Nuevo Producto",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="GUARDAR",
                    md_bg_color=ds_color('success'),
                    on_release=lambda x: self._guardar_producto(
                        input_nombre.text,
                        spinner_categoria.text,
                        input_precio.text,
                        input_stock.text,
                        input_peso.text,
                        input_descripcion.text
                    )
                )
            ]
        )
        self.dialog.open()
    
    def _guardar_producto(self, nombre, categoria, precio_str, stock_str, peso_str, descripcion):
        """Guardar producto en BD"""
        try:
            # Validaciones
            if not nombre or not nombre.strip():
                self.mostrar_error("El nombre es requerido")
                return
            
            if not precio_str or not precio_str.strip():
                self.mostrar_error("El precio es requerido")
                return
            
            precio = float(precio_str)
            stock = int(stock_str) if stock_str else 0
            peso = int(peso_str) if peso_str else 0
            
            # Insertar en BD
            conn = psycopg2.connect(**self.db_service.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO productos 
                (nombre, categoria, precio, stock, descripcion, peso_gramos)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre.strip(), categoria, precio, stock, descripcion.strip(), peso))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.dialog.dismiss()
            self.mostrar_info(f"✅ Producto '{nombre}' agregado")
            self.cargar_productos()
            
        except ValueError:
            self.mostrar_error("Valores numéricos inválidos")
        except Exception as e:
            print(f"❌ Error guardando producto: {e}")
            self.mostrar_error("Error al guardar producto")
    
    def editar_producto(self, producto_data):
        """Diálogo para editar producto"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(20),
            size_hint_y=None,
            height=dp(350)
        )
        
        # Nombre
        input_nombre = MDTextField(
            hint_text="Nombre",
            text=producto_data['nombre'],
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_nombre)
        
        # Precio
        input_precio = MDTextField(
            hint_text="Precio",
            text=str(producto_data['precio']),
            mode="rectangle",
            input_filter="float",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_precio)
        
        # Stock
        input_stock = MDTextField(
            hint_text="Stock",
            text=str(producto_data['stock']),
            mode="rectangle",
            input_filter="int",
            size_hint_y=None,
            height=dp(48)
        )
        content.add_widget(input_stock)
        
        # Descripción
        input_descripcion = MDTextField(
            hint_text="Descripción",
            text=producto_data['descripcion'],
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(input_descripcion)
        
        self.dialog = MDDialog(
            title=f"Editar: {producto_data['nombre']}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="GUARDAR",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: self._actualizar_producto(
                        producto_data['id'],
                        input_nombre.text,
                        input_precio.text,
                        input_stock.text,
                        input_descripcion.text
                    )
                )
            ]
        )
        self.dialog.open()
    
    def _actualizar_producto(self, producto_id, nombre, precio_str, stock_str, descripcion):
        """Actualizar producto en BD"""
        try:
            precio = float(precio_str)
            stock = int(stock_str)
            
            conn = psycopg2.connect(**self.db_service.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE productos 
                SET nombre = %s, precio = %s, stock = %s, descripcion = %s
                WHERE id = %s
            """, (nombre.strip(), precio, stock, descripcion.strip(), producto_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.dialog.dismiss()
            self.mostrar_info("✅ Producto actualizado")
            self.cargar_productos()
            
        except Exception as e:
            print(f"❌ Error actualizando: {e}")
            self.mostrar_error("Error al actualizar")
    
    def eliminar_producto(self, producto_data):
        """Confirmar y eliminar producto"""
        self.dialog = MDDialog(
            title="Eliminar Producto",
            text=f"¿Eliminar '{producto_data['nombre']}'?\nEsta acción no se puede deshacer.",
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ELIMINAR",
                    md_bg_color=ds_color('error'),
                    on_release=lambda x: self._confirmar_eliminar(producto_data['id'])
                )
            ]
        )
        self.dialog.open()
    
    def _confirmar_eliminar(self, producto_id):
        """Eliminar producto (soft delete)"""
        try:
            conn = psycopg2.connect(**self.db_service.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE productos 
                SET activo = FALSE 
                WHERE id = %s
            """, (producto_id,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.dialog.dismiss()
            self.mostrar_info("✅ Producto eliminado")
            self.cargar_productos()
            
        except Exception as e:
            print(f"❌ Error eliminando: {e}")
            self.mostrar_error("Error al eliminar")
    
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


# ========== WIDGET PERSONALIZADO ==========

class ProductoInventarioCard(MDCard):
    """Card de producto para inventario"""
    producto_data = DictProperty({})
    inventario_screen = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = dp(180)
        self.padding = dp(12)
        self.spacing = dp(8)
        self.elevation = 2
        self.radius = dp(12)
        self.md_bg_color = ds_color('white')
        
        self._build_ui()
    
    def _build_ui(self):
        """Construir UI del card"""
        # Header
        header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        header.add_widget(MDLabel(
            text=self.producto_data['nombre'],
            font_style="Subtitle1",
            bold=True,
            size_hint_x=0.7
        ))
        header.add_widget(MDLabel(
            text=f"${self.producto_data['precio']:.2f}",
            font_style="Subtitle1",
            bold=True,
            halign="right",
            size_hint_x=0.3,
            theme_text_color="Custom",
            text_color=ds_color('success')
        ))
        self.add_widget(header)
        
        # Info
        self.add_widget(MDLabel(
            text=f"Categoría: {self.producto_data['categoria']}",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20)
        ))
        
        self.add_widget(MDLabel(
            text=f"Stock: {self.producto_data['stock']} unidades",
            font_style="Body2",
            size_hint_y=None,
            height=dp(25)
        ))
        
        # Descripción
        if self.producto_data['descripcion']:
            self.add_widget(MDLabel(
                text=self.producto_data['descripcion'][:60] + "...",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(30)
            ))
        
        # Botones
        btn_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40)
        )
        
        btn_layout.add_widget(MDRaisedButton(
            text="EDITAR",
            icon="pencil",
            md_bg_color=ds_color('primary'),
            on_release=self.editar
        ))
        
        btn_layout.add_widget(MDFlatButton(
            text="ELIMINAR",
            icon="delete",
            theme_text_color="Custom",
            text_color=ds_color('error'),
            on_release=self.eliminar
        ))
        
        self.add_widget(btn_layout)
    
    def editar(self, instance):
        if self.inventario_screen:
            self.inventario_screen.editar_producto(self.producto_data)
    
    def eliminar(self, instance):
        if self.inventario_screen:
            self.inventario_screen.eliminar_producto(self.producto_data)