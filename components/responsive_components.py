# mis_widgets/responsive_components.py
from kivymd.uix.card import MDCard
from kivy.properties import BooleanProperty
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.properties import NumericProperty, StringProperty, ColorProperty, OptionProperty
from kivy.metrics import dp, sp


class ResponsiveCard(MDCard):
    """Card responsivo moderno para KivyMD 2.0.1"""
    
    elevation_multiplier = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_appearance()
    
    def update_appearance(self):
        """Actualizar apariencia según tamaño de pantalla"""
        from utils.helpers import es_movil, es_tablet, obtener_espaciado
        
        if es_movil():
            self.elevation = 1 * self.elevation_multiplier
            self.padding = [obtener_espaciado(1.5),]
            self.radius = [obtener_espaciado(1),]
        elif es_tablet():
            self.elevation = 2 * self.elevation_multiplier
            self.padding = [obtener_espaciado(2),]
            self.radius = [obtener_espaciado(1.5),]
        else:
            self.elevation = 3 * self.elevation_multiplier
            self.padding = [obtener_espaciado(2.5),]
            self.radius = [obtener_espaciado(2),]

class ResponsiveButton(MDButton):
    """Botón responsivo moderno para KivyMD 2.0.1"""
    
    button_style = OptionProperty("filled", options=["filled", "elevated", "outlined", "text"])
    responsive_height = NumericProperty(48)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_appearance()
        
    def update_appearance(self):
        """Actualizar apariencia del botón"""
        from utils.helpers import obtener_altura_boton, es_movil
        
        self.responsive_height = obtener_altura_boton()
        
        # Estilos responsivos
        if es_movil():
            self.size_hint_x = 1.0  # Botones más anchos en móvil
        else:
            self.size_hint_x = None
            self.width = dp(120)

class ResponsiveLabel(MDLabel):
    """Label responsivo con roles de Material Design 3"""
    
    role = OptionProperty("body", options=[
        "display", "headline", "title", "body", "label", "caption"
    ])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_size = True
        self.update_typography()
    
    def update_typography(self):
        """Actualizar tipografía según role y tamaño de pantalla"""
        from utils.helpers import es_movil
        
        # Mapeo de roles a estilos responsivos
        role_sizes = {
            "display": "H4",
            "headline": "H5", 
            "title": "H6",
            "body": "Body1",
            "label": "Body2",
            "caption": "Caption"
        }
        
        # Ajustar para móvil
        if es_movil() and self.role in ["display", "headline"]:
            # Reducir tamaño en móvil para títulos grandes
            adjusted_role = "title" if self.role == "display" else "title"
            self.font_style = role_sizes[adjusted_role]
        else:
            self.font_style = role_sizes.get(self.role, "Body1")

class StatsCard(ResponsiveCard):
    """Card para mostrar estadísticas - Versión moderna"""
    
    title = StringProperty("")
    value = StringProperty("")
    icon = StringProperty("")
    value_color = ColorProperty([0.2, 0.6, 0.2, 1])  # Verde por defecto
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.padding = dp(15)
        self.build_content()
    
    def build_content(self):
        """Construir contenido del card de estadísticas"""
        # Layout de icono y título
        header_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10))
        
        #from kivymd.uix.icon import MDIcon
        icon_widget = MDIcon(
            icon=self.icon,
            size_hint_x=None,
            width=dp(30),
            theme_text_color="Primary"
        )
        header_layout.add_widget(icon_widget)
        
        title_label = ResponsiveLabel(
            text=self.title,
            role="label",
            theme_text_color="Secondary"
        )
        header_layout.add_widget(title_label)
        
        self.add_widget(header_layout)
        
        # Valor
        value_label = ResponsiveLabel(
            text=self.value,
            role="headline",
            theme_text_color="Primary"
        )
        value_label.color = self.value_color
        self.add_widget(value_label)

class ResponsiveGrid(MDGridLayout):
    """Grid layout responsivo"""
    
    default_cols = NumericProperty(2)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_columns()
    
    def update_columns(self):
        """Actualizar número de columnas según tamaño de pantalla"""
        from utils.helpers import obtener_columnas_grid
        self.cols = obtener_columnas_grid(self.default_cols)

class ProductCard(ResponsiveCard):
    """Card especializado para productos"""
    
    product_name = StringProperty("")
    product_price = StringProperty("")
    product_image = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(5)
        self.padding = dp(10)
        self.size_hint = (None, None)
        self.size = (dp(150), dp(180))
        self.build_product_content()
    
    def build_product_content(self):
        """Construir contenido del card de producto"""
        # Imagen del producto (placeholder)
        from kivymd.uix.fitimage import FitImage
        image = FitImage(
            size_hint_y=0.5,
            source=self.product_image or "data/placeholder.png",
            radius=[dp(10), dp(10), 0, 0]
        )
        self.add_widget(image)
        
        # Información del producto
        info_layout = MDBoxLayout(orientation="vertical", spacing=dp(5))
        
        # Nombre
        name_label = ResponsiveLabel(
            text=self.product_name,
            role="body",
            theme_text_color="Primary",
            adaptive_size=True,
            shorten=True,
            shorten_from="right"
        )
        info_layout.add_widget(name_label)
        
        # Precio
        price_label = ResponsiveLabel(
            text=self.product_price,
            role="title",
            theme_text_color="Primary",
            bold=True
        )
        info_layout.add_widget(price_label)
        
        # Botón de acción
        action_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        
        from kivymd.uix.button import MDIconButton
        add_button = MDIconButton(
            icon="plus",
            theme_icon_color="Primary",
            pos_hint={"center_x": 0.5}
        )
        action_layout.add_widget(add_button)
        
        info_layout.add_widget(action_layout)
        self.add_widget(info_layout)

