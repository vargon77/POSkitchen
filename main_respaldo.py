# main.py - VERSIÓN CORREGIDA
from kivymd.app import MDApp
from kivy.lang import Builder

from views.menu.menu_screen import MenuScreen
from views.pedidos.toma_pedidos_screen import TomaPedidoScreen
from views.cocina.cocina_screen import CocinaScreen
from views.login.login_screen import LoginScreen 
from views.configuracion.config_screen import ConfigScreen
from views.caja.caja_screen import CajaScreen 
from views.pedidos.cierre_cuenta_screen import CierreCuentaScreen

from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty, DictProperty

from utils.helpers import es_movil, es_tablet, es_escritorio, obtener_tamanos_popup, obtener_altura_boton, obtener_fuente_segun_rol, obtener_columnas_grid, obtener_espaciado, obtener_elevacion_card,obtener_radio_bordes


# Hacer disponibles globalmente
#import builtins
#builtins.es_movil = es_movil
#builtins.obtener_tamanos_popup = obtener_tamanos_popup
#builtins.obtener_altura_boton = obtener_altura_boton
#builtins.obtener_fuente_titulo = obtener_fuente_titulo
#builtins.obtener_fuente_normal = obtener_fuente_normal
#import os


# Configuración inicial de ventana
Window.minimum_width = 400
Window.minimum_height = 600

class MiAppPOS(MDApp):
    is_dark_theme = BooleanProperty(False)
    db_service = ObjectProperty(None)
    auth_service = ObjectProperty(None)
    usuario_actual = DictProperty()
    is_mobile = BooleanProperty(False)
    is_tablet = BooleanProperty(False)
    is_desktop = BooleanProperty(False)
    
    def build(self):
        self.title = "Sistema POS - Expendedor"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.primary_hue = "500"
        
        # Configurar colores personalizados
        self.setup_custom_colors()
        
        # Monitorear cambios de tamaño
        Window.bind(on_resize=self.on_window_resize)
        self.update_screen_type()
        
        # Inicializar servicios
        try:
            from services.database_service import PostgreSQLService
            from services.auth_service import AuthService
            
            self.db_service = PostgreSQLService()
            self.auth_service = AuthService(self.db_service)
            print("✅ Servicios de BD y Auth inicializados")
        except Exception as e:
            print(f"❌ Error inicializando servicios: {e}")

        # Cargar archivos KV
        self.load_kv_files()

        return Builder.load_file("main.kv")

    def setup_custom_colors(self):
        """Configurar colores personalizados del sistema de diseño"""
        from themes.design_system import DesignSystem
        # Puedes personalizar más colores aquí si es necesario
        pass

    def on_window_resize(self, instance, width, height):
        """Manejar cambios de tamaño de ventana"""
        self.update_screen_type()
        
    def update_screen_type(self):
        """Actualizar tipo de pantalla según tamaño"""
        from utils.helpers import es_movil, es_tablet, es_escritorio
        self.is_mobile = es_movil()
        self.is_tablet = es_tablet()
        self.is_desktop = es_escritorio()
        print(f"🖥️  Tipo de pantalla: {'Móvil' if self.is_mobile else 'Tablet' if self.is_tablet else 'Escritorio'}")

    def load_kv_files(self):
        """Cargar todos los archivos .kv en orden"""
        kv_paths = [
            # Widgets personalizados primero
            "mis_widgets/responsive_components.kv"
            "mis_widgets/product_card.kv",
            "mis_widgets/category_chip.kv",
            
            # Pantallas después
            "views/login/login_screen.kv",
            "views/menu/menu_screen.kv", 
            "views/pedidos/toma_pedidos_screen.kv",
            "views/pedidos/cierre_cuenta_screen.kv",
            "views/cocina/cocina_screen.kv",
            "views/caja/caja_screen.kv",
            "views/configuracion/config_screen.kv",
        ]
        
        print("\n" + "="*60)
        print("📁 CARGANDO ARCHIVOS .KV")
        print("="*60)
        
        import os
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
        print(f"📱 Responsive: Móvil={self.is_mobile}, Tablet={self.is_tablet}, Desktop={self.is_desktop}")
        
        # Iniciar en pantalla de login
        self.root.ids.screen_manager.current = "login"
    
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
        self.theme_cls.theme_style = "Dark" if self.is_dark_theme else "Light"

    def actualizar_tema(self):
        self.theme_cls.theme_style = "Dark" if self.is_dark_theme else "Light"

    def mostrar_error_permisos(self, pantalla):
        """Mostrar error de permisos insuficientes"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text=f"❌ Acceso Denegado\n\nNo tienes permisos para acceder a:\n{pantalla.upper()}",
            font_size='16sp',
            halign='center'
        ))
        
        btn_ok = Button(
            text='ENTENDIDO',
            size_hint_y=None,
            height=40,
            background_color=(0.8, 0.3, 0.3, 1)
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Permisos Insuficientes',
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    def cambiar_pantalla(self, screen_name, close_drawer=True):
        """Método centralizado para cambiar pantallas"""
        try:
            if self.usuario_actual and self.auth_service:
                if not self.auth_service.verificar_permiso(screen_name):
                    self.mostrar_error_permisos(screen_name)
                    return
            
            sm = self.root.ids.screen_manager
            if close_drawer and hasattr(self.root, 'ids'):
                self.root.ids.nav_drawer.set_state("close")
            
            sm.current = screen_name
            print(f"🔄 Cambiando a pantalla: {screen_name}")
            
        except Exception as e:
            print(f"❌ Error cambiando pantalla: {e}")

    def abrir_menu(self):
        if not self.usuario_actual:
            return
        try:
            self.root.ids.nav_drawer.set_state("open")
        except Exception as e:
            print(f"❌ Error abriendo menú: {e}")

    def logout_user(self):
        if self.auth_service and self.usuario_actual:
            self.auth_service.logout()
            self.usuario_actual = {}
            self.root.ids.screen_manager.current = "login"
            print("🚪 Sesión cerrada")
        
        if hasattr(self.root, 'ids') and 'nav_drawer' in self.root.ids:
            self.root.ids.nav_drawer.set_state("close")

    def debug_permisos(self, screen_name):
        """Método temporal para debug de permisos"""
        print(f"🔍 DEBUG PERMISOS:")
        print(f"   Usuario: {self.usuario_actual}")
        print(f"   Pantalla solicitada: {screen_name}")
        
        if self.usuario_actual and self.auth_service:
            tiene_permiso = self.auth_service.verificar_permiso(screen_name)
            print(f"   ¿Tiene permiso? {tiene_permiso}")
        else:
            print("   ❌ No hay usuario o auth_service")

if __name__ == "__main__":
    MiAppPOS().run()