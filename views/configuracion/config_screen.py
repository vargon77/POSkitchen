# views/configuracion/config_screen.py
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.properties import StringProperty, DictProperty
from kivy.clock import Clock
from themes.design_system import ds_color
from kivymd.app import MDApp

class ConfigScreen(MDScreen):
    """Pantalla de configuración de empresa - SIN _widgets_dict"""
    
    # Propiedades para binding
    nombre_empresa = StringProperty("")
    direccion = StringProperty("")
    telefono = StringProperty("")
    rfc = StringProperty("")
    leyenda_footer = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_service = None
        self.dialog = None
    
    def on_enter(self):
        """Cuando se muestra la pantalla"""
        print("⚙️ Entrando a Configuración de Empresa")
        self.inicializar_servicios()
        # Delay para asegurar que los widgets estén disponibles
        Clock.schedule_once(self.cargar_configuracion, 0.1)
    
    # ========== MÉTODOS PARA TOPAPPBAR ==========
    def ir_a_menu(self, *args):
        """Volver al menú principal"""
        app = MDApp.get_running_app()
        if hasattr(app, 'cambiar_pantalla'):
            app.cambiar_pantalla("menu")
        else:
            self.manager.current = "menu"
    # ========== FIN MÉTODOS TOPAPPBAR ==========
    
    def inicializar_servicios(self):
        """Inicializar servicios de configuración"""
        if not self.config_service:
            try:
                from services.database_service import PostgreSQLService
                from services.config_service import ConfigService
                
                db = PostgreSQLService()
                self.config_service = ConfigService(db)
                print("✅ Servicios de configuración inicializados")
            except Exception as e:
                print(f"❌ Error inicializando servicios: {e}")
    
    def cargar_configuracion(self, dt=None):
        """Cargar configuración en la UI usando self.ids"""
        if not self.config_service:
            print("⚠️ Servicio de configuración no disponible")
            return
        
        try:
            config = self.config_service.obtener_config_empresa()
            print(f"📋 Configuración cargada: {config}")
            
            # Verificar que los IDs existen
            if not hasattr(self, 'ids'):
                print("⚠️ self.ids no disponible aún")
                return
            
            # Cargar datos en los widgets usando self.ids
            campos = {
                'input_nombre': 'nombre',
                'input_direccion': 'direccion',
                'input_telefono': 'telefono',
                'input_rfc': 'rfc',
                'input_leyenda': 'leyenda_footer'
            }
            
            for widget_id, config_key in campos.items():
                if widget_id in self.ids:
                    valor = config.get(config_key, '')
                    self.ids[widget_id].text = str(valor) if valor is not None else ''
                    print(f"   ✅ {widget_id} ← '{valor}'")
                else:
                    print(f"   ⚠️ {widget_id} NO encontrado en self.ids")
            
            # También actualizar propiedades para binding
            self.nombre_empresa = config.get('nombre', '')
            self.direccion = config.get('direccion', '')
            self.telefono = config.get('telefono', '')
            self.rfc = config.get('rfc', '')
            self.leyenda_footer = config.get('leyenda_footer', '')
            
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            import traceback
            traceback.print_exc()
    
    def guardar_configuracion(self):
        """Guardar configuración usando self.ids"""
        print("💾 Intentando guardar configuración...")
        
        if not self.config_service:
            self.mostrar_error("Servicio de configuración no disponible")
            return
        
        try:
            # Verificar que los IDs existen
            if not hasattr(self, 'ids'):
                self.mostrar_error("Error: widgets no disponibles")
                return
            
            # Obtener datos de los widgets usando self.ids
            nueva_config = {}
            campos = {
                'input_nombre': 'nombre',
                'input_direccion': 'direccion',
                'input_telefono': 'telefono',
                'input_rfc': 'rfc',
                'input_leyenda': 'leyenda_footer'
            }
            
            for widget_id, config_key in campos.items():
                if widget_id in self.ids:
                    nueva_config[config_key] = self.ids[widget_id].text.strip()
                else:
                    print(f"⚠️ {widget_id} no encontrado")
                    nueva_config[config_key] = ''
            
            print(f"📦 Datos a guardar: {nueva_config}")
            
            # Validaciones
            if not nueva_config['nombre']:
                self.mostrar_error("El nombre de la empresa es requerido")
                return
            
            # Guardar
            if self.config_service.actualizar_config_empresa(nueva_config):
                self.mostrar_info("✅ Configuración guardada exitosamente")
                print("🎉 Configuración guardada correctamente")
            else:
                self.mostrar_error("Error guardando configuración")
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            self.mostrar_error(error_msg)
    
    def cancelar(self):
        """Cancelar y volver al menú"""
        self.ir_a_menu()
    
    def mostrar_info(self, mensaje):
        """Mostrar mensaje informativo"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            text=mensaje,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=ds_color('primary'),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            title="Error",
            text=mensaje,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    md_bg_color=ds_color('error'),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()