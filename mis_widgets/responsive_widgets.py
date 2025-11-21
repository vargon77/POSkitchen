# mis_widgets/responsive_widgets.py - VERSIÓN COMPLETA FASE 3
"""
Widgets personalizados responsivos para POS
Compatible con Kivy 2.3.0 y KivyMD 1.2.0
TODOS los widgets necesarios para el proyecto
"""
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.chip import MDChip
from kivymd.uix.textfield import MDTextField
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.properties import (StringProperty, NumericProperty, ListProperty, 
                            BooleanProperty, ObjectProperty, DictProperty)
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.core.window import Window
from kivy.metrics import dp, sp

from themes.design_system import (DesignSystem,
    ds_color, ds_spacing, ds_font, ds_button_height, ds_grid_cols, ds_is_mobile
)


# ==================== BOTONES RESPONSIVOS ====================

class ResponsiveButton(Button):
    """Botón adaptativo base"""
    
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
        
        size_map = {'sm': 'sm', 'md': 'base', 'lg': 'lg'}
        self.font_size = ds_font(size_map.get(self.button_size, 'base'))
        
        color_map = {
            'primary': 'primary', 'success': 'success', 'error': 'error',
            'warning': 'warning', 'secondary': 'secondary', 'info': 'info'
        }
        
        self.background_color = ds_color(color_map.get(self.button_style, 'primary'))
        self.color = ds_color('white')
        self.bold = True


class ResponsiveMDRaisedButton(MDRaisedButton):
    """MDRaisedButton responsivo"""
    
    button_size = StringProperty('md')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_styles()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_styles()
    
    def _apply_styles(self):
        self.size_hint_y = None
        self.height = ds_button_height(self.button_size)


class ResponsiveMDIconButton(MDIconButton):
    """MDIconButton responsivo"""
    pass


# ==================== CARDS RESPONSIVOS ====================

class ResponsiveCard(MDCard):
    """Card responsivo base"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_responsive_styles()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_responsive_styles()
    
    def _apply_responsive_styles(self):
        padding = DesignSystem.get_card_padding()
        self.padding = padding
        self.spacing = ds_spacing('sm')


# ==================== LABELS RESPONSIVOS ====================

class ResponsiveLabel(MDLabel):
    """Label responsivo con estilos"""
    
    label_style = StringProperty('body')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_style()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_style()
    
    def _apply_style(self):
        style_map = {
            'title': 'xl',
            'subtitle': 'lg', 
            'body': 'base',
            'caption': 'sm'
        }
        
        self.font_size = ds_font(style_map.get(self.label_style, 'base'))
        
        if self.label_style == 'title':
            self.bold = True


# ==================== BOXLAYOUTS RESPONSIVOS ====================

class ResponsiveBoxLayout(MDBoxLayout):
    """BoxLayout responsivo"""
    
    responsive_spacing = StringProperty('md')
    responsive_padding = StringProperty('md')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_responsive_styles()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_responsive_styles()
    
    def _apply_responsive_styles(self):
        if self.responsive_spacing:
            self.spacing = ds_spacing(self.responsive_spacing)
        if self.responsive_padding:
            self.padding = ds_spacing(self.responsive_padding)


# ==================== GRIDS RESPONSIVOS ====================

class ResponsiveGridLayout(MDGridLayout):
    """GridLayout responsivo"""
    
    default_cols = NumericProperty(2)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_columns()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self.update_columns()
    
    def update_columns(self):
        self.cols = ds_grid_cols(self.default_cols)


# ==================== TEXTFIELDS RESPONSIVOS ====================

class ResponsiveTextField(MDTextField):
    """TextField responsivo"""
    
    field_size = StringProperty('md')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_styles()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_styles()
    
    def _apply_styles(self):
        if self.field_size == 'sm':
            self.height = dp(40)
        elif self.field_size == 'lg':
            self.height = dp(56)
        else:
            self.height = dp(48)
        
        self.size_hint_y = None


# ==================== CHIPS RESPONSIVOS ====================

class ResponsiveChip(MDChip):
    """Chip responsivo"""
    
    selected = BooleanProperty(False)
    categoria = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self._apply_styles()
        self.bind(selected=self._update_colors)
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, instance, width, height):
        self._apply_styles()
    
    def _apply_styles(self):
        if ds_is_mobile():
            self.height = dp(32)
            self.font_size = ds_font('sm')
        else:
            self.height = dp(36)
            self.font_size = ds_font('base')
        
        # Ancho mínimo
        self.width = dp(80)
    
    def _update_colors(self, *args):
        if self.selected:
            self.md_bg_color = ds_color('primary')
            self.text_color = ds_color('white')
        else:
            self.md_bg_color = ds_color('gray_light')
            self.text_color = ds_color('dark')
    
    def on_text(self, instance, value):
        """Ajustar ancho al texto"""
        estimated_width = len(value) * 7 + ds_spacing('lg')
        self.width = max(dp(80), dp(estimated_width))


# ==================== SCROLLVIEWS RESPONSIVOS ====================

class ResponsiveScrollView(ScrollView):
    """ScrollView optimizado"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if DesignSystem.is_mobile():
            self.bar_width = dp(6)
        else:
            self.bar_width = dp(8)
        
        self.bar_color = ds_color('primary', 0.6)
        self.always_overscroll = False


