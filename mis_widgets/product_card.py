# mis_widgets/product_card.py - VERSIÓN MEJORADA
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, NumericProperty
from themes.design_system import ds_color, ds_font

class ProductCard(MDCard):
    nombre = StringProperty("")
    precio = NumericProperty(0.0)
    product_id = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = "8dp"
        self.spacing = "4dp"
        self.elevation = 2
        self.radius = [12]
        self.size_hint = (None, None)
        self.size = ("160dp", "120dp")
        
        self._build_ui()
    
    def _build_ui(self):
        """Construir UI programáticamente"""
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        
        # Nombre del producto
        lbl_nombre = MDLabel(
            text=self.nombre,
            theme_text_color="Primary",
            font_style="Body2",
            adaptive_size=True,
            halign="center"
        )
        
        # Precio
        lbl_precio = MDLabel(
            text=f"${self.precio:.2f}",
            theme_text_color="Secondary", 
            font_style="H6",
            adaptive_size=True,
            halign="center",
            bold=True
        )
        
        self.add_widget(lbl_nombre)
        self.add_widget(lbl_precio)