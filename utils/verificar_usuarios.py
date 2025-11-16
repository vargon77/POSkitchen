# utils/verificar_usuarios.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import PostgreSQLService

def verificar_usuarios():
    """Verificar usuarios y roles en la base de datos"""
    db = PostgreSQLService()
    
    try:
        # Verificar empleados
        empleados = db.ejecutar_consulta("SELECT id, nombre, rol, pin_code FROM empleados")
        print("👥 EMPLEADOS EN BASE DE DATOS:")
        for emp in empleados:
            print(f"   ID: {emp['id']}, Nombre: {emp['nombre']}, Rol: {emp['rol']}, PIN: {emp['pin_code']}")
        
        # Verificar permisos del administrador
        admin = db.ejecutar_consulta("SELECT rol FROM empleados WHERE id = 1")
        if admin:
            print(f"🔑 Administrador rol: {admin[0]['rol']}")
        
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")

if __name__ == "__main__":
    verificar_usuarios()