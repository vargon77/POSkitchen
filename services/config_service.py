# services/config_service.py
"""
Servicio de configuración de empresa
Almacena datos en archivo JSON local
"""
import json
import os
from typing import Dict, Optional

class ConfigService:
    """Gestión de configuración de empresa"""
    
    CONFIG_FILE = "config_empresa.json"
    
    DEFAULT_CONFIG = {
        'nombre': '',
        'direccion': '',
        'telefono': '',
        'rfc': '',
        'leyenda_footer': '¡Gracias por su preferencia!'
    }
    
    def __init__(self, db_service=None):
        """Inicializar servicio"""
        self.db = db_service
        self._ensure_config_file()
    
    def _ensure_config_file(self):
        """Asegurar que existe el archivo de configuración"""
        if not os.path.exists(self.CONFIG_FILE):
            self._save_config(self.DEFAULT_CONFIG)
            print(f"✅ Archivo de configuración creado: {self.CONFIG_FILE}")
    
    def _save_config(self, config: Dict) -> bool:
        """Guardar configuración en archivo"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    def _load_config(self) -> Dict:
        """Cargar configuración desde archivo"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return self.DEFAULT_CONFIG.copy()
    
    def obtener_config_empresa(self) -> Dict:
        """Obtener configuración actual"""
        return self._load_config()
    
    def actualizar_config_empresa(self, nueva_config: Dict) -> bool:
        """Actualizar configuración de empresa"""
        try:
            # Obtener config actual
            config_actual = self._load_config()
            
            # Actualizar solo los campos proporcionados
            for key in self.DEFAULT_CONFIG.keys():
                if key in nueva_config:
                    config_actual[key] = nueva_config[key]
            
            # Guardar
            if self._save_config(config_actual):
                print(f"✅ Configuración actualizada: {config_actual}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error actualizando configuración: {e}")
            return False
    
    def resetear_config(self) -> bool:
        """Resetear configuración a valores por defecto"""
        return self._save_config(self.DEFAULT_CONFIG.copy())