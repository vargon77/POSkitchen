# utils/crear_tablas_caja.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import PostgreSQLService

def crear_tablas_caja():
    """Crear tablas necesarias para el módulo de caja"""
    db = PostgreSQLService()
    
    try:
        print("🗃️ Creando tablas para módulo de caja...")
        
        # Tabla movimientos_caja
        db.ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS movimientos_caja (
                id SERIAL PRIMARY KEY,
                tipo VARCHAR(20) NOT NULL,
                empleado_id INTEGER REFERENCES empleados(id),
                pedido_id INTEGER REFERENCES pedidos(id) NULL,
                monto DECIMAL(10,2) NOT NULL,
                metodo_pago VARCHAR(20) DEFAULT 'efectivo',
                detalles TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla 'movimientos_caja' creada/verificada")
        
        # Tabla cierres_caja
        db.ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS cierres_caja (
                id SERIAL PRIMARY KEY,
                empleado_id INTEGER REFERENCES empleados(id),
                fecha DATE DEFAULT CURRENT_DATE,
                fondo_inicial DECIMAL(10,2) NOT NULL,
                total_ventas DECIMAL(10,2) DEFAULT 0,
                total_efectivo DECIMAL(10,2) DEFAULT 0,
                total_tarjeta DECIMAL(10,2) DEFAULT 0,
                total_transferencia DECIMAL(10,2) DEFAULT 0,
                total_cierre DECIMAL(10,2) DEFAULT 0,
                diferencia DECIMAL(10,2) DEFAULT 0,
                observaciones TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla 'cierres_caja' creada/verificada")
        
        print("🎉 Tablas de caja creadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

if __name__ == "__main__":
    crear_tablas_caja()