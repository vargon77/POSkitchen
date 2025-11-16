# views/menu/menu_screen.py - VERSIÓN CORREGIDA Y MEJORADA
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from themes.design_system import DesignSystem

class MenuScreen(MDScreen):
    usuario_nombre = StringProperty("Usuario")
    usuario_rol = StringProperty("Rol")
    ventas_hoy = NumericProperty(0)
    pedidos_activos = NumericProperty(0)
    mesas_ocupadas = NumericProperty(0)
    mesas_totales = NumericProperty(10)
    
    # Nueva propiedad para gestión de estado
    estadisticas_data = ObjectProperty({})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._estadisticas_actualizadas = False
    
    def on_enter(self):
        """Cuando la pantalla se muestra"""
        print("📱 Cargando pantalla de Menú Principal...")
        
        # Actualizar datos del usuario
        self.actualizar_datos_usuario()
        
        # Actualizar estadísticas
        if not self._estadisticas_actualizadas:
            self.actualizar_estadisticas()
            self._estadisticas_actualizadas = True
        
        # Forzar actualización de UI
        Clock.schedule_once(self._actualizar_ui, 0.1)
    
    def actualizar_datos_usuario(self):
        """Actualizar datos del usuario desde app principal"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        if app and hasattr(app, 'usuario_actual') and app.usuario_actual:
            self.usuario_nombre = app.usuario_actual.get('nombre', 'Usuario')
            self.usuario_rol = app.usuario_actual.get('rol', 'Rol')
            print(f"👤 Usuario: {self.usuario_nombre} ({self.usuario_rol})")
        else:
            print("⚠️ No hay usuario logueado")
    
    def actualizar_estadisticas(self):
        """Actualizar estadísticas (puede ser extendido para datos reales)"""
        # Simular datos por ahora - luego conectar con servicios
        self.ventas_hoy = 1250
        self.pedidos_activos = 8
        self.mesas_ocupadas = 6
        
        # Emitir señal de actualización
        self.estadisticas_data = {
            'ventas_hoy': self.ventas_hoy,
            'pedidos_activos': self.pedidos_activos,
            'mesas_ocupadas': self.mesas_ocupadas,
            'mesas_totales': self.mesas_totales
        }
        
        print(f"📊 Estadísticas actualizadas: {self.estadisticas_data}")
    
    def _actualizar_ui(self, dt):
        """Forzar actualización de la UI"""
        try:
            # Actualizar propiedades que podrían estar bindeadas
            self.property('usuario_nombre').dispatch(self)
            self.property('ventas_hoy').dispatch(self)
            print("✅ UI de menú actualizada")
        except Exception as e:
            print(f"⚠️ Error actualizando UI: {e}")
    
    def ir_a_modulo(self, modulo):
        """Navegar a módulo específico"""
        print(f"🔄 Navegando a módulo: {modulo}")
        
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        if hasattr(app, 'cambiar_pantalla'):
            app.cambiar_pantalla(modulo)
        else:
            # Fallback
            self.manager.current = modulo
        
        print(f"✅ Navegación a {modulo} completada")
    
    def on_leave(self):
        """Cuando se sale de la pantalla"""
        print("👋 Saliendo de Menú Principal")
        # Aquí puedes limpiar recursos si es necesario