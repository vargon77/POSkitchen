# views/login/login_screen.py
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from components.responsive_components import ResponsiveCard, ResponsiveButton, ResponsiveLabel
from themes.responsive_design import ResponsiveDesign as RD


class LoginScreen(MDScreen):
    mensaje = StringProperty("Ingrese su PIN")
    pin_actual = StringProperty("")
    intentos = 0
    max_intentos = 3
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = None
        self.build_responsive_ui()
    
    def on_enter(self):
        """Cuando se muestra la pantalla"""
        self.inicializar_servicios()
        self.pin_actual = ""
        self.mensaje = "Ingrese su PIN"
        self.intentos = 0
    
    def inicializar_servicios(self):
        """Inicializar servicios de autenticación"""
        if not self.auth_service:
            try:
                from services.database_service import PostgreSQLService
                from services.auth_service import AuthService
                
                db = PostgreSQLService()
                self.auth_service = AuthService(db)
                print("✅ Servicios de autenticación inicializados")
            except Exception as e:
                print(f"❌ Error inicializando servicios: {e}")
    
    def agregar_digito(self, digito):
        """Agregar dígito al PIN"""
        if len(self.pin_actual) < 6:
            self.pin_actual += digito
            self.actualizar_display_pin()
    
    def build_responsive_ui(self):
        """Construir UI responsiva programáticamente"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.gridlayout import MDGridLayout
        from kivymd.uix.relativelayout import MDRelativeLayout
        
        # Layout principal
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=RD.spacing(3),
            padding=RD.spacing(4),
            adaptive_height=True
        )
        
        # Header responsivo
        header_card = ResponsiveCard()
        header_layout = MDBoxLayout(orientation='vertical', adaptive_height=True)
        
        title = ResponsiveLabel(
            text="🔐 SISTEMA POS",
            font_style='H4',
            halign='center',
            theme_text_color='Primary'
        )
        
        subtitle = ResponsiveLabel(
            text="Control de Acceso",
            font_style='Subtitle1',
            halign='center',
            theme_text_color='Secondary'
        )
        
        header_layout.add_widget(title)
        header_layout.add_widget(subtitle)
        header_card.add_widget(header_layout)
        main_layout.add_widget(header_card)
        
        # Display PIN responsivo
        pin_card = ResponsiveCard()
        pin_layout = MDBoxLayout(orientation='vertical', adaptive_height=True)
        
        self.pin_display = ResponsiveLabel(
            text="••••••",
            font_style='H3',
            halign='center',
            theme_text_color='Primary'
        )
        
        self.message_label = ResponsiveLabel(
            text=self.mensaje,
            font_style='Body1', 
            halign='center',
            theme_text_color='Secondary'
        )
        
        pin_layout.add_widget(self.pin_display)
        pin_layout.add_widget(self.message_label)
        pin_card.add_widget(pin_layout)
        main_layout.add_widget(pin_card)
        
        # Teclado numérico responsivo
        keyboard_card = ResponsiveCard()
        self.build_keyboard(keyboard_card)
        main_layout.add_widget(keyboard_card)
        
        self.add_widget(main_layout)
    
    def build_keyboard(self, parent):
        """Construir teclado numérico responsivo"""
        from kivymd.uix.gridlayout import MDGridLayout
        
        # Grid responsivo (3 columnas en móvil, 4 en tablet)
        cols = 3 if Window.width <= RD.BREAKPOINTS['sm'] else 4
        grid = MDGridLayout(cols=cols, spacing=RD.spacing(1), adaptive_height=True)
        
        # Botones numéricos
        buttons = [
            ('1', '1'), ('2', '2'), ('3', '3'),
            ('4', '4'), ('5', '5'), ('6', '6'), 
            ('7', '7'), ('8', '8'), ('9', '9'),
            ('⌫', 'back'), ('0', '0'), ('ENTRAR', 'enter')
        ]
        
        for text, action in buttons:
            btn = ResponsiveButton(
                text=text,
                size_hint_x=None,
                width=RD.spacing(12) if Window.width <= RD.BREAKPOINTS['sm'] else RD.spacing(15)
            )
            
            if action == 'enter':
                btn.md_bg_color = self.theme_cls.primary_color
            elif action == 'back':
                btn.md_bg_color = self.theme_cls.error_color
            else:
                btn.md_bg_color = self.theme_cls.secondary_color
                
            btn.bind(on_press=lambda instance, act=action: self.on_key_press(act))
            grid.add_widget(btn)
        
        parent.add_widget(grid)
    
    def on_key_press(self, action):
        """Manejar pulsación de teclas"""
        if action == 'back':
            self.eliminar_digito()
        elif action == 'enter':
            self.realizar_login()
        elif len(self.pin_actual) < 6:
            self.pin_actual += action
            self.actualizar_display_pin()
    
    def actualizar_display_pin(self):
        """Actualizar display del PIN"""
        display = "•" * len(self.pin_actual)
        self.pin_display.text = display
    
    def eliminar_digito(self):
        """Eliminar último dígito"""
        if self.pin_actual:
            self.pin_actual = self.pin_actual[:-1]
            self.actualizar_display_pin()
    
    def realizar_login(self):
        if len(self.pin_actual) != 6:
            self.mostrar_error("El PIN debe tener 6 dígitos")
            return
        
        if not self.auth_service:
            self.mostrar_error("Error del sistema")
            return
        
        success, usuario = self.auth_service.login(self.pin_actual)
        
        if success:
            self.login_exitoso(usuario)
        else:
            self.mostrar_error("PIN incorrecto")
    
    def login_exitoso(self, usuario):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.usuario_actual = usuario
        app.auth_service = self.auth_service
        
        self.manager.current = "menu"
        self.mostrar_mensaje_bienvenida(usuario)
    
    def mostrar_error(self, mensaje):
        self.mensaje = mensaje
        self.message_label.theme_text_color = 'Error'
        Clock.schedule_once(lambda dt: self.limpiar_mensaje(), 3)
    
    def limpiar_mensaje(self):
        self.mensaje = "Ingrese su PIN"
        self.message_label.theme_text_color = 'Secondary'
    
    def mostrar_mensaje_bienvenida(self, usuario):
        from kivymd.uix.dialog import MDDialog
    
    def bloquear_login(self):
        """Bloquear login temporalmente"""
        self.mensaje = "Sistema bloqueado temporalmente"
        if hasattr(self, 'ids'):
            # Deshabilitar teclado
            for i in range(10):
                if f'btn_{i}' in self.ids:
                    self.ids[f'btn_{i}'].disabled = True
            if 'btn_borrar' in self.ids:
                self.ids.btn_borrar.disabled = True
            if 'btn_entrar' in self.ids:
                self.ids.btn_entrar.disabled = True
        
        # Desbloquear después de 30 segundos
        Clock.schedule_once(lambda dt: self.desbloquear_login(), 30)
    
    def desbloquear_login(self):
        """Desbloquear login"""
        self.mensaje = "Ingrese su PIN"
        self.pin_actual = ""
        self.intentos = 0
        self.actualizar_display_pin()
        
        if hasattr(self, 'ids'):
            # Habilitar teclado
            for i in range(10):
                if f'btn_{i}' in self.ids:
                    self.ids[f'btn_{i}'].disabled = False
            if 'btn_borrar' in self.ids:
                self.ids.btn_borrar.disabled = False
            if 'btn_entrar' in self.ids:
                self.ids.btn_entrar.disabled = False
    
    def mostrar_popup_mensaje(self, mensaje):
        """Mostrar mensaje en popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(
            text=mensaje,
            font_size='16sp',
            halign='center'
        ))
        
        btn_ok = Button(
            text='CONTINUAR',
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.6, 1, 1)
        )
        
        content.add_widget(btn_ok)
        
        popup = Popup(
            title='Bienvenido',
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()