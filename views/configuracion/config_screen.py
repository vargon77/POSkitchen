# views/configuracion/config_screen.py

from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

class ConfigScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_service = None
        self._widgets_dict = {}  # CAMBIAR: usar _widgets_dict en lugar de widgets
        
        # Crear UI inmediatamente
        self.crear_ui()
    
    def crear_ui(self):
        """Crear la interfaz de usuario completamente en Python"""
        print("🛠️ Creando UI de configuración en Python...")
        
        # Limpiar cualquier widget existente
        self.clear_widgets()
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # === HEADER ===
        header_layout = BoxLayout(
            orientation='horizontal', 
            size_hint_y=None, 
            height=50,
            spacing=10
        )
        
        # Botón de regresar
        btn_back = Button(
            text='←',
            size_hint_x=None,
            width=50,
            background_color=(0.3, 0.5, 0.8, 1),
            background_normal=''
        )
        btn_back.bind(on_release=self.ir_a_menu)
        
        # Título
        lbl_title = Label(
            text='⚙️ CONFIGURACIÓN DE EMPRESA',
            font_size='20sp',
            bold=True,
            halign='left',
            color=(0.2, 0.2, 0.2, 1)
        )
        
        header_layout.add_widget(btn_back)
        header_layout.add_widget(lbl_title)
        main_layout.add_widget(header_layout)
        
        # === SCROLLVIEW PARA CONTENIDO ===
        scroll_view = ScrollView()
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint_y=None,
            padding=10
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # === CAMPOS DE CONFIGURACIÓN ===
        campos_config = [
            {
                'label': 'Nombre de la Empresa:',
                'hint': 'Ej: Mi Restaurante S.A. de C.V.',
                'id': 'input_nombre',
                'multiline': False,
                'height': 40
            },
            {
                'label': 'Dirección:',
                'hint': 'Ej: Av. Principal #123, Col. Centro',
                'id': 'input_direccion', 
                'multiline': False,
                'height': 40
            },
            {
                'label': 'Teléfono:',
                'hint': 'Ej: (555) 123-4567',
                'id': 'input_telefono',
                'multiline': False,
                'height': 40
            },
            {
                'label': 'RFC:',
                'hint': 'Ej: XAXX010101000',
                'id': 'input_rfc',
                'multiline': False,
                'height': 40
            },
            {
                'label': 'Leyenda de Pie de Página:',
                'hint': 'Ej: ¡Gracias por su preferencia!',
                'id': 'input_leyenda',
                'multiline': True,
                'height': 60
            }
        ]
        
        for campo in campos_config:
            # Contenedor del campo
            field_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=80 if campo['height'] == 40 else 100
            )
            
            # Label
            lbl = Label(
                text=campo['label'],
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=30
            )
            field_container.add_widget(lbl)
            
            # TextInput
            txt_input = TextInput(
                hint_text=campo['hint'],
                multiline=campo['multiline'],
                size_hint_y=None,
                height=campo['height'],
                write_tab=False
            )
            
            # Guardar referencia - CAMBIAR: usar _widgets_dict
            self._widgets_dict[campo['id']] = txt_input
            field_container.add_widget(txt_input)
            content_layout.add_widget(field_container)
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        
        # === BOTONES DE ACCIÓN ===
        btn_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=10
        )
        
        btn_guardar = Button(
            text='GUARDAR',
            background_color=(0.2, 0.7, 0.2, 1),
            background_normal=''
        )
        btn_guardar.bind(on_release=self.guardar_configuracion)
        
        btn_cancelar = Button(
            text='CANCELAR',
            background_color=(0.8, 0.3, 0.3, 1),
            background_normal=''
        )
        btn_cancelar.bind(on_release=self.ir_a_menu)
        
        btn_layout.add_widget(btn_guardar)
        btn_layout.add_widget(btn_cancelar)
        main_layout.add_widget(btn_layout)
        
        # Agregar todo a la pantalla
        self.add_widget(main_layout)
        print("✅ UI de configuración creada exitosamente")
        print(f"🔧 Widgets creados: {list(self._widgets_dict.keys())}")
    
    def on_enter(self):
        """Cuando se muestra la pantalla"""
        print("⚙️ Entrando a Configuración de Empresa")
        self.inicializar_servicios()
        self.cargar_configuracion()
    
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
    
    def cargar_configuracion(self):
        """Cargar configuración en la UI"""
        if not self.config_service:
            print("⚠️ Servicio de configuración no disponible")
            return
        
        config = self.config_service.obtener_config_empresa()
        print(f"📋 Configuración cargada: {config}")
        
        # Cargar datos en los widgets - CAMBIAR: usar _widgets_dict
        campos = {
            'input_nombre': 'nombre',
            'input_direccion': 'direccion', 
            'input_telefono': 'telefono',
            'input_rfc': 'rfc',
            'input_leyenda': 'leyenda_footer'
        }
        
        for widget_id, config_key in campos.items():
            if widget_id in self._widgets_dict:
                valor = config.get(config_key, '')
                self._widgets_dict[widget_id].text = str(valor) if valor is not None else ''
                print(f"   ✅ {widget_id} ← '{valor}'")
            else:
                print(f"   ❌ {widget_id} NO encontrado en widgets")
    
    def guardar_configuracion(self, instance):
        """Guardar configuración"""
        print("💾 Intentando guardar configuración...")
        
        if not self.config_service:
            self.mostrar_error("Servicio de configuración no disponible")
            return
        
        try:
            # CAMBIAR: usar _widgets_dict
            nueva_config = {
                'nombre': self._widgets_dict['input_nombre'].text.strip(),
                'direccion': self._widgets_dict['input_direccion'].text.strip(),
                'telefono': self._widgets_dict['input_telefono'].text.strip(),
                'rfc': self._widgets_dict['input_rfc'].text.strip(),
                'leyenda_footer': self._widgets_dict['input_leyenda'].text.strip()
            }
            
            print(f"📦 Datos a guardar: {nueva_config}")
            
            # Validaciones
            if not nueva_config['nombre']:
                self.mostrar_error("El nombre de la empresa es requerido")
                return
            
            if self.config_service.actualizar_config_empresa(nueva_config):
                self.mostrar_popup_mensaje("✅ Configuración guardada exitosamente")
                print("🎉 Configuración guardada en archivo")
            else:
                self.mostrar_error("Error guardando configuración")
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ {error_msg}")
            self.mostrar_error(error_msg)
    
    def ir_a_menu(self, instance):
        """Ir al menú principal"""
        self.manager.current = "menu"
    
    def mostrar_popup_mensaje(self, mensaje):
        """Mostrar mensaje en popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text=mensaje,
            font_size='16sp',
            halign='center'
        ))
        
        btn_ok = Button(
            text='OK',
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.6, 1, 1)
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Configuración',
            content=content,
            size_hint=(0.6, 0.3)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        self.mostrar_popup_mensaje(f"❌ {mensaje}")