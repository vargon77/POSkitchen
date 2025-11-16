# services/state_manager.py
from kivy.properties import ObservableDict, ObjectProperty
from kivy.event import EventDispatcher


#class StateManager(EventDispatcher):
#    pedido_actual = ObservableDict()
#    usuario_actual = ObservableDict()
    
#    def __init__(self):
#        self.pedido_actual = {
#            'items': [],
#            'total': 0.0,
#            'mesa': None
#        }

class StateManager(EventDispatcher):
    pedido_actual = ObjectProperty(None)
    usuario_actual = ObjectProperty(None)
    config_empresa = ObjectProperty(None)
    
    def __init__(self):
        self.bind(
            pedido_actual=self._on_pedido_change,
            usuario_actual=self._on_usuario_change
        )