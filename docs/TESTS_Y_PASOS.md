# 🧪 Tests y Pasos de Verificación

## 🎯 Introducción

Este documento describe cómo ejecutar los tests del sistema logístico y qué valida cada conjunto de pruebas. Los tests están organizados por áreas de responsabilidad y cubren desde pruebas unitarias del dominio hasta tests de integración.

---

## 🚀 Ejecución de Tests

### Requisitos Previos
- Python 3.10+ instalado
- Estar en el directorio raíz del proyecto
- No se requieren dependencias externas

### Comandos de Ejecución

#### Ejecutar todos los tests
```bash
python -m unittest discover -s logistica/tests
```

#### Ejecutar un archivo de tests específico
```bash
python -m unittest logistica.tests.test_shipment
python -m unittest logistica.tests.test_shipment_types
python -m unittest logistica.tests.test_center
python -m unittest logistica.tests.test_route
python -m unittest logistica.tests.test_center_service
python -m unittest logistica.tests.test_shipment_service
python -m unittest logistica.tests.test_route_service
```

---

## 📋 Qué valida cada test

### test_shipment.py

**Ámbito**: Validaciones y reglas de negocio de la clase base `Shipment`.

**Casos Cubiertos**:
1. Creación válida e inválida (campos vacíos, formato de código, prioridad fuera de rango).
2. Transiciones de estado permitidas (REGISTERED → IN_TRANSIT → DELIVERED) y prohibidas.
3. Gestión de prioridad (aumentar/disminuir con límites).
4. Asignación y eliminación de rutas.
5. Consulta de historial de estados y método `is_delivered()`.

### test_shipment_types.py

**Ámbito**: Comportamiento polimórfico de `FragileShipment` y `ExpressShipment`.

**Casos Cubiertos**:
* **`FragileShipment`**:
   - Prioridad mínima 2
   - no puede disminuir por debajo de 2
   - identificación como frágil
* **`ExpressShipment`**:
   - Prioridad fija 3
   - método `increase_priority` prohibido
   - método `decrease_priority` prohibido
   - identificación como exprés
   - Al pasar prioridad a un envío express lanza error.

### test_center.py

**Ámbito**: Operaciones de centros logísticos e inventario.

**Casos Cubiertos**:
1. Creación válida e inválida (patrón de ID, campos obligatorios, ID vacío).
2. Recepción de envíos (con y sin duplicados, solo objetos Shipment).
3. Despacho de envíos (solo si existen en el centro, actualización de estado a IN_TRANSIT).
4. Consultas de inventario (has_shipment, list_shipments devuelve copia).

### test_route.py

**Ámbito**: Gestión de rutas y transporte de envíos.

**Casos Cubiertos**:
1. Creación válida e inválida (origen y destino distintos, centros no nulos, patrón de ID).
2. Asignación de envíos (solo a rutas activas, relación bidireccional, registro en centro origen).
3. Eliminación de envíos de una ruta.
4. Completar ruta (después de despachar los envíos): transferencia a centro destino, estado `DELIVERED`, ruta inactiva.
5. Operaciones sobre rutas inactivas lanzan error.

### test_center_service.py

**Ámbito**: Casos de uso relacionados con centros logísticos.

**Casos Cubiertos**:
1. Registro de centros (válido, duplicado, campos vacíos).
2. Listado y consulta de centros (existente, no existente, ID vacío).
3. Recepción de un envío en un centro (válido, centro no encontrado, envío no encontrado).
4. Despacho de un envío desde un centro (válido, envío no presente, centro no encontrado).
5. Listado de envíos en un centro.

### test_shipment_service.py

**Ámbito**: Casos de uso relacionados con envíos.

**Casos Cubiertos**:
1. Registro de envíos de todos los tipos (standard, fragile, express) con validaciones específicas.
2. Unicidad del código de seguimiento.
3. Actualización de estado (transiciones válidas e inválidas).
4. Incremento y decremento de prioridad según el tipo de envío.
5. Listado de envíos ordenado alfabéticamente.
6. Consulta de un envío por código.

### test_route_service.py

**Ámbito**: Casos de uso relacionados con rutas.

**Casos Cubiertos**:
1. Creación de rutas (válida, duplicada, centros inexistentes, mismo origen/destino, ID vacío).
2. Listado y consulta de rutas. 
3. Asignación de envíos a rutas (válida, ruta inactiva, envío ya asignado, entidades no encontradas). 
4. Eliminación de un envío de una ruta. 
5. Despacho de una ruta (válido, ya despachada, inactiva, sin envíos). 
6. Completar rutas (válido, ya inactiva, sin envíos).
7. Casos de robustez: IDs vacíos, entidades inexistentes, doble despacho.

---

## 🧩 Cobertura de Tests por Capa

### Capa Domain

| Módulo | Tests | Cobertura |
| :--- |:-----:| :--- |
| **shipment.py** |  15+  | Validaciones, estados, prioridades |
| **fragile_shipment.py** |  5+   | Reglas específicas frágiles |
| **express_shipment.py** |  4+   | Reglas específicas express |
| **center.py** |  9+   | Inventario, recepción, despacho |
| **route.py** |  10+  | Ciclo de vida, envíos, completado |

### Capa Application