class OrderItemCard(ResponsiveCard):
    """Card para items del pedido"""
    
    item_name = StringProperty("")
    item_price = StringProperty("")
    item_quantity = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.spacing = dp(10)
        self.padding = dp(10)
        self.size_hint_y = None
        self.height = dp(60)
        self.build_order_item_content()
    
    def build_order_item_content(self):
        """Construir contenido del item de pedido"""
        # Información del producto
        info_layout = MDBoxLayout(orientation="vertical", size_hint_x=0.6)
        
        name_label = ResponsiveLabel(
            text=self.item_name,
            role="body",
            theme_text_color="Primary"
        )
        info_layout.add_widget(name_label)
        
        price_label = ResponsiveLabel(
            text=self.item_price,
            role="caption",
            theme_text_color="Secondary"
        )
        info_layout.add_widget(price_label)
        
        self.add_widget(info_layout)
        
        # Controles de cantidad
        quantity_layout = MDBoxLayout(orientation="horizontal", size_hint_x=0.4, spacing=dp(5))
        
        from kivymd.uix.button import MDIconButton
        minus_btn = MDIconButton(
            icon="minus",
            size_hint=(None, None),
            size=(dp(30), dp(30))
        )
        quantity_layout.add_widget(minus_btn)
        
        quantity_label = ResponsiveLabel(
            text=str(self.item_quantity),
            size_hint_x=0.4,
            halign="center",
            role="body"
        )
        quantity_layout.add_widget(quantity_label)
        
        plus_btn = MDIconButton(
            icon="plus",
            size_hint=(None, None),
            size=(dp(30), dp(30))
        )
        quantity_layout.add_widget(plus_btn)
        
        self.add_widget(quantity_layout)

class ResponsiveAppBar(MDBoxLayout):
    """App Bar responsivo"""
    
    title = StringProperty("")
    show_menu = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(56)
        self.padding = [dp(10), 0, dp(10), 0]
        self.build_app_bar()
    
    def build_app_bar(self):
        """Construir app bar"""
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.toolbar import MDTopAppBar
        
        # Botón menú (solo si es necesario)
        if self.show_menu:
            menu_btn = MDIconButton(icon="menu")
            self.add_widget(menu_btn)
        
        # Título
        title_label = ResponsiveLabel(
            text=self.title,
            role="headline",
            theme_text_color="Primary",
            size_hint_x=1
        )
        self.add_widget(title_label)
        
        # Espacio para acciones adicionales
        actions_layout = MDBoxLayout(orientation="horizontal", size_hint_x=None, width=dp(100))
        self.add_widget(actions_layout)

# Clase de utilidad para manejar temas
class ThemeManager:
    """Gestor de temas para la aplicación"""
    
    @staticmethod
    def get_color_scheme(style="light"):
        """Obtener esquema de colores según estilo"""
        schemes = {
            "light": {
                "primary": "#FF6B35",
                "secondary": "#2EC4B6", 
                "background": "#F8F9FA",
                "surface": "#FFFFFF",
                "on_primary": "#FFFFFF",
                "on_surface": "#2C3E50"
            },
            "dark": {
                "primary": "#FF8E53", 
                "secondary": "#4ECDC4",
                "background": "#121212",
                "surface": "#1E1E1E",
                "on_primary": "#000000",
                "on_surface": "#FFFFFF"
            }
        }
        return schemes.get(style, schemes["light"])
    
    @staticmethod
    def setup_theme(app, style="light"):
        """Configurar tema de la aplicación"""
        color_scheme = ThemeManager.get_color_scheme(style)
        
        # Configurar colores primarios
        app.theme_cls.primary_palette = "Orange"
        app.theme_cls.theme_style = "Light" if style == "light" else "Dark"
        
        # Aquí puedes agregar más personalizaciones de tema

# Factory para crear componentes fácilmente
class ComponentFactory:
    """Fábrica de componentes responsivos"""
    
    @staticmethod
    def create_button(text, style="filled", on_press=None):
        """Crear botón responsivo"""
        button = ResponsiveButton(button_style=style)
        button_text = MDButtonText(text=text)
        button.add_widget(button_text)
        
        if on_press:
            button.bind(on_press=on_press)
        
        return button
    
    @staticmethod
    def create_label(text, role="body", **kwargs):
        """Crear label responsivo"""
        return ResponsiveLabel(text=text, role=role, **kwargs)
    
    @staticmethod
    def create_card(**kwargs):
        """Crear card responsivo"""
        return ResponsiveCard(**kwargs)
    
    @staticmethod
    def create_stats_card(title, value, icon, value_color=None):
        """Crear card de estadísticas"""
        card = StatsCard(title=title, value=value, icon=icon)
        if value_color:
            card.value_color = value_color
        return card

# Hacer disponibles los componentes globalmente
import builtins
builtins.ResponsiveButton = ResponsiveButton
builtins.ResponsiveLabel = ResponsiveLabel
builtins.ResponsiveCard = ResponsiveCard
builtins.StatsCard = StatsCard
builtins.ProductCard = ProductCard
builtins.ComponentFactory = ComponentFactory