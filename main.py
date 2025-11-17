# main.py - VERSIÓN FINAL PROFESIONAL
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ObjectProperty, DictProperty
from kivy.factory import Factory

# Importar pantallas
from views.login.login_screen import LoginScreen
from views.menu.menu_screen import MenuScreen
from views.pedidos.toma_pedidos_screen import TomaPedidoScreen
from views.pedidos.cierre_cuenta_screen import CierreCuentaScreen
from views.cocina.cocina_screen import CocinaScreen
from views.caja.caja_screen import CajaScreen
from views.configuracion.config_screen import ConfigScreen

# Importar widgets responsivos
from mis_widgets.responsive_widgets import ResponsiveGridLayout

# Sistema de diseño
from themes.design_system import (
    DesignSystem, ds_color, ds_spacing, dp, ds_font, 
    ds_grid_cols, ds_button_height, ds_is_mobile
)

# Hacer helpers disponibles globalmente
import builtins
builtins.ds_color = ds_color
builtins.ds_spacing = ds_spacing
builtins.ds_font = ds_font
builtins.DesignSystem = DesignSystem
builtins.ds_button_height = ds_button_height
builtins.ds_is_mobile = ds_is_mobile
builtins.ds_grid_cols = ds_grid_cols
builtins.dp = dp
builtins.sp = lambda x: dp(x)  # Agregar sp también

import os

# Registrar widgets personalizados
Factory.register('ResponsiveGridLayout', cls=ResponsiveGridLayout)