| Servicio | Tests | Cobertura                                      |
| :--- |:-----:|:-----------------------------------------------|
| **shipment_service.py** |  18+  | Registro, consulta, actualización, prioridades |
| **route_service.py** |  20+  | Asignación, despacho, completado               |
| **center_service.py** |  12+  | Registro, consulta, inventario                 |

### Capa Infrastructure

- Probados indirectamente a través de los servicios con repositorios en memoria
---

## 🔄 Pasos de Verificación Manual

### Verificación 1: Instalación Básica

```bash
# 1. Clonar repositorio
git clone https://github.com/EchedeyHenr/logistica.git
cd logistica

# 2. Ejecutar todos los tests
python -m unittest discover -s logistica/tests
# ✅ Debe pasar todos los tests de la carpeta test

# 2.1 Ejecutar un test específico
python -m unittest logistica.tests.test_deseado
# ✅ Debe pasar todos los tests del archivo

# 3. Ejecutar aplicación
python -m logistica.presentation.menu
# ✅ Debe mostrar menú sin errores
```

### Verificación 2: Funcionalidad Completa
```bash
Dentro de la aplicación:

1. Listar envíos (opción 7)
   ✅ Muestra 5 envíos iniciales

2. Registrar nuevo envío (opción 1)
   Código: VRF100, Tipo: standard, Prioridad: 2
   ✅ Registra sin errores

3. Listar envíos nuevamente
   ✅ Ahora muestra 6 envíos, VRF100 al final

4. Crear ruta (opción 12)
   ID: MAD16-BCN03-STD-189, Origen: MAD16, Destino: BCN03
   ✅ Crea ruta exitosamente

5. Asignar envío a ruta (opción 2)
   Envío: VRF100, Ruta: MAD16-BCN03-STD-189
   ✅ Asigna correctamente

6. Ver detalles envío (opción 8)
   Código: VRF100
   ✅ Muestra ruta asignada MAD16-BCN03-STD-189

7. Despachar ruta (opción 15)
   Ruta: MAD16-BCN03-STD-189
   ✅ Despacha correctamente

8. Ver detalles envío nuevamente
   ✅ Estado: IN_TRANSIT

9. Completar ruta (opción 16)
   Ruta: MAD16-BCN03-STD-189
   ✅ Completa correctamente

10. Ver detalles envío final
    ✅ Estado: DELIVERED
    ✅ Historial: REGISTERED → IN_TRANSIT → DELIVERED
```

### Verificación 3: Validación de Errores
```bash
1. Intentar registrar envío duplicado
   Código: ABC123 (ya existe)
   ✅ Error: "Ya existe un envío con el código de seguimiento 'ABC123'"

2. Intentar crear ruta con mismo origen/destino
   Origen: MAD16, Destino: MAD16
   ✅ Error: "El centro de origen y destino no pueden ser el mismo"

3. Intentar transición inválida de estado
   Envío: ABC123 (REGISTERED)
   Nuevo estado: DELIVERED (debería ser IN_TRANSIT primero)
   ✅ Error: "Transición no permitida"

4. Intentar disminuir prioridad de frágil a 1
   Envío: SHN114 (frágil, prioridad 2)
   Opción: 6 (disminuir prioridad)
   ✅ Error: "La prioridad de un envío frágil no puede ser inferior a 2"
```

---

## 🐛 Depuración de Tests Fallidos

### Síntomas Comunes y Soluciones

#### 1. "ModuleNotFoundError"
`ModuleNotFoundError: No module named 'logistica'`

**Solución**:
```bash
# Ejecutar desde el directorio correcto
cd /ruta/al/proyecto  # Un nivel arriba de logistica/
python -m unittest discover -s logistica/tests
```

#### 2. "AttributeError"
`AttributeError: 'Shipment' object has no attribute 'x'`

**Solución**:
- Verificar que el test usa la versión correcta del código
- Verificar imports: `from logistica.domain.shipment import Shipment`

#### 3. Tests que pasaban pero ahora fallan
**Posibles causas**:
1. Cambios en el código sin actualizar tests
2. Dependencias entre tests (estado compartido)
3. Cambios en datos iniciales

**Solución**:
```bash
# Ejecutar tests en orden aislado
python -m unittest logistica.test.test_deseado
```

#### 4. Errores de Estado Compartido
**Síntoma**: Tests pasan individualmente pero fallan al ejecutar todos
**Causa**: Tests modifican estado global (repositorios compartidos)

**Solución en tests**: Usar setUp para crear objetos nuevos en cada test
```bash
def setUp(self):
    self.repo = ShipmentRepositoryMemory()
    self.service = ShipmentService(self.repo)
```

---

## ✅ Checklist de Tests

### Antes de Commit
- Todos los tests unitarios pasan (`python -m unittest discover`)
- Tests de integración pasan
- No hay tests saltados (`unittest.skip`) sin justificación
- Cobertura aceptable (>80% en dominio)

### Antes de Release
- Tests de sistema completos
- Tests de robustez completos
- Performance aceptable
- Documentación de tests actualizada

### Para Nueva Funcionalidad
- Tests unitarios para nuevas clases/métodos
- Tests de integración para flujos nuevos
- Tests de regresión para funcionalidad existente
- Actualizar este documento si hay nuevos tests
