# 🧩 Modelo de Dominio del Sistema Logístico

## 🏗️ Introducción

El modelo de dominio representa los conceptos fundamentales, sus atributos, comportamientos y relaciones dentro del contexto del negocio logístico. Este documento describe las **entidades**, **invariantes** y **colaboraciones** que forman el núcleo del sistema.

---

## 📦 Entidades Principales

### 1. Shipment (Envío)
**Responsabilidad**: Representar un paquete o bulto que se transporta a través de la red logística.

#### Atributos
| Atributo | Tipo | Descripción | Inmutabilidad |
|----------|------|-------------|---------------|
| `tracking_code` | `str` | Código único de seguimiento | Inmutable |
| `sender` | `str` | Remitente del envío | Inmutable |
| `recipient` | `str` | Destinatario del envío | Inmutable |
| `_priority` | `int` | Nivel de prioridad (1-3) | Mutable (con restricciones) |
| `_current_status` | `str` | Estado actual (REGISTERED/IN_TRANSIT/DELIVERED) | Mutable (con reglas) |
| `_status_history` | `List[str]` | Historial completo de estados | Solo adición |
| `_assigned_route` | `Optional[str]` | ID de ruta asignada | Mutable |

#### Comportamientos
```python
# Gestión de estado
def update_status(new_status: str) -> None
def can_change_to(new_status: str) -> bool

# Gestión de prioridad
def increase_priority() -> None
def decrease_priority() -> None

# Gestión de ruta
def assign_route(route_id: str) -> None
def remove_route() -> None
def is_assigned_to_route() -> bool

# Consultas
def is_delivered() -> bool
def get_status_history() -> List[str]
```

### Invariantes
1. `tracking_code` debe ser único en todo el sistema
2. `priority` debe estar en el rango {1, 2, 3}
3. Solo transiciones válidas entre estados
4. Historial debe reflejar todos los cambios de estado en orden

### 2. FragileShipment (Envío Frágil)
**Responsabilidad**: Especialización de Shipment para mercancía delicada con reglas adicionales.

#### Atributos Adicionales
| Atributo | Tipo | Descripción     | 
|----------|------|-----------------|
| `_fragile` | `bool` | Siempre `True` (identificador) |

### Invariantes Adicionales
1. Prioridad nunca inferior a 2
2. Marcado como frágil permanentemente

### 3. ExpressShipment (Envío Express)
**Responsabilidad**: Especialización para envíos urgentes con prioridad máxima fija.

#### Atributos Especiales
* `priority`: Siempre retorna 3 (propiedad de solo lectura)

#### Comportamientos Específicos
* **Constructor**: Establece prioridad automática a 3
* `increase_priority()`: Siempre lanza error (ya es máxima)
* `decrease_priority()`: Siempre lanza error (No puede disminuir)
* `shipment_type`: Siempre retorna "EXPRESS"

### Invariantes
1. Prioridad siempre es 3 (no modificable)
2. Tipo siempre es EXPRESS

### 4. Center (Centro Logístico)
**Responsabilidad**: Representar un nodo físico en la red logística que almacena y transfiere envíos.

#### Atributos
| Atributo | Tipo | Descripción | Inmutabilidad |
| :--- | :--- | :--- | :--- |
| `center_id` | `str` | Identificador único del centro | Inmutable |
| `name` | `str` | Nombre descriptivo (ej: "Sede Norte") | Inmutable |
| `location` | `str` | Ubicación física o coordenadas | Inmutable |
| `_shipments` | `List[Shipment]` | Inventario actual de envíos | Mutable |

#### Comportamientos
```python
# Gestión de inventario
def receive_shipment(shipment: Shipment) -> None
def dispatch_shipment(shipment: Shipment) -> Shipment
def list_shipments() -> List[Shipment]
def has_shipment(tracking_code: str) -> bool
```

### Invariantes
1. `center_id` debe ser único
2. No puede contener el mismo envío dos veces
3. Solo puede despachar envíos que tenga en inventario
4. Atributos básicos no pueden ser vacíos

### 5. Route (Ruta de Transporte)
**Responsabilidad**: Gestionar el transporte de envíos entre dos centros logísticos.

#### Atributos
| Atributo | Tipo | Descripción | Inmutabilidad |
| :--- | :--- | :--- | :--- |
| `route_id` | `str` | Identificador único de la ruta | Inmutable |
| `origin_center` | `Center` | Centro de partida | Inmutable |
| `destination_center` | `Center` | Centro de llegada | Inmutable |
| `_shipments` | `List[Shipment]` | Envíos asignados a esta ruta | Mutable |
| `_active` | `bool` | Estado operativo de la ruta | Mutable |

#### Comportamientos
```python
# Gestión de envíos
def add_shipment(shipment: Shipment) -> None
def remove_shipment(shipment: Shipment) -> None
def list_shipment() -> List[Shipment]

# Gestión de ciclo de vida
def complete_route() -> None
```

### Invariantes
1. `origin_center ≠ destination_center`
2. Solo rutas activas pueden recibir nuevos envíos
3. Al completarse, todos los envíos pasan a DELIVERED
4. `origin_center` y `destination_center` deben existir

## 📐 Invariantes del Sistema

### Invariantes Globales
1. **Unicidad de Identificadores**: No puede haber dos entidades con el mismo ID
   * **Shipments**: `tracking_code` único
   * **Centers**: `center_id` único
   * **Routes**: `route_id` único
