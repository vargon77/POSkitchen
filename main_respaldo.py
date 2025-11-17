# main.py - VERSIÓN CORREGIDA
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from views.pedidos.toma_pedidos_screen import TomaPedidoScreen
from views.menu.menu_screen import MenuScreen
from views.cocina.cocina_screen import CocinaScreen
from views.login.login_screen import LoginScreen 
from views.configuracion.config_screen import ConfigScreen
from views.caja.caja_screen import CajaScreen 
from views.pedidos.cierre_cuenta_screen import CierreCuentaScreen
from kivy.factory import Factory 
from mis_widgets.responsive_widgets import ResponsiveGridLayout
from kivy.properties import BooleanProperty, ObjectProperty, DictProperty
from kivy.lang import Builder
# ✅ IMPORTAR SISTEMA DE DISEÑO CORREGIDO
from themes.design_system import DesignSystem, ds_color, ds_spacing, dp, ds_font, ds_grid_cols, ds_button_height,ds_is_mobile

# Hacer helper functions disponibles globalmente
import builtins
builtins.ds_color = ds_color
builtins.ds_spacing = ds_spacing
builtins.ds_font = ds_font
builtins.DesignSystem = DesignSystem
builtins.ds_button_height= ds_button_height
builtins.ds_is_mobile=ds_is_mobile
builtins.dp= dp

import os
Factory.register('ResponsiveGridLayout', cls=ResponsiveGridLayout)

