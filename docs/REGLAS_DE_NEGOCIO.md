# 📋 Reglas de Negocio del Sistema Logístico

## 🎯 Introducción

Este documento describe las **reglas de negocio (business rules)** que gobiernan el comportamiento del sistema de gestión logística. Estas reglas están implementadas principalmente en la capa de **Domain** y garantizan la coherencia, integridad y validez de todas las operaciones.

---

## 📦 Reglas para Envíos (Shipments)

### RN-001: Unicidad del Código de Seguimiento
- **Descripción**: Cada envío debe tener un código de seguimiento único en todo el sistema
- **Ubicación**: `application/shipment_service.py` - método `register_shipment()`
- **Implementación**:
```python
if self._repo.get_by_tracking_code(tracking_code) is not None:
    raise ValueError(f"Ya existe un envío con el código '{tracking_code}'.")
```
- **Mensaje de error**:
`"Ya existe un envío con el código de seguimiento 'X'."`

### RN-002: Valores Obligatorios en Envío
- **Descripción**: Los campos básicos de un envío no pueden estar vacíos
- **Ubicación**: `domain/shipment.py` - método `__init__()`
- **Campos validados**:
  - `tracking_code`: No vacío, tipo string
  - `sender`: No vacío, tipo string
  - `recipient`: No vacío, tipo string
- **Mensaje de error**:
  - `"Ya existe un envío con el código de seguimiento 'X'."`
  - `"El remitente no puede estar vacío."`
  - `"El destinatario no puede estar vacío."`

### RN-003: Rango de Prioridades Válido
- **Descripción**: La prioridad debe ser 1, 2 o 3
- **Ubicación**: `domain/shipment.py` - método `__init__()`
- **Implementación**:
```python
if priority not in (1, 2, 3):
    raise ValueError("La prioridad debe ser 1, 2 o 3.")
```
- **Mensaje de error**:
`"La prioridad debe ser 1, 2 o 3."`

### RN-035: Formato del código de seguimiento (`tracking_code`)
- **Descripción**: El código de seguimiento de un envío debe tener 3 letras mayúsculas seguidas de 3 dígitos (ej. `ABC123`).
- **Ubicación**: `domain/shipment.py` - método `__init__()`
- **Implementación**:
```python
import re
if not re.match(r'^[A-Z]{3}\d{3}$', tracking_code):
    raise ValueError("El código de seguimiento debe tener 3 letras mayúsculas seguidas de 3 dígitos (ej. ABC123).") 
```
- **Mensaje de error**:
`El código de seguimiento debe tener 3 letras mayúsculas seguidas de 3 dígitos (ej. ABC123).`

## 🎭 Reglas Específicas por Tipo de Envío

### RN-004: Prioridad Mínima para Envíos Frágiles
- **Descripción**: Los envíos frágiles no pueden tener prioridad inferior a 2
- **Ubicación**: `domain/fragile_shipment.py` - método `__init__()`
- **Implementación**:
```python
if priority < 2:
    raise ValueError("Un envío frágil no puede tener prioridad inferior a 2.")
```
- **Mensaje de error**:
`"Un envío frágil no puede tener prioridad inferior a 2."`
- **Justificacion**: Mercancía delicada requiere manejo especial y mayor prioridad

### RN-005: Prioridad Fija para Envíos Express
- **Descripción**: Los envíos express tienen siempre prioridad 3 (máxima)
- **Ubicación**: `domain/express_shipment.py` - propiedad `priority`
- **Implementación**:
```python
@property
def priority(self):
    return 3  # Siempre devuelve 3
```
- **Comportamiento**: No se puede modificar la prioridad de un envío express
- **Mensaje de error al intentar aumentar**:
`"Un envío express ya tiene prioridad máxima."`

### RN-006: Límite Inferior para Disminuir Prioridad de Frágiles
- **Descripción**: Los envíos frágiles no pueden bajar de prioridad 2
- **Ubicación**: `domain/fragile_shipment.py` - método `decrease_priority()`
- **Implementación**:
```python
if self._priority <= 2:
    raise ValueError("La prioridad de un envío frágil no puede ser inferior a 2.")
```
- **Mensaje de error**:
`"La prioridad de un envío frágil no puede ser inferior a 2."`

## 🔄 Reglas de Transición de Estados

