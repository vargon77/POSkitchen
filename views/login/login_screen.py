# views/login/login_screen.py
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock

class LoginScreen(MDScreen):
    mensaje = StringProperty("Ingrese su PIN")
    pin_actual = StringProperty("")
    intentos = 0
    max_intentos = 3
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = None
    
    def on_enter(self):
        """Cuando se muestra la pantalla"""
        self.inicializar_servicios()
        self.pin_actual = ""
        self.mensaje = "Ingrese su PIN"
        self.intentos = 0
        self.actualizar_display_pin()
    
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
    
    def on_pre_enter(self):
        """Configurar los botones antes de mostrar la pantalla"""
        self.configurar_botones()
    
    def configurar_botones(self):
        """Configurar eventos de los botones"""
        if not hasattr(self, 'ids'):
            return
            
        # Buscar y configurar botones numéricos
        for i in range(10):
            btn_id = f'btn_{i}'
            if btn_id in self.ids:
                self.ids[btn_id].bind(on_press=lambda instance, digit=str(i): self.agregar_digito(digit))
        
        # Configurar botones especiales si existen
        if 'btn_delete' in self.ids:
            self.ids.btn_delete.bind(on_press=lambda x: self.eliminar_digito())
        if 'btn_enter' in self.ids:
            self.ids.btn_enter.bind(on_press=lambda x: self.realizar_login())
    def agregar_digito(self, digito):
        """Agregar dígito al PIN"""
        if len(self.pin_actual) < 6:
            self.pin_actual += digito
            self.actualizar_display_pin()
    
    def eliminar_digito(self):
        """Eliminar último dígito del PIN"""
        if self.pin_actual:
            self.pin_actual = self.pin_actual[:-1]
            self.actualizar_display_pin()
    
    def actualizar_display_pin(self):
        """Actualizar display del PIN (ocultar dígitos)"""
        if hasattr(self, 'ids') and 'pin_display' in self.ids:
            display = "•" * len(self.pin_actual)
            self.ids.pin_display.text = display
    
    def realizar_login(self):
        """Realizar proceso de login"""
        if len(self.pin_actual) != 6:
            self.mostrar_error("El PIN debe tener 6 dígitos")
            return
        
        if not self.auth_service:
            self.mostrar_error("Error del sistema")
            return
        
        # Intentar login
        success, usuario = self.auth_service.login(self.pin_actual)
        
        if success:
            self.login_exitoso(usuario)
        else:
            self.intentos += 1
            intentos_restantes = self.max_intentos - self.intentos
            
            if intentos_restantes > 0:
                self.mostrar_error(f"PIN incorrecto. {intentos_restantes} intentos restantes.")
            else:
                self.mostrar_error("Demasiados intentos fallidos. Contacte al administrador.")
                self.bloquear_login()
    
    def login_exitoso(self, usuario):
        """Procesar login exitoso"""
        print(f"🎉 Login exitoso: {usuario['nombre']} ({usuario['rol']})")
        
        # Guardar usuario en la app principal
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.usuario_actual = usuario
        app.auth_service = self.auth_service
        
        # Verificar datos iniciales después del login
        if hasattr(app, 'verificar_datos_iniciales'):
            app.verificar_datos_iniciales()
        
        # Registrar acción
        self.auth_service.registrar_accion(usuario['id'], 'ACCESO_SISTEMA', f'Acceso a pantalla principal')
        
        # Ir a pantalla principal
        self.manager.current = "menu"
        
        # Mostrar mensaje de bienvenida
        self.mostrar_popup_mensaje(f"¡Bienvenido {usuario['nombre']}!\nRol: {usuario['rol'].capitalize()}")
    
    def mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        self.mensaje = mensaje
        self.pin_actual = ""
        self.actualizar_display_pin()
        
        # Programar limpieza del mensaje
        Clock.schedule_once(lambda dt: setattr(self, 'mensaje', "Ingrese su PIN"), 3)
    
    def bloquear_login(self):
        """Bloquear login temporalmente"""
        self.mensaje = "Sistema bloqueado temporalmente"
        # Desbloquear después de 30 segundos
        Clock.schedule_once(lambda dt: self.desbloquear_login(), 30)
    
    def desbloquear_login(self):
        """Desbloquear login"""
        self.mensaje = "Ingrese su PIN"
        self.pin_actual = ""
        self.intentos = 0
        self.actualizar_display_pin()
    
    def mostrar_popup_mensaje(self, mensaje):
        """Mostrar mensaje en popup"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        self.dialog = MDDialog(
            title="Bienvenido",
            text=mensaje,
            buttons=[
                MDFlatButton(
                    text="CONTINUAR",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()