# ==================== SEPARADORES ====================

class ResponsiveSeparator(BoxLayout):
    """Separador responsivo"""
    
    separator_color = ListProperty([0.7, 0.7, 0.7, 0.5])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        
        with self.canvas:
            Color(*self.separator_color)
            self.line = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update, size=self._update)
    
    def _update(self, *args):
        self.line.pos = self.pos
        self.line.size = self.size


# ==================== SPINNERS RESPONSIVOS ====================

class ResponsiveSpinner(Spinner):
    """Spinner responsivo"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = ds_color('white')
        self.color = ds_color('dark')
        self.size_hint_y = None
        self.height = dp(48)


# ==================== WIDGETS ESPECÍFICOS DEL PROYECTO ====================

class CategoryChipPro(ResponsiveChip):
    """Chip profesional para categorías"""
    pass


class ProductCardPro(ResponsiveCard):
    """Card profesional de producto"""
    
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


class OrderItemPro(ResponsiveCard):
    """Item profesional de pedido"""
    
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


class PedidoItemCompact(ResponsiveCard):
    """Item compacto de pedido"""
    
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


class ItemFilaTabla(ResponsiveBoxLayout):
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


class PedidoCocinaCard(ResponsiveCard):
    """Card de pedido para cocina"""
    
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
        colores = {
            'pendiente': ds_color('warning'),
            'confirmado': ds_color('warning'),
            'preparacion': ds_color('info'),
            'listo': ds_color('success')
        }
        return colores.get(self.estado, ds_color('gray'))
    
    @property
    def color_estado_light(self):
        colores = {
            'pendiente': (*ds_color('warning')[:3], 0.1),
            'confirmado': (*ds_color('warning')[:3], 0.1),
            'preparacion': (*ds_color('info')[:3], 0.1),
            'listo': (*ds_color('success')[:3], 0.1)
        }
        return colores.get(self.estado, (*ds_color('gray')[:3], 0.1))
    
    @property
    def color_tiempo(self):
        if "🔴" in self.tiempo_espera:
            return ds_color('error')
        elif "⚠️" in self.tiempo_espera:
            return ds_color('warning')
        else:
            return ds_color('success')
    
    @property
    def texto_boton_principal(self):
        textos = {
            'pendiente': 'INICIAR',
            'confirmado': 'INICIAR',
            'preparacion': 'MARCAR LISTO',
            'listo': 'ENTREGADO'
        }
        return textos.get(self.estado, 'ACCIÓN')
    
    @property
    def icono_boton_principal(self):
        iconos = {
            'pendiente': 'play',
            'confirmado': 'play',
            'preparacion': 'check',
            'listo': 'check-all'
        }
        return iconos.get(self.estado, 'check')
    
    @property
    def color_boton_principal(self):
        colores = {
            'pendiente': ds_color('warning'),
            'confirmado': ds_color('warning'),
            'preparacion': ds_color('success'),
            'listo': ds_color('info')
        }
        return colores.get(self.estado, ds_color('primary'))
    
    def accion_principal(self):
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
        if self.cocina_screen:
            self.cocina_screen.ver_detalle_pedido(self.pedido_id)


class PedidoPagoCard(ResponsiveCard):
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


# ==================== ESTADOS VACÍOS ====================

class EmptyStateWidget(ResponsiveBoxLayout):
    """Widget para estados vacíos"""
    
    message = StringProperty('No hay datos')
    icon = StringProperty('🔭')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = ds_spacing('2xl')
        self.spacing = ds_spacing('md')


class CocinaEmptyState(EmptyStateWidget):
    """Estado vacío cocina"""
    
    def __init__(self, **kwargs):
        kwargs['icon'] = '👨‍🍳'
        kwargs['message'] = 'Sin pedidos activos'
        super().__init__(**kwargs)


class CajaEmptyState(EmptyStateWidget):
    """Estado vacío caja"""
    
    def __init__(self, **kwargs):
        kwargs['icon'] = '💰'
        kwargs['message'] = 'Sin pedidos pendientes'
        super().__init__(**kwargs)


class EmptyCartState(EmptyStateWidget):
    """Estado vacío carrito"""
    
    def __init__(self, **kwargs):
        kwargs['icon'] = '🛒'
        kwargs['message'] = 'Carrito vacío'
        super().__init__(**kwargs)


# ==================== CARDS ESTADÍSTICAS ====================

class EstadisticaCard(ResponsiveCard):
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