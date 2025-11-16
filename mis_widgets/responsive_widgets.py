# mis_widgets/responsive_widgets.py
"""
Widgets personalizados responsivos para POS
Compatible con Kivy 2.3.0 y KivyMD 1.2.0
"""
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Rectangle

from themes.design_system import (DesignSystem,
    ds_color, ds_spacing, ds_font, ds_button_height, ds_grid_cols, ds_is_mobile
)


# ==================== BOTONES ====================

class ResponsiveButton(Button):
    """Botón adaptativo usando DesignSystem unificado"""
    
    button_style = StringProperty('primary')
    button_size = StringProperty('md')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self._apply_styles()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_styles()
    
    def _apply_styles(self):
        self.height = ds_button_height(self.button_size)
        self.size_hint_y = None
        
        # Tamaño de fuente responsivo
        size_map = {'sm': 'sm', 'md': 'base', 'lg': 'lg'}
        self.font_size = ds_font(size_map.get(self.button_size, 'base'))
        
        # Colores según estilo
        color_map = {
            'primary': 'primary', 'success': 'success', 'error': 'error',
            'warning': 'warning', 'secondary': 'secondary',
        }
        
        self.background_color = ds_color(color_map.get(self.button_style, 'primary'))
        self.color = ds_color('white')
        self.bold = True



class ResponsiveIconButton(ResponsiveButton):
    """Botón con icono (emoji o texto)"""
    
    icon = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.icon:
            self.text = f"{self.icon} {self.text}" if self.text else self.icon


# ==================== TARJETAS ====================

class ResponsiveCard(BoxLayout):
    """Tarjeta responsiva usando DesignSystem unificado"""
    
    elevation = NumericProperty(2)
    border_radius = NumericProperty(8)
    bg_color = ListProperty([1, 1, 1, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self._apply_responsive_styles()
        self._update_canvas()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_responsive_styles()
    
    def _apply_responsive_styles(self):
        """Aplicar estilos usando DesignSystem unificado"""
        from themes.design_system import DesignSystem
        padding = DesignSystem.get_card_padding()
        self.padding = padding
        self.spacing = ds_spacing('sm')
    
    def _update_canvas(self):
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.border_radius)]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ProductCard(ResponsiveCard):
    """Tarjeta de producto optimizada"""
    
    producto_nombre = StringProperty('')
    producto_precio = NumericProperty(0.0)
    producto_stock = NumericProperty(0)
    on_select = None
    
    def __init__(self, **kwargs):
        # Extraer callback antes de super
        self.on_select = kwargs.pop('on_select', None)
        super().__init__(**kwargs)
        self._build_ui()
    
    def _build_ui(self):
        """Construir UI de la tarjeta"""
        self.clear_widgets()
        
        # Nombre del producto
        lbl_nombre = Label(
            text=self.producto_nombre,
            font_size=ds_font('md'),
            bold=True,
            size_hint_y=0.5,
            halign='center',
            valign='middle'
        )
        lbl_nombre.bind(size=lbl_nombre.setter('text_size'))
        self.add_widget(lbl_nombre)
        
        # Precio
        lbl_precio = Label(
            text=f"${self.producto_precio:.2f}",
            font_size=ds_font('lg'),
            color=ds_color('primary'),
            bold=True,
            size_hint_y=0.3,
            halign='center'
        )
        self.add_widget(lbl_precio)
        
        # Stock (si aplica)
        if self.producto_stock > 0:
            lbl_stock = Label(
                text=f"Stock: {self.producto_stock}",
                font_size=ds_font('sm'),
                color=ds_color('gray'),
                size_hint_y=0.2
            )
            self.add_widget(lbl_stock)
    
    def on_touch_down(self, touch):
        """Manejar toque/click"""
        if self.collide_point(*touch.pos):
            if self.on_select:
                self.on_select(self)
            return True
        return super().on_touch_down(touch)


# ==================== LAYOUTS ====================
class ResponsiveGridLayout(MDGridLayout):
    """GridLayout responsivo usando DesignSystem unificado"""
    
    default_cols = NumericProperty(2)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_columns()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self.update_columns()
    
    def update_columns(self):
        self.cols = ds_grid_cols(self.default_cols)


