# services/auth_service.py - PERMISOS CORREGIDOS
import psycopg2
from typing import Dict, Optional, Tuple
from datetime import datetime

class AuthService:
    def __init__(self, db_service):
        self.db = db_service
        self.usuario_actual = None
    
    def login(self, pin_code: str) -> Tuple[bool, Optional[Dict]]:
        """Autenticar usuario por PIN"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id, nombre, rol, pin_code, activo
                FROM empleados 
                WHERE pin_code = %s AND activo = TRUE
            """, (pin_code,))
            
            resultado = cur.fetchone()
            cur.close()
            conn.close()
            
            if resultado:
                usuario = {
                    'id': resultado[0],
                    'nombre': resultado[1],
                    'rol': resultado[2],
                    'pin_code': resultado[3],
                    'activo': resultado[4]
                }
                
                self.usuario_actual = usuario
                self.registrar_accion(usuario['id'], 'LOGIN', 'Inicio de sesión exitoso')
                
                print(f"✅ Login exitoso: {usuario['nombre']} ({usuario['rol']})")
                return True, usuario
            else:
                print("❌ Login fallido: PIN incorrecto o usuario inactivo")
                return False, None
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False, None
    
    def logout(self):
        """Cerrar sesión del usuario actual"""
        if self.usuario_actual:
            self.registrar_accion(self.usuario_actual['id'], 'LOGOUT', 'Cierre de sesión')
            print(f"🚪 Logout: {self.usuario_actual['nombre']}")
            self.usuario_actual = None
    
    def registrar_accion(self, empleado_id: int, accion: str, detalles: str = ""):
        """Registrar acción en el historial"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO historial_sesiones (empleado_id, accion, detalles)
                VALUES (%s, %s, %s)
            """, (empleado_id, accion, detalles))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error registrando acción: {e}")
    
    def obtener_historial(self, limite: int = 50) -> list:
        """Obtener historial de sesiones recientes"""
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    hs.created_at,
                    e.nombre,
                    e.rol,
                    hs.accion,
                    hs.detalles
                FROM historial_sesiones hs
                JOIN empleados e ON hs.empleado_id = e.id
                ORDER BY hs.created_at DESC
                LIMIT %s
            """, (limite,))
            
            historial = []
            for row in cur.fetchall():
                historial.append({
                    'fecha': row[0],
                    'usuario': row[1],
                    'rol': row[2],
                    'accion': row[3],
                    'detalles': row[4] or ''
                })
            
            cur.close()
            conn.close()
            
            return historial
            
        except Exception as e:
            print(f"❌ Error obteniendo historial: {e}")
            return []
    
    def verificar_permiso(self, pantalla: str) -> bool:
        """Verificar permisos - VERSIÓN CORREGIDA Y MÁS FLEXIBLE"""
        if not self.usuario_actual:
            print(f"⚠️ Sin usuario actual - denegando acceso a {pantalla}")
            return False
        
        rol = self.usuario_actual['rol'].lower()
        
        # ADMINISTRADOR tiene acceso a TODO
        if rol == 'administrador' or rol == 'admin':
            print(f"✅ Admin tiene acceso total a {pantalla}")
            return True
        
        # PERMISOS POR ROL - MÁS FLEXIBLES
        permisos = {
            'mesero': [
                'menu', 'pedidos', 'cierre_cuenta', 'cocina'
            ],
            'cocinero': [
                'menu', 'cocina', 'pedidos'  # Puede ver pedidos
            ],
            'cajero': [
                'menu', 'caja', 'cierre_cuenta', 'pedidos', 'cocina', 'inventario'
            ],
            'administrador': [  # Por si acaso no detecta 'admin'
                'menu', 'pedidos', 'cierre_cuenta', 'cocina', 
                'caja', 'inventario', 'config', 'reportes'
            ]
        }
        
        pantallas_permitidas = permisos.get(rol, ['menu'])
        
        tiene_permiso = pantalla in pantallas_permitidas
        
        if tiene_permiso:
            print(f"✅ Rol '{rol}' tiene acceso a '{pantalla}'")
        else:
            print(f"🚫 Rol '{rol}' NO tiene acceso a '{pantalla}'")
            print(f"   Pantallas permitidas: {pantallas_permitidas}")
        
        return tiene_permiso
    
    def cambiar_pin(self, nuevo_pin: str) -> bool:
        """Cambiar PIN del usuario actual"""
        if not self.usuario_actual:
            return False
        
        try:
            conn = psycopg2.connect(**self.db.conn_params)
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE empleados 
                SET pin_code = %s 
                WHERE id = %s
            """, (nuevo_pin, self.usuario_actual['id']))
            
            conn.commit()
            cur.close()
            conn.close()
            
            self.registrar_accion(self.usuario_actual['id'], 'CAMBIAR_PIN', 'PIN actualizado')
            
            print(f"✅ PIN actualizado para {self.usuario_actual['nombre']}")
            return True
            
        except Exception as e:
            print(f"❌ Error cambiando PIN: {e}")
            return False
        
    def puede_cerrar_pedidos(self, usuario_actual: Dict) -> bool:
        """Verificar si el usuario puede cerrar pedidos (procesar pagos)"""
        if not usuario_actual:
            return False
        
        rol = usuario_actual.get('rol', '').lower()
        return rol in ['cajero', 'administrador', 'admin']

    def puede_imprimir_tickets(self, usuario_actual: Dict) -> bool:
        """Verificar si el usuario puede imprimir tickets"""
        if not usuario_actual:
            return False
        
        rol = usuario_actual.get('rol', '').lower()
        return rol in ['cajero', 'administrador', 'admin']