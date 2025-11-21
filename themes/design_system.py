# themes/design_system.py 
"""
Sistema de Diseño Unificado para POS
Compatible con Kivy 2.3.0 y KivyMD 1.2.0
"""
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from typing import Dict, Tuple, List
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty

class ScreenSize:
    """Clasificación de tamaños de pantalla"""
    MOBILE_SMALL = "mobile_small"    # < 480px
    MOBILE = "mobile"                # 480-767px
    TABLET = "tablet"                # 768-1023px
    DESKTOP = "desktop"              # >= 1024px

class DesignSystem(EventDispatcher):
    """Sistema centralizado de diseño y estilos - UNIFICADO"""
    
    # Breakpoints unificados
    BREAKPOINTS = {
        'xs': 360,   # Móviles pequeños
        'sm': 600,   # Móviles grandes/Tablets pequeñas  
        'md': 960,   # Tablets
        'lg': 1280,  # Desktop pequeños
        'xl': 1920   # Desktop grandes
    }
    
    # ==================== COLORES UNIFICADOS ====================
    COLORS = {
        # Colores principales (Material Design 3)
        'primary': get_color_from_hex('#6750A4'),
        'primary_dark': get_color_from_hex('#4F378B'),
        'primary_light': get_color_from_hex('#EADDFF'),
        
        'secondary': get_color_from_hex('#625B71'),
        'secondary_dark': get_color_from_hex('#4A4458'),
        'secondary_light': get_color_from_hex('#E8DEF8'),
        
        'accent': get_color_from_hex('#F4A261'),
        
        # Estados (compatibles con global_styles.kv)
        'success': get_color_from_hex('#0D6E42'),
        'warning': get_color_from_hex('#7C5800'),
        'error': get_color_from_hex('#B3261E'),
        'info': get_color_from_hex('#3498DB'),
        
        # Neutrales
        'dark': get_color_from_hex('#2C3E50'),
        'gray_dark': get_color_from_hex('#34495E'),
        'gray': get_color_from_hex('#7F8C8D'),
        'gray_light': get_color_from_hex('#BDC3C7'),
        'light': get_color_from_hex('#ECF0F1'),
        'white': get_color_from_hex('#FFFFFF'),
        
        # Estados de pedido
        'pedido_pendiente': get_color_from_hex('#F39C12'),
        'pedido_preparacion': get_color_from_hex('#3498DB'),
        'pedido_listo': get_color_from_hex('#2ECC71'),
        'pedido_pagado': get_color_from_hex('#9B59B6'),
    }
    
    # ==================== MÉTODOS RESPONSIVOS UNIFICADOS ====================
    
    @staticmethod
    def get_grid_cols(default_cols: int = 2) -> int:
        """Método de compatibilidad - usar ds_grid_cols() mejor"""
        return DesignSystem.grid_cols(default_cols)

    def spacing(size_key: str = 'base') -> float:
        """Espaciado responsivo UNIFICADO"""
        base_spacing = {
            'xs': 4, 'sm': 8, 'md': 12, 'base': 16,
            'lg': 20, 'xl': 24, '2xl': 32, '3xl': 40,
        }
        
        base = base_spacing.get(size_key, 16)
        
        # Lógica responsiva unificada
        if Window.width <= DesignSystem.BREAKPOINTS['xs']:
            return dp(base * 0.75)
        elif Window.width <= DesignSystem.BREAKPOINTS['sm']:
            return dp(base * 0.9)
        else:
            return dp(base)
    
    @staticmethod
    def font_size(size_key: str = 'base') -> float:
        """Tipografía responsiva UNIFICADA"""
        base_sizes = {
            'xs': 10, 'sm': 12, 'base': 14, 'md': 16,
            'lg': 18, 'xl': 20, '2xl': 24, '3xl': 30, '4xl': 36,
        }
        
        base = base_sizes.get(size_key, 14)
        
        # Lógica responsiva unificada
        if Window.width <= DesignSystem.BREAKPOINTS['xs']:
            return sp(base * 0.9)
        elif Window.width <= DesignSystem.BREAKPOINTS['sm']:
            return sp(base * 0.95)
        else:
            return sp(base)
    
    @staticmethod
    def button_height(size: str = 'md') -> float:
        """Altura de botones UNIFICADA"""
        heights = {
            'sm': 40, 'md': 48, 'lg': 56
        }
        
        base = heights.get(size, 48)
        
        # Lógica responsiva unificada
        if Window.width <= DesignSystem.BREAKPOINTS['xs']:
            return dp(base * 0.85)
        elif Window.width <= DesignSystem.BREAKPOINTS['sm']:
            return dp(base * 0.95)
        else:
            return dp(base)
    
    @staticmethod
    def grid_cols(default_cols: int = 2) -> int:
        """Columnas de grid UNIFICADO"""
        if Window.width <= DesignSystem.BREAKPOINTS['xs']:
            return 1
        elif Window.width <= DesignSystem.BREAKPOINTS['sm']:
            return min(2, default_cols)
        elif Window.width <= DesignSystem.BREAKPOINTS['md']:
            return min(3, default_cols)
        else:
            return default_cols
    
    # ==================== DETECCIÓN DE PANTALLA (MANTENIDO) ====================
    
    @staticmethod
    def get_screen_type() -> str:
        """Detectar tipo de pantalla actual"""
        width = Window.width
        
        if width < 480:
            return ScreenSize.MOBILE_SMALL
        elif width < 768:
            return ScreenSize.MOBILE
        elif width < 1024:
            return ScreenSize.TABLET
        else:
            return ScreenSize.DESKTOP
    
    @staticmethod
    def is_mobile() -> bool:
        return DesignSystem.get_screen_type() in [ScreenSize.MOBILE_SMALL, ScreenSize.MOBILE]
    
    @staticmethod
    def is_tablet() -> bool:
        return DesignSystem.get_screen_type() == ScreenSize.TABLET
    
    @staticmethod
    def is_desktop() -> bool:
        return DesignSystem.get_screen_type() == ScreenSize.DESKTOP
    
    # ==================== UTILIDADES UNIFICADAS ====================
    
    @staticmethod
    def get_card_padding() -> List[float]:
        """Padding para tarjetas UNIFICADO"""
        if DesignSystem.is_mobile():
            return [dp(12), dp(12)]
        elif DesignSystem.is_tablet():
            return [dp(16), dp(16)]
        else:
            return [dp(20), dp(20)]
    
    @staticmethod
    def get_border_radius(size: str = 'md') -> List[float]:
        """Radio de bordes UNIFICADO"""
        radii = {
            'none': [0], 'sm': [dp(4)], 'md': [dp(8)],
            'lg': [dp(12)], 'xl': [dp(16)], 'full': [dp(999)]
        }
        return radii.get(size, [dp(8)])
    
    @staticmethod
    def get_elevation(level: int = 2) -> Dict:
        """Sombras UNIFICADO"""
        elevations = {
            0: {'elevation': 0}, 1: {'elevation': dp(2)},
            2: {'elevation': dp(4)}, 3: {'elevation': dp(8)},
            4: {'elevation': dp(12)}, 5: {'elevation': dp(16)},
        }
        return elevations.get(level, elevations[2])
    
    # ==================== LAYOUTS RESPONSIVOS UNIFICADOS ====================
    
    @staticmethod
    def get_popup_size() -> Tuple[float, float]:
        """Tamaño de popups UNIFICADO"""
        if DesignSystem.is_mobile():
            return (0.9, 0.85)
        elif DesignSystem.is_tablet():
            return (0.7, 0.75)
        else:
            return (0.5, 0.6)
    
    # ==================== CONFIGURACIÓN GLOBAL ====================
    
    @staticmethod
    def apply_global_styles(app):
        """Aplicar estilos globales a la app"""
        app.theme_cls.primary_palette = "DeepPurple"
        app.theme_cls.accent_palette = "Teal"
        app.theme_cls.theme_style = "Light"


# ==================== HELPER FUNCTIONS GLOBALES UNIFICADAS ====================

def ds_color(color_name: str, alpha: float = 1.0) -> Tuple:
    """Obtener color del sistema de diseño UNIFICADO"""
    color = DesignSystem.COLORS.get(color_name, DesignSystem.COLORS['gray'])
    if alpha < 1.0:
        return (*color[:3], alpha)
    return color

def ds_spacing(size: str = 'base') -> float:
    """Obtener espaciado UNIFICADO"""
    return DesignSystem.spacing(size)

def ds_font(size: str = 'base') -> float:
    """Obtener tamaño de fuente UNIFICADO"""
    return DesignSystem.font_size(size)

def ds_button_height(size: str = 'md') -> float:
    """Obtener altura de botón UNIFICADO"""
    return DesignSystem.button_height(size)

def ds_is_mobile() -> bool:
    """¿Es móvil? UNIFICADO"""
    return DesignSystem.is_mobile()

def ds_is_tablet() -> bool:
    """¿Es tablet? UNIFICADO"""
    return DesignSystem.is_tablet()

def ds_grid_cols(default_cols: int = 2) -> int:
    """Columnas para grid UNIFICADO"""
    return DesignSystem.grid_cols(default_cols)