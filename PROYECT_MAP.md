# PROYECT_MAP.md - Mapa completo del proyecto
"""
🎯 SISTEMA POS - MAPA DE MÓDULOS:n
    Seleccionar Mesa → Agregar Productos → Confirmar Pedido → Enviar a Cocina


    Vista Cocina: Ver pedidos pendientes, marcar como listos

    Vista Meseros: Ver pedidos listos para entregar

CORE MODULES (100% COMPLETADOS):
✅ main.py & main.kv - Núcleo de la aplicación
✅ services/database_service.py - Conexión PostgreSQL
✅ services/pedido_service.py - Gestión de pedidos  
✅ services/cocina_service.py - Vista cocina
✅ services/auth_service.py - Login y permisos

VIEWS COMPLETADAS:
✅ views/menu/ - Pantalla principal
✅ views/pedidos/ - Toma de pedidos
✅ views/cocina/ - Vista cocina
✅ views/login/ - Sistema de autenticación

DATABASE TABLES:
✅ empleados - Usuarios y roles
✅ productos - Catálogo de productos
✅ pedidos - Cabecera de pedidos
✅ items_pedido - Detalle de pedidos
✅ historial_sesiones - Auditoría


TABLAS EXISTENTES:
empleados         ✅ ID, nombre, rol, pin_code, activo
productos         ✅ ID, nombre, precio, categoria, stock  
pedidos           ✅ ID, mesa, estado, total, empleado_id
items_pedido      ✅ pedido_id, producto_id, cantidad, precio
historial_sesiones ✅ empleado_id, accion, detalles, timestamp



PENDIENTES POR MÓDULO:
🔷 CAJA (Siguiente):
   - services/caja_service.py
   - views/caja/caja_screen.py
   - views/caja/caja_screen.kv
   - Tabla: movimientos_caja

🔷 REPORTES (Futuro):
   - services/reportes_service.py
   - views/reportes/reportes_screen.py
   - views/reportes/reportes_screen.kv

🔷 NOTIFICACIONES (Futuro):
   - services/notificaciones_service.py
   - Sistema de eventos en tiempo real
"""