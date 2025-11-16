# test_imports.py
try:
    from views.login.login_screen import LoginScreen
    from views.menu.menu_screen import MenuScreen
    from views.pedidos.toma_pedidos_screen import TomaPedidoScreen
    from views.cocina.cocina_screen import CocinaScreen
    from views.configuracion.config_screen import ConfigScreen
    from views.caja.caja_screen import CajaScreen
    from views.pedidos.cierre_cuenta_screen import CierreCuentaScreen
    
    print("✅ Todas las pantallas importadas correctamente")
    
except ImportError as e:
    print(f"❌ Error importando: {e}")