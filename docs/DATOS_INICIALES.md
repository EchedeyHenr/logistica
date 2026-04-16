# 📊 Datos Iniciales del Sistema Logístico

## 🎯 Introducción

El sistema incluye datos iniciales predefinidos para facilitar las pruebas, demostraciones y desarrollo. Estos datos se cargan automáticamente al iniciar la aplicación y proporcionan un entorno listo para usar con centros, rutas y envíos de ejemplo.

---

## 📦 Datos Precargados

### Centros Logísticos Iniciales
| ID | Nombre | Ubicación | Descripción |
|----|--------|-----------|-------------|
| `MAD16` | Madrid Centro | Calle inventada 16 | Centro principal en Madrid |
| `BCN03` | Barcelona Centro | Carrer inventat 03 | Centro principal en Barcelona |
| `LPA06` | Las Palmas de Gran Canaria | Calle León y Castillo 06 | Centro en Canarias |

### Rutas de Transporte Iniciales
| ID de Ruta | Origen | Destino | Estado | Descripción |
|------------|--------|---------|--------|-------------|
| `MAD16-BCN03-STD-001` | `MAD16` | `BCN03` | Activa | Ruta estándar Madrid-Barcelona |
| `MAD16-BCN03-EXP-006` | `MAD16` | `BCN03` | Activa | Ruta express Madrid-Barcelona |
| `MAD16-LPA06-STD-003` | `MAD16` | `LPA06` | Activa | Ruta estándar Madrid-Canarias |
| `MAD16-LPA06-EXP-009` | `MAD16` | `LPA06` | Activa | Ruta express Madrid-Canarias |

### Envíos Iniciales
| Código | Remitente | Destinatario | Tipo | Prioridad | Estado | Ruta Asignada |
|--------|-----------|--------------|------|-----------|--------|---------------|
| `ABC123` | Amazon | Juan Pérez | Standard | 1 | REGISTERED | Ninguna |
| `EXP456` | Zara | María López | Standard | 2 | REGISTERED | Ninguna |
| `URG789` | Apple | Carlos Gómez | Express | 3 | REGISTERED | Ninguna |
| `ALB882` | Alibaba | Victor Aldama | Standard | 1 | REGISTERED | Ninguna |
| `SHN114` | Shein | Atteneri López | Fragile | 2 | REGISTERED | Ninguna |

---

## 🛠️ Modificación de Datos Iniciales

### Ubicación del Archivo
Los datos iniciales se definen en: `infrastructure/seed_data.py`

### Estructura del Archivo
```python
def seed_repository(use_sqlite=True):
    # 0. Instanciación DB si es necesario (Fase 04)
    if use_sqlite:
        import subprocess, os
        # Si logistica.db no existe lanza el script autónomo de inicialización DDL y seed:
        if not os.path.exists("logistica.db"):
            subprocess.run(["python", "crear_bd.py"])
        # Retorna implementaciones SQL
        return {"shipments": ShipmentRepositorySQLite(), ...}

    # 1. Crear repositorios (Modo Memoria)
    shipment_repo = ShipmentRepositoryMemory()
    center_repo = CenterRepositoryMemory()
    route_repo = RouteRepositoryMemory()
    
    # 2. Crear centros
    center_madrid = Center("MAD16", "Madrid Centro", "Calle inventada 16")
    center_barcelona = Center("BCN03", "Barcelona Centro", "Carrer inventat 03")
    center_gran_canaria = Center("LPA06", "Las Palmas de Gran Canaria", 
                                         "Calle León y Castillo 06")
    
    # 3. Crear rutas
    route_01 = Route("MAD16-BCN03-STD-001", center_madrid, center_barcelona)
    route_express = Route("MAD16-BCN03-EXP-006", center_madrid, center_barcelona)
    # ... más rutas
    
    # 4. Crear envíos
    envio1 = Shipment("ABC123", "Amazon", "Juan Pérez", 1)
    envio2 = Shipment("EXP456", "Zara", "María López", 2)
    envio3 = ExpressShipment("URG789", "Apple", "Carlos Gómez")
    # ... más envíos
    
    # 5. Retornar diccionario con repositorios
    return {
        "shipments": shipment_repo,
        "routes": route_repo,
        "centers": center_repo
    }
```

## 🔧 Personalización de Datos

### 1. Agregar Nuevo Centro
```python
# En seed_data.py, después de los centros existentes
center_valencia = Center("VAL-01", "Valencia Norte", "Avenida del Puerto 45")
center_repo.add(center_valencia)
```

### 2. Agregar Nueva Ruta
```python
# Crear ruta entre centros existentes
route_valencia_barcelona = Route("VAL-BCN-01", center_valencia, center_barcelona)
route_repo.add(route_valencia_barcelona)
```

### 3. Agregar Nuevo Envío
```python
# Envío estándar
nuevo_envio = Shipment("NEW001", "Nike", "Ana García", priority=2)
shipment_repo.add(nuevo_envio)

# Envío frágil
nuevo_fragil = FragileShipment("FRAG001", "Porcelanas S.A.", "Luis Martínez", priority=2)
shipment_repo.add(nuevo_fragil)

# Envío express
nuevo_express = ExpressShipment("EXP001", "DHL Express", "Sofía Rodríguez")
shipment_repo.add(nuevo_express)
```

### 4. Asignar Envíos a Rutas en Inicialización
```python
# Asignar envío existente a ruta existente
envio1 = shipment_repo.get_by_tracking_code("ABC123")
route_01 = route_repo.get_by_route_id("MAD16-BCN03-STD-001")
route_01.add_shipment(envio1)
envio1.assign_route("MAD16-BCN03-STD-001")
```

## 🧪 Datos para Casos de Prueba Específicos

