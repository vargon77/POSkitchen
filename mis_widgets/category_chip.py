# mis_widgets/category_chip.py - VERSIÓN MEJORADA
from kivymd.uix.chip import MDChip
from kivy.properties import StringProperty, BooleanProperty
from themes.design_system import ds_color

class CategoryChip(MDChip):
    categoria = StringProperty("")
    selected = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(selected=self._update_appearance)
        self._update_appearance()
    
    def _update_appearance(self, *args):
        """Actualizar apariencia basada en estado seleccionado"""
        if self.selected:
            self.md_bg_color = ds_color('primary')
            self.text_color = ds_color('white')
        else:
            self.md_bg_color = ds_color('light')
            self.text_color = ds_color('dark')