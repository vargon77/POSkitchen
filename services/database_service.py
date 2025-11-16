# services/database_service.py (actualizado)
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class PostgreSQLService:
    def __init__(self):
        self.conn_params = {
            'host': 'localhost',
            'database': 'pos_system',
            'user': 'postgres', 
            'password': 'qwerty',  # Cambia por tu password real
            'port': '5432'
        }
        self._test_connection()
    
    def _test_connection(self):
        """Prueba básica de conexión"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            print("✅ PostgreSQLService: Conexión exitosa")
            conn.close()
        except Exception as e:
            print(f"❌ PostgreSQLService: Error - {e}")
            raise
    
  
    def ejecutar_consulta(self, query, params=None):
        """Método genérico para ejecutar queries - VERSIÓN CORREGIDA"""
        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params or ())
                    
                    # PARA INSERT CON RETURNING - manejar diferente
                    if query.strip().upper().startswith('INSERT') and 'RETURNING' in query.upper():
                        result = cur.fetchone()
                        conn.commit()
                        # Si es un diccionario (RealDictCursor), extraer el valor
                        if result and isinstance(result, dict):
                            return result['id'] if 'id' in result else result
                        else:
                            return result  # Puede ser un tuple o directamente el valor
                    
                    # PARA SELECT
                    elif query.strip().upper().startswith('SELECT'):
                        return cur.fetchall()
                    
                    # PARA UPDATE, DELETE, etc.
                    else:
                        conn.commit()
                        return cur.rowcount
                        
        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            print(f"   Query: {query}")
            print(f"   Params: {params}")
            raise

    def obtener_tablas(self):
        """Método para debug: ver qué tablas existen"""
        try:
            return self.ejecutar_consulta("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
        except Exception as e:
            print(f"Error obteniendo tablas: {e}")
            return []