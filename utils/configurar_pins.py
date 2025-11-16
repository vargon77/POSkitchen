# utils/configurar_pins.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import PostgreSQLService

def configurar_pins_iniciales():
    """Configurar PINs iniciales para los empleados"""
    db = PostgreSQLService()
    
    try:
        # Actualizar empleados existentes con PINs
        pins = {
            1: '123456',  # Admin
            2: '111111',  # Mesero
            3: '222222'   # Cocinero
        }
        
        for empleado_id, pin in pins.items():
            db.ejecutar_consulta(
                "UPDATE empleados SET pin_code = %s WHERE id = %s",
                (pin, empleado_id)
            )
            print(f"✅ PIN configurado para empleado {empleado_id}: {pin}")
        
        print("🎉 PINs configurados exitosamente")
        
    except Exception as e:
        print(f"❌ Error configurando PINs: {e}")

if __name__ == "__main__":
    configurar_pins_iniciales()