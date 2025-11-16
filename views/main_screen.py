from kivymd.uix.screen import MDScreen

from views.menu.menu_screen import MenuScreen

class MainScreen(MDScreen):
    def cambiar_pantalla(self, MainScreen):
        self.ids.screen_manager.current = MenuScreen
        if hasattr(self, 'ids') and 'nav_drawer' in self.ids:
            self.ids.nav_drawer.set_state("close")