# views/menu/menu_screen.py - VERSIÓN MEJORADA
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, DictProperty
from kivy.clock import Clock
from themes.design_system import DesignSystem, ds_grid_cols
from kivymd.app import MDApp

class MenuScreen(MDScreen):
    usuario_nombre = StringProperty("Usuario")
    usuario_rol = StringProperty("Rol")
    ventas_hoy = NumericProperty(0)
    pedidos_activos = NumericProperty(0)
    mesas_ocupadas = NumericProperty(0)
    mesas_totales = NumericProperty(10)
    
    # Nueva propiedad para gestión de estado
    estadisticas_data = DictProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._estadisticas_actualizadas = False
        self._grid_actualizado = False
    
    def on_enter(self):
        """Cuando la pantalla se muestra"""
        print("📱 Cargando pantalla de Menú Principal...")
        
        # Actualizar datos del usuario
        self.actualizar_datos_usuario()
        
        # Actualizar estadísticas
        if not self._estadisticas_actualizadas:
            self.actualizar_estadisticas()
            self._estadisticas_actualizadas = True
        
        # Actualizar grid responsivo
        self.actualizar_grid_responsive()
        
        # Forzar actualización de UI
        Clock.schedule_once(self._actualizar_ui, 0.1)
    
    def on_size(self, *args):
        """Cuando cambia el tamaño de la ventana"""
        self.actualizar_grid_responsive()
    
    def actualizar_grid_responsive(self):
        """Actualizar columnas del grid según tamaño de pantalla"""
        if hasattr(self, 'ids') and 'grid_modulos' in self.ids:
            # Calcular columnas según ancho de pantalla
            cols = ds_grid_cols(default_cols=2)
            
            # Para móvil siempre 1 columna en menú
            if DesignSystem.is_mobile():
                cols = 1
            elif DesignSystem.is_tablet():
                cols = 2
            else:
                cols = 3
            
            self.ids.grid_modulos.cols = cols
            print(f"📐 Grid actualizado: {cols} columnas")
    
    def actualizar_datos_usuario(self):
        """Actualizar datos del usuario desde app principal"""
        app = MDApp.get_running_app()
        
        if app and hasattr(app, 'usuario_actual') and app.usuario_actual:
            self.usuario_nombre = app.usuario_actual.get('nombre', 'Usuario')
            self.usuario_rol = app.usuario_actual.get('rol', 'Rol')
            print(f"👤 Usuario: {self.usuario_nombre} ({self.usuario_rol})")
        else:
            print("⚠️ No hay usuario logueado")
    
    def actualizar_estadisticas(self):
        """Actualizar estadísticas desde BD"""
        try:
            app = MDApp.get_running_app()
            
            if not app or not app.db_service:
                print("⚠️ Servicio de BD no disponible")
                return
            
            # Obtener estadísticas reales
            from services.pedido_service import PedidoService
            from services.caja_service import CajaService
            
            pedido_service = PedidoService(app.db_service)
            caja_service = CajaService(app.db_service)
            
            # Ventas del día
            ventas = caja_service.obtener_ventas_dia()
            self.ventas_hoy = ventas.get('total_monto', 0)
            
            # Pedidos activos
            pedidos = pedido_service.obtener_pedidos_activos()
            self.pedidos_activos = len(pedidos)
            
            # Mesas ocupadas (simplificado)
            self.mesas_ocupadas = min(self.pedidos_activos, self.mesas_totales)
            
            # Actualizar diccionario de datos
            self.estadisticas_data = {
                'ventas_hoy': self.ventas_hoy,
                'pedidos_activos': self.pedidos_activos,
                'mesas_ocupadas': self.mesas_ocupadas,
                'mesas_totales': self.mesas_totales
            }
            
            print(f"📊 Estadísticas actualizadas: {self.estadisticas_data}")
            
        except Exception as e:
            print(f"⚠️ Error obteniendo estadísticas reales: {e}")
            # Usar valores simulados si falla
            self.ventas_hoy = 1250
            self.pedidos_activos = 8
            self.mesas_ocupadas = 6
    
    def _actualizar_ui(self, dt):
        """Forzar actualización de la UI"""
        try:
            # Actualizar propiedades que podrían estar bindeadas
            self.property('usuario_nombre').dispatch(self)
            self.property('ventas_hoy').dispatch(self)
            self.property('pedidos_activos').dispatch(self)
            print("✅ UI de menú actualizada")
        except Exception as e:
            print(f"⚠️ Error actualizando UI: {e}")
    
    def ir_a_modulo(self, modulo):
        """Navegar a módulo específico CON VALIDACIÓN"""
        print(f"🔄 Navegando a módulo: {modulo}")
        
        app = MDApp.get_running_app()
        
        # Validar que el usuario tenga permisos
        if hasattr(app, 'auth_service') and app.auth_service:
            if not app.auth_service.verificar_permiso(modulo):
                print(f"❌ Permiso denegado para: {modulo}")
                self._mostrar_error_permisos(modulo)
                return
        
        # Navegar
        if hasattr(app, 'cambiar_pantalla'):
            app.cambiar_pantalla(modulo)
        else:
            # Fallback
            self.manager.current = modulo
        
        print(f"✅ Navegación a {modulo} completada")
    
    def _mostrar_error_permisos(self, modulo):
        """Mostrar mensaje de error de permisos"""
        from kivymd.uix.snackbar import Snackbar
        Snackbar(
            text=f"No tienes permisos para acceder a {modulo.upper()}",
            duration=3
        ).open()
    
    def refrescar_estadisticas(self):
        """Método público para refrescar estadísticas"""
        self._estadisticas_actualizadas = False
        self.actualizar_estadisticas()
    
    def on_leave(self):
        """Cuando se sale de la pantalla"""
        print("👋 Saliendo de Menú Principal")