# utils/database_init.py
from services.database_service import PostgreSQLService
import os

def inicializar_base_datos():
    """Crear tablas iniciales"""
    db = PostgreSQLService()
    
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    try:
        with db.get_cursor() as cur:
            cur.execute(schema_sql)
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

def insertar_datos_iniciales():
    """Insertar productos y empleados de ejemplo"""
    db = PostgreSQLService()
    
    productos_ejemplo = [
        ('Hamburguesa Clásica', 'Carne, lechuga, tomate, queso', 120.00, 45.00, 'comida', 'hamburguesas'),
        ('Pizza Margarita', 'Salsa tomate, mozzarella, albahaca', 180.00, 60.00, 'comida', 'pizzas'),
        ('Coca-Cola', '500ml', 25.00, 8.00, 'bebidas', 'refrescos'),
    ]
    
    with db.get_cursor() as cur:
        # Insertar productos
        for producto in productos_ejemplo:
            cur.execute("""
                INSERT INTO productos (nombre, descripcion, precio, costo, categoria, subcategoria)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, producto)
        
        # Insertar empleado admin
        cur.execute("""
            INSERT INTO empleados (nombre, email, pin_code, rol)
            VALUES (%s, %s, %s, %s)
        """, ('Administrador', 'admin@pos.com', '123456', 'administrador'))
    
    print("✅ Datos iniciales insertados")

if __name__ == "__main__":
    inicializar_base_datos()
    insertar_datos_iniciales()