class MiAppPOS(MDApp):
    is_dark_theme = BooleanProperty(False)
    db_service = ObjectProperty(None)
    auth_service = ObjectProperty(None)
    usuario_actual = DictProperty({})
    
    def build(self):
        self.title = "Sistema POS - Profesional"
        self.icon = ""  # Puedes agregar un ícono aquí
        
        # Aplicar estilos globales del sistema de diseño
        DesignSystem.apply_global_styles(self)
        
        # Configuración del tema KivyMD
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        
        # Configurar ventana según dispositivo
        self._setup_window()
        
        # Inicializar servicios
        self._inicializar_servicios()
        
        # Cargar estilos globales
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
            Window.size = (1280, 800)
        
        # En desarrollo, simular diferentes dispositivos
        if os.environ.get('SIMULATE_DEVICE'):
            device = os.environ.get('SIMULATE_DEVICE')
            sizes = {
                'mobile': (360, 640),
                'tablet': (768, 1024),
                'desktop': (1280, 800)
            }
            Window.size = sizes.get(device, (1280, 800))
        
        # Establecer tamaño mínimo
        Window.minimum_width = 400
        Window.minimum_height = 600
        
        print(f"\n{'='*60}")
        print(f"📱 CONFIGURACIÓN DE VENTANA")
        print(f"{'='*60}")
        print(f"Tipo de pantalla: {screen_type}")
        print(f"Dimensiones: {Window.width}x{Window.height}px")
        print(f"¿Es móvil?: {DesignSystem.is_mobile()}")
        print(f"¿Es tablet?: {DesignSystem.is_tablet()}")
        print(f"¿Es desktop?: {DesignSystem.is_desktop()}")
        print(f"Columnas grid: {ds_grid_cols()}")
        print(f"{'='*60}\n")
    
    def _inicializar_servicios(self):
        """Inicializar servicios de base de datos y autenticación"""
        try:
            from services.database_service import PostgreSQLService
            from services.auth_service import AuthService
            
            self.db_service = PostgreSQLService()
            self.auth_service = AuthService(self.db_service)
            print("✅ Servicios de BD y Auth inicializados")
        except Exception as e:
            print(f"❌ Error inicializando servicios: {e}")
            import traceback
            traceback.print_exc()
    
    def load_global_styles(self):
        """Cargar estilos globales"""
        global_styles = "themes/global_styles.kv"
        if os.path.exists(global_styles):
            try:
                Builder.load_file(global_styles)
                print(f"✅ Estilos globales cargados: {global_styles}")
            except Exception as e:
                print(f"❌ ERROR cargando estilos globales: {e}")
    
    def load_kv_files(self):
        """Cargar todos los archivos .kv en orden"""
        kv_paths = [
            # Widgets personalizados primero
            "mis_widgets/product_card.kv",
            "mis_widgets/category_chip.kv",
            
            # Pantallas principales
            "views/login/login_screen.kv",
            "views/menu/menu_screen.kv",
            "views/pedidos/toma_pedidos_screen.kv",
            "views/pedidos/cierre_cuenta_screen.kv",
            "views/cocina/cocina_screen.kv",
            "views/caja/caja_screen.kv",
            "views/configuracion/config_screen.kv",
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
        print("🚀 Aplicación iniciada correctamente")
        
        # Verificar pantallas disponibles
        self._verificar_pantallas()
        
        # Iniciar en pantalla de login
        self.root.ids.screen_manager.current = "login"
    
    def _verificar_pantallas(self):
        """Verificar que todas las pantallas estén registradas"""
        try:
            sm = self.root.ids.screen_manager
            pantallas_esperadas = [
                'login', 'menu', 'pedidos', 'cierre_cuenta', 
                'cocina', 'caja', 'inventario', 'config'
            ]
            
            print("\n" + "="*60)
            print("🔍 VERIFICACIÓN DE PANTALLAS")
            print("="*60)
            
            pantallas_ok = []
            pantallas_faltantes = []
            
            for pantalla in pantallas_esperadas:
                existe = pantalla in sm.screen_names
                if existe:
                    pantallas_ok.append(pantalla)
                    print(f"   ✅ {pantalla}")
                else:
                    pantallas_faltantes.append(pantalla)
                    print(f"   ❌ {pantalla} - FALTANTE")
            
            print(f"\n📊 Resumen: {len(pantallas_ok)}/{len(pantallas_esperadas)} pantallas disponibles")
            
            if pantallas_faltantes:
                print(f"⚠️  Pantallas faltantes: {', '.join(pantallas_faltantes)}")
            
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ Error verificando pantallas: {e}")
    
    def verificar_datos_iniciales(self):
        """Verificar datos iniciales después del login"""
        try:
            from services.producto_service import ProductoService
            producto_service = ProductoService(self.db_service)
            
            productos = producto_service.obtener_todos_productos()
            if not productos:
                print("⚠️ No hay productos en la base de datos")
                self._mostrar_dialogo_info(
                    "Base de Datos",
                    "No hay productos registrados.\nContacte al administrador."
                )
            else:
                print(f"✅ {len(productos)} productos disponibles")
        except Exception as e:
            print(f"❌ Error verificando datos: {e}")
    
    def toggle_theme(self):
        """Cambiar tema claro/oscuro"""
        self.is_dark_theme = not self.is_dark_theme
        self.actualizar_tema()

    def actualizar_tema(self):
        """Actualizar tema de la aplicación"""
        self.theme_cls.theme_style = "Dark" if self.is_dark_theme else "Light"
        print(f"🎨 Tema cambiado a: {self.theme_cls.theme_style}")

    def cambiar_pantalla(self, screen_name, close_drawer=True):
        """Método centralizado para cambiar pantallas con validación"""
        try:
            # Verificar permisos si hay usuario logueado
            if self.usuario_actual and self.auth_service:
                if not self.auth_service.verificar_permiso(screen_name):
                    self.mostrar_error_permisos(screen_name)
                    return
            
            sm = self.root.ids.screen_manager
            
            # Cerrar drawer si está abierto
            if close_drawer and hasattr(self.root, 'ids') and 'nav_drawer' in self.root.ids:
                self.root.ids.nav_drawer.set_state("close")
            
            # Verificar que la pantalla existe
            if screen_name not in sm.screen_names:
                print(f"⚠️ Pantalla '{screen_name}' no existe")
                self._mostrar_dialogo_info(
                    "Error de Navegación",
                    f"La pantalla '{screen_name}' no está disponible"
                )
                return
            
            sm.current = screen_name
            print(f"📄 Navegación exitosa → {screen_name}")
            
        except Exception as e:
            print(f"❌ Error cambiando pantalla: {e}")
            import traceback
            traceback.print_exc()

    def mostrar_error_permisos(self, pantalla):
        """Mostrar error de permisos insuficientes"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton
        
        dialog = MDDialog(
            title="🚫 Acceso Denegado",
            text=f"No tienes permisos para acceder a:\n{pantalla.upper()}",
            buttons=[
                MDRaisedButton(
                    text="ENTENDIDO",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def abrir_menu(self):
        """Abrir menú lateral"""
        if not self.usuario_actual:
            print("⚠️ No hay usuario logueado - menú bloqueado")
            return
            
        try:
            if hasattr(self.root, 'ids') and 'nav_drawer' in self.root.ids:
                self.root.ids.nav_drawer.set_state("open")
                print("📂 Menú lateral abierto")
        except Exception as e:
            print(f"❌ Error abriendo menú: {e}")

    def logout_user(self):
        """Cerrar sesión del usuario"""
        if self.auth_service and self.usuario_actual:
            usuario_nombre = self.usuario_actual.get('nombre', 'Usuario')
            self.auth_service.logout()
            self.usuario_actual = {}
            
            # Cerrar drawer
            if hasattr(self.root, 'ids') and 'nav_drawer' in self.root.ids:
                self.root.ids.nav_drawer.set_state("close")
            
            # Ir a pantalla de login
            self.root.ids.screen_manager.current = "login"
            
            print(f"🚪 Sesión cerrada - {usuario_nombre}")
    
    def _mostrar_dialogo_info(self, titulo, mensaje):
        """Mostrar diálogo informativo"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDRaisedButton
        
        dialog = MDDialog(
            title=titulo,
            text=mensaje,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()


if __name__ == "__main__":
    # Opcional: simular dispositivo diferente
    # os.environ['SIMULATE_DEVICE'] = 'mobile'  # mobile, tablet, desktop
    
    try:
        app = MiAppPOS()
        app.run()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO AL INICIAR LA APLICACIÓN:")
        print(f"{e}\n")
        import traceback
        traceback.print_exc()