2. **Consistencia de Referencias**:
   * Si `Shipment.assigned_route = X`, entonces `Route X` debe contener ese shipment
   * Si `Shipment` está en `Center.inventory`, debe estar `REGISTERED` o `DELIVERED`
   * Si `Shipment` está en `Route.shipments`, debe estar asignado a esa ruta
3. Integridad del Ciclo de Vida:
   * `Shipment` creado → estado `REGISTERED`
   * `Shipment` en ruta despachada → estado `IN_TRANSIT`
   * `Shipment` en ruta completada → estado `DELIVERED`
   * Estados finales no pueden revertirse

### Invariantes por Estado

#### Para Estado REGISTERED
* No tiene `assigned_route` o si la tiene, aún está en centro origen
* No aparece en historial de estados posteriores
* Puede asignarse a cualquier ruta activa

#### Para Estado IN_TRANSIT
* Debe tener `assigned_route`
* La ruta asignada debe estar activa
* No está en inventario de ningún centro
* Aparece en historial: `REGISTERED → IN_TRANSIT`

#### Para Estado DELIVERED
* Debe estar en inventario de centro destino
* Su ruta asignada (si la tenía) debe estar completada
* Aparece en historial: `REGISTERED → IN_TRANSIT → DELIVERED`
* Es estado final (no puede cambiar)

## 🎯 Patrones de Diseño Aplicados

### 1. Heritage y Polimorfismo
```python
# Jerarquía de envíos
Shipment (base)
├── FragileShipment (prioridad especial)
└── ExpressShipment (prioridad fija)

# Comportamiento polimórfico
def calculate_priority_score(shipment: Shipment):
    # Funciona con cualquier subtipo
    return shipment.priority * shipment.get_urgency_factor()
```

### 2. Repository Pattern
```python
# Contrato en Domain
class ShipmentRepository:
    def add(self, shipment: Shipment) -> None
    
# Implementación en Infrastructure  
class ShipmentRepositoryMemory(ShipmentRepository):
    def add(self, shipment: Shipment):
        self._storage[shipment.tracking_code] = shipment
```

### 3. Dependency Injection
```python
# Los servicios reciben dependencias
class ShipmentService:
    def __init__(self, repo: ShipmentRepository):  # Inyección
        self._repo = repo
```

### 4. Immutable Core
* Identificadores (`tracking_code`, `center_id`, `route_id`) inmutables
* Datos básicos (`sender`, `recipient`, `name`, `location`) inmutables
* Solo estado y relaciones pueden cambiar

## 🔄 Ciclo de Vida de las Entidades

### Shipment Lifecycle
```
Creación → REGISTERED → (opcional: asignar a ruta)
         ↓
     IN_TRANSIT (al despachar ruta)
         ↓
     DELIVERED (al completar ruta)
         ║
     [ESTADO FINAL]
```

### Route Lifecycle
```
Creación → Activa → (añadir envíos)
         ↓
    Despachada (envíos → IN_TRANSIT)
         ↓
    Completada (envíos → DELIVERED)
         ║
    [ESTADO FINAL: Inactiva]
```

### Center States
```
Operativo → (recibir envíos) → Con inventario
         ↓ (despachar envíos)
       Sin inventario
         ↑ (recibir más)
```

## 🧪 Validación del Modelo

### Reglas de Validación por Entidad

#### Shipment Validation Rules
1. `tracking_code` no vacío y único
2. `sender` y `recipient` no vacíos
3. `priority ∈ {1, 2, 3}`
4. Transiciones de estado válidas

#### FragileShipment Additional Rules
1. `priority ≥ 2` en creación
2. `priority` nunca < 2

#### Route Validation Rules
1. `origin_center ≠ destination_center`
2. Centros no nulos
3. Solo activa si puede recibir envíos

### Ejemplos de Estados Inválidos
```python
# ❌ INVALIDO: Envío DELIVERED sin haber pasado por IN_TRANSIT
shipment.update_status("DELIVERED")  # Error si estado actual es REGISTERED

# ❌ INVALIDO: Fragile con prioridad 1
FragileShipment("F1", "A", "B", priority=1)  # ValueError

# ❌ INVALIDO: Ruta consigo misma
Route("R1", center, center)  # ValueError
```

## 🔍 Perspectivas del Modelo

### Perspectiva Operativa
* **Envíos**: Qué se transporta 
* **Centros**: Dónde se almacena 
* **Rutas**: Cómo se mueve

### Perspectiva de Estado
* **REGISTERED**: Pendiente de procesar 
* **IN_TRANSIT**: En movimiento 
* **DELIVERED**: Completado

### Perspectiva de Prioridad
* **1 (Baja)**: Standard no urgente 
* **2 (Media)**: Standard urgente o Frágil 
* **3 (Alta)**: Express (siempre) o Frágil urgente

## 📝 Evolución del Modelo

### Extensiones Posibles Futuras
No necesariamente serán añadidas.

1. **Vehicle Entity**: Añadir camiones/conductores a las rutas
2. **Time Tracking**: Fechas de creación, despacho, entrega
3. **Capacity Limits**: Límites de volumen/peso en centros
4. **Multi-step Routes**: Rutas con múltiples paradas intermedias
5. **Customer Entity**: Clientes con historial de envíos

### Consideraciones de Diseño
* El modelo actual es minimalista pero completo
* Extensible mediante herencia y composición
* Independiente de infraestructura
* Testeable en aislamiento