class ResponsiveScrollView(ScrollView):
    """ScrollView con configuración optimizada"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Optimizar para móvil
        if DesignSystem.is_mobile():
            self.bar_width = dp(6)
            self.scroll_type = ['bars', 'content']
        else:
            self.bar_width = dp(8)
        
        self.bar_color = ds_color('primary', 0.6)
        self.always_overscroll = False


# ==================== ITEMS DE LISTA ====================

class PedidoItemCard(ResponsiveCard):
    """Item de pedido en lista"""
    
    item_nombre = StringProperty('')
    item_cantidad = NumericProperty(1)
    item_precio = NumericProperty(0.0)
    item_subtotal = NumericProperty(0.0)
    
    on_increase = None
    on_decrease = None
    on_delete = None
    
    def __init__(self, **kwargs):
        # Extraer callbacks
        self.on_increase = kwargs.pop('on_increase', None)
        self.on_decrease = kwargs.pop('on_decrease', None)
        self.on_delete = kwargs.pop('on_delete', None)
        
        super().__init__(**kwargs)
        self.size_hint_y = None
        
        # Altura adaptativa
        if DesignSystem.is_mobile():
            self.height = dp(60)
        else:
            self.height = dp(70)
        
        self._build_ui()
    
    def _build_ui(self):
        """Construir UI del item"""
        self.clear_widgets()
        
        layout = BoxLayout(orientation='horizontal', spacing=ds_spacing('sm'))
        
        # Nombre (50%)
        lbl_nombre = Label(
            text=self.item_nombre,
            size_hint_x=0.4,
            font_size=ds_font('base'),
            text_size=(None, None),
            halign='left',
            valign='middle'
        )
        layout.add_widget(lbl_nombre)
        
        # Controles de cantidad
        if self.on_decrease or self.on_increase:
            # Botón -
            btn_menos = Button(
                text='-',
                size_hint_x=0.1,
                background_color=ds_color('error'),
                background_normal='',
                font_size=ds_font('lg'),
                bold=True
            )
            if self.on_decrease:
                btn_menos.bind(on_press=lambda x: self.on_decrease(self))
            layout.add_widget(btn_menos)
            
            # Cantidad
            lbl_cant = Label(
                text=str(self.item_cantidad),
                size_hint_x=0.1,
                font_size=ds_font('lg'),
                bold=True
            )
            layout.add_widget(lbl_cant)
            
            # Botón +
            btn_mas = Button(
                text='+',
                size_hint_x=0.1,
                background_color=ds_color('success'),
                background_normal='',
                font_size=ds_font('lg'),
                bold=True
            )
            if self.on_increase:
                btn_mas.bind(on_press=lambda x: self.on_increase(self))
            layout.add_widget(btn_mas)
        else:
            # Solo mostrar cantidad
            lbl_cant = Label(
                text=f"x{self.item_cantidad}",
                size_hint_x=0.2,
                font_size=ds_font('base'),
                bold=True
            )
            layout.add_widget(lbl_cant)
        
        # Subtotal
        lbl_subtotal = Label(
            text=f"${self.item_subtotal:.2f}",
            size_hint_x=0.3,
            font_size=ds_font('md'),
            bold=True,
            halign='right',
            color=ds_color('primary')
        )
        layout.add_widget(lbl_subtotal)
        
        self.add_widget(layout)


# ==================== ENCABEZADOS ====================

class SectionHeader(BoxLayout):
    """Encabezado de sección"""
    
    title = StringProperty('')
    subtitle = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(60) if self.subtitle else dp(40)
        self.padding = ds_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Construir encabezado"""
        lbl_title = Label(
            text=self.title,
            font_size=ds_font('xl'),
            bold=True,
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))
        self.add_widget(lbl_title)
        
        if self.subtitle:
            lbl_subtitle = Label(
                text=self.subtitle,
                font_size=ds_font('sm'),
                color=ds_color('gray'),
                halign='left',
                size_hint_y=None,
                height=dp(20)
            )
            lbl_subtitle.bind(size=lbl_subtitle.setter('text_size'))
            self.add_widget(lbl_subtitle)


# ==================== CHIPS/TAGS ====================

class ResponsiveChip(Button):
    """Chip/Tag para categorías"""
    
    selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.size_hint = (None, None)
        
        if DesignSystem.is_mobile():
            self.height = dp(32)
            self.font_size = ds_font('sm')
        else:
            self.height = dp(36)
            self.font_size = ds_font('base')
        
        self.update_appearance()
        self.bind(selected=lambda *x: self.update_appearance())
    
    def update_appearance(self):
        """Actualizar apariencia según estado"""
        if self.selected:
            self.background_color = ds_color('primary')
            self.color = ds_color('white')
        else:
            self.background_color = ds_color('light')
            self.color = ds_color('dark')
        
        self.bold = self.selected
    
    def on_size(self, *args):
        """Ajustar ancho al texto"""
        self.width = self.texture_size[0] + ds_spacing('lg')


# ==================== SEPARADORES ====================

class Divider(BoxLayout):
    """Línea divisora"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        
        with self.canvas:
            Color(*ds_color('gray_light'))
            self.line = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update, size=self._update)
    
    def _update(self, *args):
        self.line.pos = self.pos
        self.line.size = self.size


# ==================== UTILIDADES ====================

class EmptyStateWidget(BoxLayout):
    """Widget para estados vacíos"""
    
    message = StringProperty('No hay datos')
    icon = StringProperty('📭')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = ds_spacing('2xl')
        self.spacing = ds_spacing('md')
        
        # Icono
        lbl_icon = Label(
            text=self.icon,
            font_size=ds_font('4xl'),
            size_hint_y=None,
            height=dp(80)
        )
        self.add_widget(lbl_icon)
        
        # Mensaje
        lbl_msg = Label(
            text=self.message,
            font_size=ds_font('lg'),
            color=ds_color('gray'),
            italic=True
        )
        self.add_widget(lbl_msg)


class LoadingSpinner(BoxLayout):
    """Indicador de carga simple"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = ds_spacing('xl')
        
        lbl = Label(
            text='🔄 Cargando...',
            font_size=ds_font('lg'),
            color=ds_color('primary')
        )
        self.add_widget(lbl)