### RN-007: Secuencia de Estados Válida
- **Descripción**: Los envíos deben seguir una secuencia específica de estados
- **Ubicación**: `domain/shipment.py` - método `can_change_to()`
- **Transiciones permitidas**:
1. `REGISTERED` → `IN_TRANSIT`
2. `IN_TRANSIT` → `DELIVERED`
- **Implementación**:
```python
valid_transitions = {
    "REGISTERED": "IN_TRANSIT",
    "IN_TRANSIT": "DELIVERED"
}
```
- **Mensaje de error**:
`"Transición no permitida: de X a Y"`

### RN-008: Estado Inicial de Envío
- **Descripción**: Todo envío nuevo comienza en estado `REGISTERED`
- **Ubicación**: `domain/shipment.py` - método `__init__()`
- **Implementación**:
```python
self._current_status = "REGISTERED"
self._status_history = ["REGISTERED"]
```
- **Implicaciones**: No se puede crear un envío directamente en `IN_TRANSIT` o `DELIVERED`

## 🏭 Reglas para Centros Logísticos

### RN-009: Unicidad del Identificador de Centro
- **Descripción**: Cada centro debe tener un ID único (case-insensitive)
- **Ubicación**: `application/center_service.py` - método `register_center()`
- **Implementación**:
```python
center = self._center_repo.get_by_center_id(center_id)
if center is not None:
    raise ValueError(f"Ya hay registrado un centro con el ID '{center_id}'.")
```
- **Mensaje de error**:
`"Ya hay registrado un centro con el identificador 'X'."`

### RN-010: Valores Obligatorios en Centro
- **Descripción**: Todos los campos del centro son obligatorios
- **Ubicación**: `domain/center.py` - método `__init__()`
- **Campos validados**:
  - `center_id`: No vacío, tipo string
  - `name`: No vacío, tipo string
  - `location`: No vacío, tipo string
- **Mensaje de error**:
  - `"El ID del centro no puede estar vacío."`
  - `"El nombre del centro no puede estar vacío."`
  - `"La ubicación del centro no puede estar vacía."`

### RN-011: No Duplicar Envíos en un Centro
- **Descripción**: Un envío no puede estar dos veces en el mismo centro
- **Ubicación**: `domain/center.py` - método `receive_shipment()`
- **Implementación**:
```python
if self.has_shipment(shipment.tracking_code):
    raise ValueError("El envío ya se encuentra en el centro.")
```
- **Mensaje de error**:
`"El envío ya se encuentra en el centro."`

### RN-012: Solo Envíos en el Centro Pueden Despacharse
- **Descripción**: Solo se pueden despachar envíos que estén físicamente en el centro
- **Ubicación**: `domain/center.py` - método `dispatch_shipment()`
- **Implementación**:
```python
if not self.has_shipment(shipment.tracking_code):
    raise ValueError("El envío no se encuentra en el centro.")
```
- **Mensaje de error**:
`"El envío no se encuentra en el centro."`

### RN-034: Formato del identificador de centro (`center_id`)
- **Descripción**: El identificador de un centro debe tener 3 o 4 letras mayúsculas seguidas de 2 dígitos (ej. `MAD01`, `BCN02`).
- **Ubicación**: `domain/center.py` - método `__init__()`
- **Implementación**:
```python
import re
if not re.match(r'^[A-Z]{3,4}\d{2}$', center_id):
    raise ValueError("El ID del centro debe tener 3 o 4 letras mayúsculas seguidas de 2 dígitos (ej. MAD01).")
```
- **Mensaje de error**:
`"El ID del centro debe tener 3 o 4 letras mayúsculas seguidas de 2 dígitos (ej. MAD01)."`

## 🚛 Reglas para Rutas de Transporte

### RN-013: Origen y Destino Diferentes
- **Descripción**: Una ruta no puede tener el mismo centro de origen y destino
- **Ubicación**: `domain/route.py` - método `__init__()`
- **Implementación**:
```python
if origin_center == destination_center:
    raise ValueError("El centro de origen y destino no pueden ser el mismo.")
```
- **Mensaje de error**:
`"El centro de origen y destino no pueden ser el mismo."`

### RN-014: Centros Obligatorios en Ruta
- **Descripción**: Tanto origen como destino deben estar definidos
- **Ubicación**: `domain/route.py` - método `__init__()`
- **Implementación**:
```python
if origin_center is None or destination_center is None:
    raise ValueError("Los centros de origen y destino deben estar definidos.")
```
- **Mensaje de error**:
`"Los centros de origen y destino deben estar definidos."`

