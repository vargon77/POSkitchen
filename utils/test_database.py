# utils/test_database.py
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.database_service import PostgreSQLService
    print("✅ Import exitoso")
except ImportError as e:
    print(f"❌ Error de import: {e}")
    print("💡 Asegúrate de tener:")
    print("   - services/__init__.py")
    print("   - services/database_service.py")
    sys.exit(1)

def test_pedidos():
    """Probar la creación de pedidos"""
    db = PostgreSQLService()
    
    try:
        print("🧪 Probando creación de pedido...")
        
        # Probar INSERT con RETURNING
        result = db.ejecutar_consulta(
            "INSERT INTO pedidos (mesa, empleado_id) VALUES (%s, %s) RETURNING id",
            ("TEST", 1)
        )
        
        print(f"🔍 Resultado: {result} (tipo: {type(result)})")
        
        if isinstance(result, dict):
            print("✅ Retorna diccionario")
            print(f"   ID: {result.get('id')}")
        elif isinstance(result, int):
            print("✅ Retorna entero directamente")
            print(f"   ID: {result}")
        elif isinstance(result, tuple):
            print("✅ Retorna tupla")
            print(f"   ID: {result[0] if result else 'vacío'}")
        else:
            print(f"❌ Tipo no manejado: {type(result)}")
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pedidos()