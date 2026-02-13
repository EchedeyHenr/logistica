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

#### 1. Tests del Dominio - Envíos
```bash
python -m unittest logistica.test.test_shipment
```
**Propósito**: Validar reglas de negocio específicas de los envíos.

#### 2. Tests del dominio - Envios exprés y frágil
```bash
python -m unittest logistica.test.test_shipment_types
```
**Propósito**: Validar reglas de negocio específicas de los envíos exprés y frágil.

#### 3. Tests del Dominio - Centros
```bash
python -m unittest logistica.test.test_center
```
**Propósito**: Verificar la gestión operativa de centros logísticos.

#### 4. Tests del Dominio - Rutas
```bash
python -m unittest logistica.test.test_route
```
**Propósito**: Comprobar el flujo de transporte entre centros.

#### 5. Tests de Infraestructura y Servicios
```bash
python -m logistica.test_infra_and_services
```
**Propósito**: Ejecutar tests de integración de extremo a extremo.

#### 6. Tests de Lógica de Envíos
```bash
python -m logistica.test_shipment_logic
```
**Propósito**: Probar específicamente la lógica polimórfica de los envíos.

#### 7. Tests de Robustez
```bash
python -m logistica.test_robustness
```
**Propósito**: Evaluar resiliencia frente a condiciones adversas.

---

## 📋 Qué valida cada test

### test_shipment.py

**Ámbito**: Validaciones básicas y reglas de negocio de la clase `Shipment`.

**Casos Cubiertos**:
1. Creación válida e inválida
   - Campos obligatorios no vacíos
   - formato de código
   - Prioridad en rango 1-3
   - Estado inicial REGISTERED
2. Transiciones de estado permitidas y prohibidas
   - REGISTERED → IN_TRANSIT ✓
   - IN_TRANSIT → DELIVERED ✓
   - REGISTERED → DELIVERED ✗ (inválido)
3. Gestión de prioridad
   - Aumentar de 1 a 2, de 2 a 3
   - Disminuir de 3 a 2, de 2 a 1
   - Límites: no pasar de 3, no bajar de 1
4. Asignación/remoción de rutas
   - Asignar ruta a envío sin ruta
   - Remover ruta de envío con ruta
   - Error al remover si no tiene ruta
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
1. Creación válida e inválida
   - patrón de ID, nombre, ubicación obligatorios
   - Inventario inicial vacío
2. Recepción de envíos
   - Agregar envío al inventario
   - No permitir duplicados
   - Solo aceptar objetos Shipment
3. Despacho de envíos
   - Solo despachar envíos en inventario
   - Actualizar estado a IN_TRANSIT
   - Remover del inventario
4. Consultas de inventario
   - Listar envíos presentes
   - Verificar presencia por código

### test_route.py

**Ámbito**: Gestión de rutas y transporte de envíos.

**Casos Cubiertos**:
1. Creación de ruta
   - Origen y destino diferentes
   - Centros no nulos
   - Estado inicial activo
2. Asignación de envíos
   - Solo a rutas activas
   - Actualiza relación bidireccional
   - Registra en centro origen
3. Completar ruta
   - Solo rutas activas
   - Envíos a DELIVERED
   - Envíos a centro destino
   - Ruta a inactiva
4. Listado de envíos en ruta

### test_infra_and_services.py

**Ámbito**: Integración entre capas y flujos completos.

**Casos Cubiertos**:
1. Registro completo de envío
   - Creación mediante servicio
   - Persistencia en repositorio
   - Recuperación posterior
2. Asignación a ruta completa
   - Coordinación entre servicios
   - Actualización de múltiples entidades
   - Verificación de estado consistente
3. Flujo completo de entrega
   - REGISTERED → asignar → IN_TRANSIT → DELIVERED
   - Verificación en cada paso
   - Estado final correcto
4. Interacción entre servicios
   - ShipmentService + RouteService
   - RouteService + CenterService
   - Coordinación de operaciones complejas

### test_shipment_logic.py

**Ámbito**: Comportamiento polimórfico de tipos de envío.

**Casos Cubiertos**:
1. Diferenciación por tipo
   - shipment_type property específica
   - Comportamientos diferentes según tipo
   - Identificación correcta
2. Reglas específicas de Frágil
   - Prioridad mínima 2
   - No puede bajar de prioridad 2
   - Identificación como frágil
3. Reglas específicas de Express
   - Prioridad siempre 3
   - No modificable
   - Tipo EXPRESS