### Caso 1: Prueba de Prioridades
```python
# Envíos con diferentes prioridades para testing
test_priorities = [
    Shipment("PRIO1", "Test", "User1", 1),  # Prioridad baja
    Shipment("PRIO2", "Test", "User2", 2),  # Prioridad media  
    Shipment("PRIO3", "Test", "User3", 3),  # Prioridad alta
]
for envio in test_priorities:
    shipment_repo.add(envio)
```

### Caso 2: Prueba de Estados
```python
# Envíos en diferentes estados
envio_registered = Shipment("STAT1", "Test", "User", 1)
envio_registered.update_status("REGISTERED")

envio_transit = Shipment("STAT2", "Test", "User", 2)
envio_transit.update_status("IN_TRANSIT")

envio_delivered = Shipment("STAT3", "Test", "User", 3)
envio_delivered.update_status("DELIVERED")
```

### Caso 3: Prueba de Rutas Complejas
```python
# Red más compleja para testing
centers = [
    Center("NORTH", "Norte", "Ciudad Norte"),
    Center("SOUTH", "Sur", "Ciudad Sur"),
    Center("EAST", "Este", "Ciudad Este"),
    Center("WEST", "Oeste", "Ciudad Oeste"),
]

routes = [
    Route("N-S", centers[0], centers[1]),
    Route("S-E", centers[1], centers[2]),
    Route("E-W", centers[2], centers[3]),
    Route("W-N", centers[3], centers[0]),
]
```

## 🔄 Reinicio de Datos

### Durante Desarrollo
Si usas las versiones en memoria (`use_sqlite=False`), los datos se reinician cada vez.
Con el uso de SQLite (Fase 04 en adelante), los datos son **persistentes** en `logistica.db`. Para un reinicio completo (Factory Reset) borrar físicamente el archivo `logistica.db` antes de:
```bash
python -m logistica.presentation.menu
```

## 📊 Estadísticas de Datos Iniciales

### Conteo Actual
| Entidad | Cantidad | Notas |
| :--- | :---: | :--- |
| **Centros** | 3 | Madrid, Barcelona, Gran Canaria |
| **Rutas** | 4 | 2 normales + 2 express |
| **Envíos** | 5 | 3 estándar + 1 frágil + 1 express |
| **Envíos por Tipo** | 5 | Standard: 3, Fragile: 1, Express: 1 |
| **Prioridades** | 5 | Prioridad 1: 2 envíos, 2: 2 envíos, 3: 1 envío |
| **Estados** | Todos | REGISTERED (Listos para procesar) |

### Relaciones Iniciales
* **Ningún envío asignado a ruta**: Todos listos para asignación
* **Todas las rutas activas**: Pueden recibir envíos
* **Centros balanceados**: Cada centro aparece en múltiples rutas
* **Tipos variados**: Ejemplos de todos los tipos de envío

## 🎯 Escenarios Preconfigurados

### Escenario 1: Demostración Básica
```
1. Listar envíos (opción 5) - Ver 5 envíos
2. Listar centros (opción 8) - Ver 3 centros
3. Listar rutas (opción 11) - Ver 4 rutas
4. Asignar ABC123 a MAD16-BCN03-STD-001 (opción 12)
5. Despachar ruta MAD16-BCN03-STD-001 (opción 14)
6. Completar ruta MAD16-BCN03-STD-001 (opción 15)
7. Ver detalles de ABC123 (opción 6) - Ver entregado
```

### Escenario 2: Gestión de Prioridades
```
1. Ver detalles de SHN114 (opción 6) - Frágil, prioridad 2
2. Aumentar prioridad (opción 3) - Llega a 3
3. Intentar disminuir (opción 4) - Error (no puede bajar de 2)
4. Ver detalles de URG789 (opción 6) - Express, prioridad 3
5. Intentar aumentar (opción 3) - Error (ya es máxima)
```

### Escenario 3: Validación de Reglas
```
1. Crear envío frágil con prioridad 1 (opción 1)
   - Error: "Un envío frágil no puede tener prioridad inferior a 2"
2. Crear ruta con mismo origen/destino (opción 10)
   - Error: "El centro de origen y destino no pueden ser el mismo"
3. Asignar envío a ruta completada
   - Error: "La ruta no está activa"
```

## ⚠️ Consideraciones Importantes

### 1. IDs Case-Insensitive
Todos los identificadores (códigos de envío, IDs de centro/ruta) se normalizan a minúsculas internamente:
```python
# "ABC123" y "abc123" son el mismo envío
# "MAD16" y "mad16" son el mismo centro
```

### 2. Persistencia Entre Ejecuciones
```python
# Por defecto ahora usamos persistencia fuerte (use_sqlite=True) 
# Todo avance quedará guardado para tu próxima ejecución en 'logistica.db'.
```

### 3. Thread Safety
```python
# Los datos no son thread-safe en la implementación actual
# Uso en entornos multi-hilo requiere sincronización adicional
```

### 4. Orden de Creación
El orden en seed_data.py importa:
1. Primero centros (las rutas los necesitan)
2. Luego rutas (necesitan centros ya creados)
3. Finalmente envíos (pueden existir independientemente)

## 📝 Mantenimiento de Datos Iniciales

### Cuándo Actualizar
1. **Nuevas funcionalidades**: Agregar datos que las ejemplifiquen 
2. **Corrección de bugs**: Incluir datos que reproduzcan el bug corregido 
3. **Mejoras de UX**: Datos que muestren mejor las capacidades del sistema 
4. **Nuevos tipos de prueba**: Datos para nuevos casos de test

### Buenas Prácticas
* Mantener datos representativos del dominio real 
* Incluir ejemplos de todos los tipos y estados 
* Evitar datos ofensivos o inapropiados 
* Documentar cambios en el CHANGELOG 
* Versión los datos junto con el código