### RN-015: Solo Rutas Activas Aceptan Envíos
- **Descripción**: Solo se pueden añadir envíos a rutas en estado activo
- **Ubicación**: `domain/route.py` - método `add_shipment()`
- **Implementación**:
```python
if not self.is_active:
    raise ValueError("La ruta no está activa.")
```
- **Mensaje de error**:
`"La ruta no está activa."`

### RN-016: Un Envío Solo en una Ruta
- **Descripción**: Un envío no puede estar asignado a múltiples rutas simultáneamente
- **Ubicación**: `application/route_service.py` - método `assign_shipment_to_route()`
- **Implementación**:
```python
if shipment.is_assigned_to_route():
    raise ValueError(f"El envío '{tracking_code}' ya está asignado a una ruta.")
```
- **Mensaje de error**:
`"El envío 'X' ya está asignado a una ruta."`

### RN-017: Despacho Requiere Envíos en Origen
- **Descripción**: Para despachar una ruta, todos sus envíos deben estar en el centro origen
- **Ubicación**: `application/route_service.py` - método `dispatch_route()`
- **Lógica implícita**: El método `dispatch_shipment()` del centro valida la presencia

### RN-018: Completar Ruta Requiere Estar Activa
- **Descripción**: Solo rutas activas pueden completarse
- **Ubicación**: `domain/route.py` - método `complete_route()`
- **Implementación**:
```python
if not self._active:
    raise ValueError("La ruta no está activa.")
```
- **Mensaje de error**:
`"La ruta no está activa."`

### RN-036: Formato del identificador de ruta (`route_id`)
- **Descripción**:  El identificador de una ruta debe seguir el patrón `ORIGEN-DESTINO-TIPO-999`, donde:
  - `ORIGEN` y `DESTINO` son identificadores de centros válidos (según RN-034)
  - `TIPO` es uno de: `STD` (estándar), `FRG` (frágil) o `EXP` (exprés).
  - `999` es un número de tres dígitos.
- **Ubicación**: `domain/route.py` - método `__init__()`
- **Implementación**:
```python
import re
if not re.match(r'^[A-Z]{3,4}\d{2}-[A-Z]{3,4}\d{2}-(STD|FRG|EXP)-\d{3}$', route_id):
    raise ValueError("El ID de la ruta debe tener el formato ORIGEN-DESTINO-TIPO-999 (ej. MAD01-BCN02-EXP-001).")
```
- **Mensaje de error**:
`"El ID de la ruta debe tener el formato ORIGEN-DESTINO-TIPO-999 (ej. MAD01-BCN02-EXP-001)."`

## ⚙️ Reglas de Límites y Validaciones

### RN-019: Límites de Prioridad por Tipo

| Tipo de Envío | Prioridad Mínima | Prioridad Máxima | ¿Modificable? |
| :--- | :---: | :---: | :--- |
| **Standard** | 1 | 3 | Sí |
| **Fragile** | 2 | 3 | Sí (no < 2) |
| **Express** | 3 | 3 | No |

### RN-020: Validación de Aumento de Prioridad
- **Standard**: No puede pasar de 2 a 3
- **Fragile**: No puede pasar de 2 a 3 (si ya es 2, no puede aumentar)
- **Express**: Nunca puede aumentar (siempre es 3)

### RN-021: Validación de Disminución de Prioridad
- **Standard**: No puede bajar de 1
- **Fragile**: No puede bajar de 2
- **Express**: Nunca puede disminuir (siempre es 3)

## 🔍 Reglas de Consulta y Listados

### RN-022: Ordenación Alfabética de Envíos
- **Descripción**: Los listados de envíos se ordenan por código de seguimiento (case-insensitive)
- **Ubicación**: `application/shipment_service.py` - método `list_shipments()`
- **Implementación**:
```python
result.sort(key=lambda item: item[0].lower())
```

### RN-023: Case-Insensitive en Búsquedas
- **Descripción**: Todas las búsquedas por ID/código son insensibles a mayúsculas/minúsculas
- **Ubicación**: Repositorios en memoria (`infrastructure/`)
- **Implementación**:
```python
key = tracking_code.lower()  # Normaliza a minúsculas
return self._storage.get(key)
```
## 🛡️ Reglas de Integridad Referencial

