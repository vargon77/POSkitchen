# mis_widgets/order_item.py 
from kivymd.uix.card import MDCard
from kivy.properties import DictProperty, ObjectProperty
from themes.design_system import ds_color, ds_spacing, ds_button_height, dp

class OrderItem(MDCard):
    item_data = DictProperty()
    pedido_screen = ObjectProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.padding = ds_spacing('sm')
        self.spacing = ds_spacing('sm')
        self.size_hint_y = None
        self.height = ds_button_height('md')
        self.elevation = 1
        self.radius = [8]
        
        self._build_ui()
    
    def _build_ui(self):
        """Construir UI del item de pedido"""
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.boxlayout import MDBoxLayout
        
        # Nombre (40%)
        lbl_nombre = MDLabel(
            text=self.item_data['nombre'],
            theme_text_color="Primary",
            size_hint_x=0.4,
            adaptive_height=True
        )
        
        # Controles de cantidad (30%)
        box_cantidad = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.3,
            spacing=ds_spacing('xs'),
            adaptive_size=True
        )
        
        btn_menos = MDIconButton(
            icon="minus",
            theme_icon_color="Custom",
            icon_color=ds_color('error'),
            size_hint_x=None,
            width=ds_button_height('sm')
        )
        
        lbl_cantidad = MDLabel(
            text=str(self.item_data['cantidad']),
            theme_text_color="Primary",
            bold=True,
            size_hint_x=None,
            width=dp(30),
            halign="center"
        )
        
        btn_mas = MDIconButton(
            icon="plus",
            theme_icon_color="Custom", 
            icon_color=ds_color('success'),
            size_hint_x=None,
            width=ds_button_height('sm')
        )
        
        box_cantidad.add_widget(btn_menos)
        box_cantidad.add_widget(lbl_cantidad)
        box_cantidad.add_widget(btn_mas)
        
        # Subtotal (30%)
        lbl_subtotal = MDLabel(
            text=f"${self.item_data['subtotal']:.2f}",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=0.3,
            halign="right"
        )
        
        # Conectar eventos
        btn_mas.bind(on_release=self._aumentar_cantidad)
        btn_menos.bind(on_release=self._disminuir_cantidad)
        
        self.add_widget(lbl_nombre)
        self.add_widget(box_cantidad)
        self.add_widget(lbl_subtotal)
    
    def _aumentar_cantidad(self, instance):
        self.item_data['cantidad'] += 1
        self._actualizar_item()
    
    def _disminuir_cantidad(self, instance):
        if self.item_data['cantidad'] > 1:
            self.item_data['cantidad'] -= 1
            self._actualizar_item()
        else:
            self.pedido_screen.eliminar_item_pedido(self.item_data)
    
    def _actualizar_item(self):
        """Actualizar item y recalcular"""
        self.item_data['subtotal'] = self.item_data['cantidad'] * self.item_data['precio']
        self.pedido_screen.actualizar_pedido_completo()