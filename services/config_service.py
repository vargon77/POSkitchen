# services/config_service.py
import json
import os
from typing import Dict

class ConfigService:
    def __init__(self, db_service):
        self.db = db_service
        self.config_file = "config/empresa_config.json"
        self.config_default = {
            'empresa': {
                'nombre': 'MI RESTAURANTE',
                'direccion': 'Dirección no configurada',
                'telefono': '000-000-0000',
                'rfc': 'XAXX010101000',
                'leyenda_footer': '¡Gracias por su visita!'
            },
            'tickets': {
                'imprimir_automaticamente': True,
                'mostrar_preview': True,
                'fuente_ticket': 'Arial'
            },
            'seguridad': {
                'rol_cierre_pedidos': 'cajero',  # mesero, cajero, administrador
                'requiere_autorizacion_devoluciones': True
            }
        }
    
    def cargar_configuracion(self) -> Dict:
        """Cargar configuración desde archivo JSON"""
        try:
            # Crear directorio si no existe
            os.makedirs("config", exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Crear archivo con configuración por defecto
                self.guardar_configuracion(self.config_default)
                return self.config_default
                
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return self.config_default
    
    def guardar_configuracion(self, config: Dict) -> bool:
        """Guardar configuración en archivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("✅ Configuración guardada exitosamente")
            return True
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            return False
    
    def obtener_config_empresa(self) -> Dict:
        """Obtener configuración de empresa"""
        config = self.cargar_configuracion()
        return config.get('empresa', self.config_default['empresa'])
    
    def actualizar_config_empresa(self, nueva_config: Dict) -> bool:
        """Actualizar configuración de empresa"""
        config = self.cargar_configuracion()
        config['empresa'] = nueva_config
        return self.guardar_configuracion(config)