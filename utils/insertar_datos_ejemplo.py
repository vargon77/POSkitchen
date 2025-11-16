# utils/insertar_datos_ejemplo.py
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ahora importar después de agregar al path
from services.database_service import PostgreSQLService

def insertar_datos_iniciales():
    db = PostgreSQLService()
    
    try:
        # 1. Verificar tablas existentes
        tablas = db.ejecutar_consulta("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        print(f"📊 Tablas encontradas: {[t['table_name'] for t in tablas]}")
        
        # 2. Insertar empleados
        empleados = [
            ('Juan Pérez', 'administrador'),
            ('María García', 'mesero'),
            ('Carlos López', 'cocinero'),
        ]
        
        for nombre, rol in empleados:
            db.ejecutar_consulta(
                "INSERT INTO empleados (nombre, rol) VALUES (%s, %s)",
                (nombre, rol)
            )
        print("✅ Empleados insertados")
        
        # 3. Insertar productos de ejemplo
        productos = [
            ('Hamburguesa Clásica', 'Carne, lechuga, tomate, queso', 120.00, 45.00, 'comida', 'hamburguesas'),
            ('Pizza Margarita', 'Salsa tomate, mozzarella, albahaca', 180.00, 60.00, 'comida', 'pizzas'),
            ('Ensalada César', 'Lechuga, pollo, crutones, aderezo', 95.00, 30.00, 'comida', 'ensaladas'),
            ('Coca-Cola', '500ml', 25.00, 8.00, 'bebidas', 'refrescos'),
            ('Agua Mineral', '500ml', 15.00, 5.00, 'bebidas', 'aguas'),
            ('Café Americano', 'Taza regular', 35.00, 10.00, 'bebidas', 'cafes'),
        ]
        
        for nombre, descripcion, precio, costo, categoria, subcategoria in productos:
            db.ejecutar_consulta(
                """INSERT INTO productos 
                (nombre, descripcion, precio, costo, categoria, subcategoria, stock) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (nombre, descripcion, precio, costo, categoria, subcategoria, 100)
            )
        print("✅ Productos insertados")
        
        # 4. Verificar datos insertados
        empleados_count = db.ejecutar_consulta("SELECT COUNT(*) as count FROM empleados")[0]['count']
        productos_count = db.ejecutar_consulta("SELECT COUNT(*) as count FROM productos")[0]['count']
        
        print(f"🎉 Datos insertados: {empleados_count} empleados, {productos_count} productos")
        
    except Exception as e:
        print(f"❌ Error insertando datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    insertar_datos_iniciales()