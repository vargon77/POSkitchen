from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.properties import ObjectProperty
from mis_widgets.product_card import ProductCard

class ProductosContainer(MDBoxLayout):
    screen = ObjectProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "15dp"
        self.padding = "10dp"
        self.adaptive_height = True
    
    def on_screen(self, instance, value):
        if value:
            self.filtrar_productos("Todos")
    
    def filtrar_productos(self, categoria):
        self.clear_widgets()
        
        if categoria == "Todos":
            productos_a_mostrar = self.screen.productos
        else:
            productos_a_mostrar = [p for p in self.screen.productos if p["categoria"] == categoria]
        
        # Crear grid layout para productos
        grid = MDGridLayout(cols=2, spacing="15dp", adaptive_height=True)
        self.add_widget(grid)
        
        for producto in productos_a_mostrar:
            card = ProductCard(
                nombre=producto["nombre"],
                descripcion=producto["descripcion"],
                precio=producto["precio"],
                imagen=producto["imagen"],
                producto=producto,
                size_hint=(0.5, None),
                height="200dp"
            )
            grid.add_widget(card)