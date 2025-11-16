# mis_widgets/responsive_components.py
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.properties import NumericProperty, StringProperty, ColorProperty, OptionProperty
from kivy.metrics import dp, sp

class ResponsiveCard(MDCard):
    """Card responsivo simplificado para KivyMD 2.0.1"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configuración básica que funciona en KivyMD 2.0.1
        self.elevation = 1
        self.padding = dp(10)
        self.radius = dp(10)
        
    def on_size(self, *args):
        """Actualizar cuando cambia el tamaño"""
        self.update_appearance()
    
    def update_appearance(self):
        """Actualizar apariencia según tamaño de pantalla"""
        from kivy.core.window import Window
        
        if Window.width <= dp(600):  # Móvil
            self.padding = dp(8)
            self.radius = dp(8)
        elif Window.width <= dp(960):  # Tablet
            self.padding = dp(12)
            self.radius = dp(12)
        else:  # Desktop
            self.padding = dp(16)
            self.radius = dp(16)

class ResponsiveButton(MDButton):
    """Botón responsivo simplificado"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(48)
        
    def update_appearance(self):
        """Actualizar apariencia del botón"""
        from kivy.core.window import Window
        
        if Window.width <= dp(600):  # Móvil
            self.height = dp(44)
        elif Window.width <= dp(960):  # Tablet
            self.height = dp(48)
        else:  # Desktop
            self.height = dp(52)

class ResponsiveLabel(MDLabel):
    """Label responsivo simplificado - SIN USAR ROLES PROBLEMÁTICOS"""
    
    def __init__(self, **kwargs):
        # Eliminar cualquier referencia a 'role' que cause problemas
        if 'role' in kwargs:
            kwargs.pop('role')
        super().__init__(**kwargs)
        self.adaptive_size = True
        
    def set_font_size(self, size_type='body'):
        """Método seguro para establecer tamaño de fuente"""
        sizes = {
            'display': sp(32), 'headline': sp(24), 'title': sp(20),
            'body': sp(16), 'label': sp(14), 'caption': sp(12)
        }
        
        base_size = sizes.get(size_type, sp(16))
        
        # Ajustes responsivos
        from kivy.core.window import Window
        if Window.width <= dp(600):  # Móvil
            self.font_size = base_size * 0.9
        elif Window.width <= dp(960):  # Tablet
            self.font_size = base_size
        else:  # Desktop
            self.font_size = base_size * 1.1

class StatsCard(ResponsiveCard):
    """Card para mostrar estadísticas - Versión simplificada"""
    
    def __init__(self, title="", value="", icon="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.padding = dp(15)
        
        # Layout de icono y título
        header_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(30))
        
       # from kivymd.uix.icon import MDIcon
        icon_widget = MDIcon(
            icon=icon,
            size_hint_x=None,
            width=dp(30)
        )
        header_layout.add_widget(icon_widget)
        
        title_label = ResponsiveLabel(text=title)
        title_label.set_font_size('label')
        title_label.theme_text_color = "Secondary"
        header_layout.add_widget(title_label)
        
        self.add_widget(header_layout)
        
        # Valor
        value_label = ResponsiveLabel(text=value)
        value_label.set_font_size('headline')
        value_label.theme_text_color = "Primary"
        value_label.bold = True
        self.add_widget(value_label)

class ProductCard(ResponsiveCard):
    """Card especializado para productos - Versión simplificada"""
    
    def __init__(self, name="", price="", image="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(5)
        self.padding = dp(10)
        self.size_hint = (None, None)
        
        # Tamaño responsivo
        from kivy.core.window import Window
        if Window.width <= dp(600):  # Móvil
            self.size = (dp(120), dp(160))
        else:
            self.size = (dp(150), dp(180))
        
        # Imagen del producto
        from kivymd.uix.fitimage import FitImage
        image_widget = FitImage(
            size_hint_y=0.5,
            source=image or "data/placeholder.png",
            radius=[dp(10), dp(10), 0, 0]
        )
        self.add_widget(image_widget)
        
        # Información del producto
        info_layout = MDBoxLayout(orientation="vertical", spacing=dp(5))
        
        # Nombre
        name_label = ResponsiveLabel(text=name)
        name_label.set_font_size('body')
        name_label.theme_text_color = "Primary"
        name_label.shorten = True
        info_layout.add_widget(name_label)
        
        # Precio
        price_label = ResponsiveLabel(text=price)
        price_label.set_font_size('title')
        price_label.theme_text_color = "Primary"
        price_label.bold = True
        info_layout.add_widget(price_label)
        
        # Botón de acción
        from kivymd.uix.button import MDIconButton
        add_button = MDIconButton(
            icon="plus",
            pos_hint={"center_x": 0.5}
        )
        info_layout.add_widget(add_button)
        
        self.add_widget(info_layout)

# Factory simplificada
class ComponentFactory:
    """Fábrica de componentes responsivos simplificada"""
    
    @staticmethod
    def create_button(text, on_press=None, style="filled"):
        """Crear botón responsivo"""
        button = ResponsiveButton()
        button_text = MDButtonText(text=text)
        button.add_widget(button_text)
        
        if on_press:
            button.bind(on_press=on_press)
        
        return button
    
    @staticmethod
    def create_label(text, font_size='body', **kwargs):
        """Crear label responsivo"""
        label = ResponsiveLabel(text=text, **kwargs)
        label.set_font_size(font_size)
        return label
    
    @staticmethod
    def create_card(**kwargs):
        """Crear card responsivo"""
        return ResponsiveCard(**kwargs)
    
    @staticmethod
    def create_stats_card(title, value, icon):
        """Crear card de estadísticas"""
        return StatsCard(title=title, value=value, icon=icon)

# Hacer disponibles los componentes globalmente
import builtins
builtins.ResponsiveButton = ResponsiveButton
builtins.ResponsiveLabel = ResponsiveLabel
builtins.ResponsiveCard = ResponsiveCard
builtins.StatsCard = StatsCard
builtins.ProductCard = ProductCard
builtins.ComponentFactory = ComponentFactory