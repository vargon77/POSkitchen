# utils/helpers.py (actualizado)
from kivy.core.window import Window
from kivy.metrics import dp, sp

def es_movil():
    """Determinar si es dispositivo móvil"""
    return Window.width <= dp(600)

def es_tablet():
    """Determinar si es tablet"""
    return dp(600) < Window.width <= dp(960)

def es_escritorio():
    """Determinar si es escritorio"""
    return Window.width > dp(960)

def obtener_tamanos_popup():
    """Obtener tamaño responsivo para popups - Actualizado para MD3"""
    if es_movil():
        return (0.95, 0.85)  # Más grande en móvil para mejor usabilidad
    elif es_tablet():
        return (0.75, 0.75)
    else:
        return (0.6, 0.7)

def obtener_altura_boton():
    """Altura responsiva para botones MD3"""
    if es_movil():
        return dp(44)
    elif es_tablet():
        return dp(48)
    else:
        return dp(52)

def obtener_fuente_segun_rol(rol="body"):
    """Obtener tamaño de fuente según rol de Material Design 3"""
    roles = {
        "display": sp(32), "headline": sp(24), "title": sp(20),
        "body": sp(16), "label": sp(14), "caption": sp(12)
    }
    
    base_size = roles.get(rol, sp(16))
    
    # Ajustes responsivos
    if es_movil():
        return base_size * 0.9
    elif es_tablet():
        return base_size
    else:
        return base_size * 1.1

def obtener_columnas_grid(default_cols=2):
    """Calcular columnas para grid layout - Mejorado"""
    if es_movil():
        return 1
    elif es_tablet():
        return min(2, default_cols)
    else:
        return default_cols

def obtener_espaciado(multiplier=1):
    """Espaciado responsivo - Mejorado"""
    base = dp(8)
    if es_movil():
        return base * multiplier * 0.8  # Más compacto en móvil
    elif es_tablet():
        return base * multiplier
    else:
        return base * multiplier * 1.2   # Más espaciado en desktop

def obtener_elevacion_card(base_elevation=1):
    """Elevación responsiva para cards"""
    if es_movil():
        return base_elevation
    elif es_tablet():
        return base_elevation + 1
    else:
        return base_elevation + 2

def obtener_radio_bordes():
    """Radio de bordes responsivo"""
    if es_movil():
        return dp(8)
    elif es_tablet():
        return dp(12)
    else:
        return dp(16)

# Hacer disponibles globalmente
import builtins
builtins.es_movil = es_movil
builtins.es_tablet = es_tablet
builtins.es_escritorio = es_escritorio
builtins.obtener_tamanos_popup = obtener_tamanos_popup
builtins.obtener_altura_boton = obtener_altura_boton
builtins.obtener_fuente_segun_rol = obtener_fuente_segun_rol
builtins.obtener_columnas_grid = obtener_columnas_grid
builtins.obtener_espaciado = obtener_espaciado
builtins.obtener_elevacion_card = obtener_elevacion_card
builtins.obtener_radio_bordes = obtener_radio_bordes