### RN-024: Envío Debe Existir para Operaciones
- **Descripción**: Cualquier operación sobre un envío requiere que exista
- **Aplicación**: En todos los servicios antes de operar
- **Patrón común**:
```python
shipment = self._repo.get_by_tracking_code(tracking_code)
if shipment is None:
    raise ValueError(f"No hay ningún envío con el código '{tracking_code}'.")
```

### RN-025: Centro Debe Existir para Operaciones
- **Descripción**: Cualquier operación sobre un centro requiere que exista
- **Aplicación**: Similar a RN-024 pero para centros

### RN-026: Ruta Debe Existir para Operaciones
- **Descripción**: Cualquier operación sobre una ruta requiere que exista
- **Aplicación**: Similar a RN-024 pero para rutas

## 📊 Reglas de Estado del Sistema

### RN-027: Estados Posibles de Ruta

| Estado | Descripción | ¿Acepta nuevos envíos? | ¿Se puede despachar? |
| :--- | :--- | :---: | :---: |
| **Activa** | Ruta operativa | Sí | Sí |
| **Finalizada** | Ruta completada | No | No |

### RN-028: Estados Posibles de Envío

| Estado | Descripción | ¿Puede asignarse a ruta? | ¿Puede entregarse? |
| :--- | :--- | :---: | :---: |
| **REGISTERED** | Creado en sistema | Sí | No |
| **IN_TRANSIT** | En camino | No (ya asignado) | Sí |
| **DELIVERED** | Entregado | No | No (estado final) |

## ⚠️ Reglas de Error y Resiliencia

### RN-029: Mensajes de Error Informativos
- **Descripción**: Todos los errores deben incluir información suficiente para diagnosticar
- **Ejemplos**:
  - ❌ `"Error en la operación"`
  - ✅ `"No existe un centro con el identificador 'MAD-99'"`

### RN-030: No Silenciar Errores
- **Descripción**: Las excepciones deben propagarse hasta la capa de presentación
- - **Implementación**: No usar `try-except` que capture y silencie sin registrar

### RN-031: Validación Antes de Persistir
- **Descripción**: Todas las validaciones se hacen antes de modificar el estado
- **Patrón**: Validar → Operar → Persistir (nunca Operar → Validar → Revertir)

## 🔄 Reglas de Historial y Trazabilidad

### RN-032: Historial Completo de Estados
- **Descripción**: Todo envío mantiene registro completo de todos sus estados
- **Ubicación**: `domain/shipment.py` - atributo `_status_history`
- **Implementación**: Lista que se actualiza en cada cambio de estado
- **Garantía**: El historial es inmutable (solo lectura para consulta)

### RN-033: No Modificación de Historial
- **Descripción**: El historial de estados no puede ser modificado externamente
- **Implementación**:
```python
def get_status_history(self):
    return self._status_history.copy()  # Devuelve copia
```

## 📋 Resumen de Reglas por Entidad

### Envíos (Shipment)
1. Código único (RN-001)
2. Campos obligatorios (RN-002)
3. Prioridad 1-3 (RN-003)
4. Secuencia de estados (RN-007, RN-008)
5. Historial completo (RN-032, RN-033)

### Envíos Frágiles (FragileShipment)
1. Prioridad mínima 2 (RN-004)
2. No bajar de prioridad 2 (RN-006)

### Envíos Express (ExpressShipment)
1. Prioridad fija 3 (RN-005)
2. No modificable (RN-005)

### Centros Logísticos (Center)
1. ID único (RN-009)
2. Campos obligatorios (RN-010)
3. No duplicar envíos (RN-011)
4. Validar presencia para despacho (RN-012)

### Rutas (Route)
1. Origen ≠ destino (RN-013)
2. Centros definidos (RN-014)
3. Solo activas aceptan envíos (RN-015)
4. Un envío por ruta (RN-016)
5. Estados claros (RN-027)

## 📝 Mantenimiento de Reglas

### Cuando Agregar Nueva Regla
1. Documentar en este archivo con formato RN-XXX
2. Implementar en la capa Domain (si es posible)
3. Crear tests unitarios que la validen 
4. Actualizar mensajes de error si es necesario

### Cuando Modificar Regla Existente
1. Actualizar este documento 
2. Actualizar implementación 
3. Actualizar tests afectados 
4. Verificar que no rompe funcionalidad existente