4. Polimorfismo en operaciones
   - Mismos métodos, comportamientos diferentes
   - Uso a través de interfaz común
   - Sustituibilidad Liskov (los objetos de una subclase deben poder reemplazar a los de 
   la clase base sin alterar el funcionamiento del programa)

### test_robustness.py

**Ámbito**: Casos extremos y manejo de errores.

**Casos Cubiertos**:
1. Datos inválidos
   - Strings vacíos
   - Valores None
   - Tipos incorrectos
2. Operaciones en estados incorrectos
   - Despachar ruta sin envíos
   - Completar ruta no activa
   - Asignar a ruta completada
3. Condiciones de carrera potenciales
   - Operaciones repetidas
   - Estados inconsistentes
   - Operaciones en paralelo (simuladas)
4. Recuperación de errores
   - Excepciones informativas
   - Estado no corrupto tras error
   - Mensajes de error claros

---

## 🧩 Cobertura de Tests por Capa

### Capa Domain

| Módulo | Tests | Cobertura |
| :--- | :---: | :--- |
| **shipment.py** | 15+ | Validaciones, estados, prioridades |
| **fragile_shipment.py** | 5+ | Reglas específicas frágiles |
| **express_shipment.py** | 3+ | Reglas específicas express |
| **center.py** | 8+ | Inventario, recepción, despacho |
| **route.py** | 10+ | Ciclo de vida, envíos, completado |

### Capa Application

| Servicio | Tests | Cobertura |
| :--- | :---: | :--- |
| **shipment_service.py** | 6+ | Registro, consulta, actualización |
| **route_service.py** | 8+ | Asignación, despacho, completado |
| **center_service.py** | 4+ | Registro, consulta, inventario |

### Capa Infrastructure

| Repositorio | Tests | Cobertura |
| :--- | :---: | :--- |
| **memory_shipment.py** | 3+ | CRUD, búsquedas case-insensitive |
| **memory_center.py** | 3+ | CRUD, búsquedas |
| **memory_route.py** | 3+ | CRUD, búsquedas |

### Tests de Integración

| Ámbito | Tests | Cobertura |
| :--- | :---: | :--- |
| **Flujos completos** | 5+ | Ciclo: REGISTERED → DELIVERED |
| **Inter-servicios** | 4+ | Coordinación entre servicios |
| **Datos reales** | 3+ | Consistencia con seed_data.py |

---

## 🔄 Pasos de Verificación Manual

### Verificación 1: Instalación Básica

```bash
# 1. Clonar repositorio
git clone https://github.com/EchedeyHenr/logistica.git
cd logistica

# 2. Ejecutar todos los tests
python -m unittest
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
   Código: VERIF1, Tipo: standard, Prioridad: 2
   ✅ Registra sin errores

3. Listar envíos nuevamente
   ✅ Ahora muestra 6 envíos, VERIF1 al final

4. Crear ruta (opción 12)
   ID: TEST-ROUTE, Origen: MAD-16, Destino: BCN-03
   ✅ Crea ruta exitosamente

5. Asignar envío a ruta (opción 2)
   Envío: VERIF1, Ruta: TEST-ROUTE
   ✅ Asigna correctamente

6. Ver detalles envío (opción 8)
   Código: VERIF1
   ✅ Muestra ruta asignada TEST-ROUTE

7. Despachar ruta (opción 15)
   Ruta: TEST-ROUTE
   ✅ Despacha correctamente

8. Ver detalles envío nuevamente
   ✅ Estado: IN_TRANSIT

9. Completar ruta (opción 16)
   Ruta: TEST-ROUTE
   ✅ Completa correctamente

10. Ver detalles envío final
    ✅ Estado: DELIVERED
    ✅ Historial: REGISTERED → IN_TRANSIT → DELIVERED
```

### Verificación 3: Validación de Errores
```bash
1. Intentar registrar envío duplicado
   Código: ABC123 (ya existe)
   ✅ Error: "Ya existe un envío con ese código"

2. Intentar crear ruta con mismo origen/destino
   Origen: MAD-16, Destino: MAD-16
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
python -m unittest logistica.test.test_shipment
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

**Solución en tests**:
```bash
def setup_method(self):
    # Crear estado fresco para cada test
    self.repo = ShipmentRepositoryMemory()
    self.service = ShipmentService(self.repo)
```

---

## ✅ Checklist de Tests

### Antes de Commit
- Todos los tests unitarios pasan
- Tests de integración pasan
- No hay tests skip/pendientes sin justificación
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
