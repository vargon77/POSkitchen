# main_test.py
from kivymd.app import MDApp
from kivy.lang import Builder
from services.database_service import PostgreSQLService

KV = '''
MDScreen:
    MDBoxLayout:
        orientation: "vertical"
        padding: "20dp"
        spacing: "20dp"
        
        MDLabel:
            id: status_label
            text: "Probando conexión a PostgreSQL..."
            halign: "center"
            theme_text_color: "Primary"
            
        MDRaisedButton:
            id: test_btn
            text: "Probar Conexión"
            on_release: app.probar_conexion()
            pos_hint: {"center_x": 0.5}
'''

class TestApp(MDApp):
    def build(self):
        return Builder.load_string(KV)
    
    def on_start(self):
        # Intentar conexión automáticamente al iniciar
        self.probar_conexion()
    
    def probar_conexion(self):
        try:
            db = PostgreSQLService()
            self.root.ids.status_label.text = "✅ Conexión exitosa a PostgreSQL!"
            self.root.ids.status_label.theme_text_color = "Secondary"
        except Exception as e:
            self.root.ids.status_label.text = f"❌ Error: {str(e)}"
            self.root.ids.status_label.theme_text_color = "Error"

if __name__ == "__main__":
    TestApp().run()