# setup_database.py
import psycopg2
from psycopg2 import sql

def crear_base_datos():
    try:
        # Conectar a postgres por defecto
        conn = psycopg2.connect(
            host="localhost",
            database="pos_system", 
            user="postgres",
            password="qwerty",
            port="5432"
        )
        conn.autocommit = True  # Necesario para crear DB
        
        cur = conn.cursor()
        
        # Verificar si la base de datos ya existe
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'pos_system'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('pos_system')
            ))
            print("✅ Base de datos 'pos_system' creada")
        else:
            print("✅ Base de datos 'pos_system' ya existe")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creando base de datos: {e}")

if __name__ == "__main__":
    crear_base_datos()