class MiAppPOS(MDApp):
    is_dark_theme = BooleanProperty(False)
    db_service = ObjectProperty(None)
    auth_service = ObjectProperty(None)
    usuario_actual = DictProperty()
    
    def build(self):
        self.title = "Sistema POS - Moderno"
        
        # ✅ APLICAR ESTILOS GLOBALES DEL SISTEMA DE DISEÑO PRIMERO
        DesignSystem.apply_global_styles(self)
        
        # Configuración moderna del tema para KivyMD 1.2.0
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        # Nota: material_style "M3" no existe en KivyMD 1.2.0
        
        # Configurar ventana según dispositivo
        self._setup_window()
        
        # Inicializar servicios primero
        try:
            from services.database_service import PostgreSQLService
            from services.auth_service import AuthService
            
            self.db_service = PostgreSQLService()
            self.auth_service = AuthService(self.db_service)
            print("✅ Servicios de BD y Auth inicializados")
        except Exception as e:
            print(f"❌ Error inicializando servicios: {e}")

        # ✅ CARGAR ESTILOS GLOBALES PRIMERO
        self.load_global_styles()
        
        # Cargar archivos .kv
        self.load_kv_files()

        # Retornar interfaz principal
        return Builder.load_file("main.kv")
    
    def _setup_window(self):
        """Configurar ventana según tipo de dispositivo"""
        screen_type = DesignSystem.get_screen_type()
        
        # Configuración responsiva automática
        if DesignSystem.is_mobile():
            Window.size = (360, 640)
        elif DesignSystem.is_tablet():
            Window.size = (768, 1024)
        else:
            Window.size = (1200, 800)
        
        # En desarrollo, simular diferentes dispositivos
        if os.environ.get('SIMULATE_DEVICE'):
            device = os.environ.get('SIMULATE_DEVICE')
            if device == 'mobile':
                Window.size = (360, 640)
            elif device == 'tablet':
                Window.size = (768, 1024)
            elif device == 'desktop':
                Window.size = (1280, 720)
        
        # Establecer tamaño mínimo
        Window.minimum_width = 400
        Window.minimum_height = 600
        
        print(f"📱 Tipo de pantalla: {screen_type}")
        print(f"📏 Dimensiones: {Window.width}x{Window.height}")
    
    def load_global_styles(self):
        """Cargar estilos globales PRIMERO"""
        global_styles = "themes/global_styles.kv"
        if os.path.exists(global_styles):
            try:
                Builder.load_file(global_styles)
                print(f"✅ {global_styles}")
            except Exception as e:
                print(f"❌ ERROR en {global_styles}: {e}")
    
    def load_kv_files(self):
        """Cargar todos los archivos .kv en orden"""
        kv_paths = [
            # Widgets personalizados primero
            "mis_widgets/product_card.kv",
            "mis_widgets/category_chip.kv",
            
            # Pantallas después
            "views/login/login_screen.kv",
            "views/menu/menu_screen.kv",
            "views/pedidos/toma_pedidos_screen.kv",
            "views/pedidos/cierre_cuenta_screen.kv",
            "views/cocina/cocina_screen.kv",
            #"views/caja/caja_screen.kv",
           # "views/configuracion/config_screen.kv",
        ]
        
        print("\n" + "="*60)
        print("📂 CARGANDO ARCHIVOS .KV")
        print("="*60)
        
        for kv_file in kv_paths:
            if os.path.exists(kv_file):
                try:
                    Builder.load_file(kv_file)
                    print(f"✅ {kv_file}")
                except Exception as e:
                    print(f"❌ ERROR en {kv_file}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"⚠️  NO EXISTE: {kv_file}")
        
        print("="*60 + "\n")
    
    def on_start(self):
        """Cuando la app inicia"""
        print("🚀 Aplicación iniciada")
        
        # Mostrar información del dispositivo
        self._print_device_info()
        
        # Verificar cierre_cuenta_screen
        try:
            sm = self.root.ids.screen_manager
            if 'cierre_cuenta' in sm.screen_names:
                cierre_screen = sm.get_screen('cierre_cuenta')
                print(f"\n🔍 VERIFICACIÓN CierreCuentaScreen:")
                print(f"   - Pantalla existe: ✅")
                print(f"   - hasattr(ids): {hasattr(cierre_screen, 'ids')}")
                print(f"   - IDs count: {len(cierre_screen.ids) if hasattr(cierre_screen, 'ids') and cierre_screen.ids else 0}")
        except Exception as e:
            print(f"❌ Error verificando cierre_cuenta_screen: {e}")
        
        # Iniciar en pantalla de login
        self.root.ids.screen_manager.current = "login"
    
    def _print_device_info(self):
        """Imprimir información del dispositivo"""
        print(f"\n{'='*60}")
        print(f"📱 INFORMACIÓN DEL DISPOSITIVO")
        print(f"{'='*60}")
        print(f"Tipo: {DesignSystem.get_screen_type()}")
        print(f"Dimensiones: {Window.width}x{Window.height}px")
        print(f"¿Es móvil?: {DesignSystem.is_mobile()}")
        print(f"¿Es tablet?: {DesignSystem.is_tablet()}")
        print(f"¿Es desktop?: {DesignSystem.is_desktop()}")
        print(f"Columnas grid: {ds_grid_cols()}")
        print(f"{'='*60}\n")
    
    def verificar_datos_iniciales(self):
        """Verificar que hay empleados y productos - SOLO DESPUÉS DE LOGIN"""
        try:
            from services.producto_service import ProductoService
            producto_service = ProductoService(self.db_service)
            
            productos = producto_service.obtener_todos_productos()
            if not productos:
                print("⚠️ No hay productos en la base de datos")
            else:
                print(f"✅ {len(productos)} productos cargados")
        except Exception as e:
            print(f"❌ Error verificando datos: {e}")
    
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.actualizar_tema()

    def actualizar_tema(self):
        self.theme_cls.theme_style = "Dark" if self.is_dark_theme else "Light"

    def cambiar_pantalla(self, screen_name, close_drawer=True):
        """Método centralizado para cambiar pantallas - CON VERIFICACIÓN DE PERMISOS"""
        try:
            # Verificar permisos si hay usuario logueado
            if self.usuario_actual and self.auth_service:
                if not self.auth_service.verificar_permiso(screen_name):
                    self.mostrar_error_permisos(screen_name)
                    return
            
            sm = self.root.ids.screen_manager
            
            if close_drawer and hasattr(self.root, 'ids'):
                self.root.ids.nav_drawer.set_state("close")
            
            sm.current = screen_name
            
            print(f"📄 Cambiando a pantalla: {screen_name}")
            
        except Exception as e:
            print(f"❌ Error cambiando pantalla: {e}")

    def mostrar_error_permisos(self, pantalla):
        """Mostrar error de permisos insuficientes"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        self.dialog = MDDialog(
            title="Acceso Denegado",
            text=f"No tienes permisos para acceder a:\n{pantalla.upper()}",
            buttons=[
                MDFlatButton(
                    text="ENTENDIDO",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def abrir_menu(self):
        """Abrir menú lateral - SOLO SI HAY USUARIO LOGUEADO"""
        if not self.usuario_actual:
            return
            
        try:
            self.root.ids.nav_drawer.set_state("open")
        except Exception as e:
            print(f"❌ Error abriendo menú: {e}")

    def logout_user(self):
        """Cerrar sesión del usuario"""
        if self.auth_service and self.usuario_actual:
            self.auth_service.logout()
            self.usuario_actual = {}
            
            # Ir a pantalla de login
            self.root.ids.screen_manager.current = "login"
            print("🚪 Sesión cerrada")
        
        # Cerrar drawer si está abierto
        if hasattr(self.root, 'ids') and 'nav_drawer' in self.root.ids:
            self.root.ids.nav_drawer.set_state("close")


if __name__ == "__main__":
    # Opcional: simular dispositivo
    # os.environ['SIMULATE_DEVICE'] = 'mobile'  # mobile, tablet, desktop
    
    MiAppPOS().run()