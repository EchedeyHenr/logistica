# Guía de rutas Flask — echedey / logística

## El dominio en una línea

Sistema de gestión logística con tres entidades principales: **Shipment** (envío estándar),
**ExpressShipment** y **FragileShipment** (subclases con reglas de prioridad propias),
**Center** (centro logístico que almacena envíos) y **Route** (ruta que conecta dos centros
y transporta envíos entre ellos mediante una relación N:M).

---

## Inventario completo del menú

Las 16 opciones se clasifican en cuatro categorías según el tipo de operación que realizan:

| Categoría | Criterio |
|-----------|----------|
| **Lectura** | Solo consulta; no modifica estado. |
| **Acción** | Crea o elimina una entidad o relación; estado inicial o final. |
| **Transición** | Avanza la máquina de estados (ruta o envío). |
| **Acción combinada (coordina varias entidades a la vez)** | Coordina varias entidades al mismo tiempo en una sola operación. |

| # | Operación en menú | Método del servicio | Categoría | Excepción capturada |
|---|-------------------|---------------------|-----------|---------------------|
| 1 | Registrar envío | `ShipmentService.register_shipment()` | Acción | `ValueError` (código duplicado, tipo inválido, patrón inválido) |
| 2 | Asignar envío a ruta | `RouteService.assign_shipment_to_route()` | Acción combinada (coordina varias entidades a la vez) | `ValueError` (ruta inexistente, ruta inactiva, envío inexistente, envío ya asignado) |
| 3 | Quitar envío de ruta | `RouteService.remove_shipment_from_route()` | Acción | `ValueError` (ruta inexistente, envío inexistente, envío no pertenece a esa ruta) |
| 4 | Actualizar estado de envío | `ShipmentService.update_shipment_status()` | Transición | `ValueError` (envío inexistente, transición no permitida) |
| 5 | Aumentar prioridad del envío | `ShipmentService.increase_shipment_priority()` | Acción | `ValueError` (envío inexistente, prioridad ya máxima, Express no modificable) |
| 6 | Disminuir prioridad del envío | `ShipmentService.decrease_shipment_priority()` | Acción | `ValueError` (envío inexistente, prioridad ya mínima, Fragile no puede bajar de 2) |
| 7 | Listar envíos | `ShipmentService.list_shipments()` | Lectura | — |
| 8 | Ver detalles de un envío | `ShipmentService.get_shipment()` | Lectura | `ValueError` (envío inexistente) |
| 9 | Registrar centro logístico | `CenterService.register_center()` | Acción | `ValueError` (campos vacíos, ID duplicado) |
| 10 | Listar centros logísticos | `CenterService.list_centers()` | Lectura | — |
| 11 | Ver envíos en un centro | `CenterService.list_shipments_in_center()` | Lectura | `ValueError` (ID vacío, centro inexistente) |
| 12 | Crear ruta | `RouteService.create_route()` | Acción | `ValueError` (ID vacío, ruta duplicada, centro origen/destino inexistente, patrón de ID inválido) |
| 13 | Listar rutas | `RouteService.list_routes()` | Lectura | — |
| 14 | Asignar varios envíos a ruta | `RouteService.assign_shipment_to_route()` (bucle) | Acción combinada (coordina varias entidades a la vez) | `ValueError` por cada código (se acumulan, no abortan el bucle) |
| 15 | Despachar ruta | `RouteService.dispatch_route()` | Transición | `ValueError` (ruta inexistente, ruta inactiva, ya despachada) |
| 16 | Completar ruta | `RouteService.complete_route()` | Transición | `ValueError` (ruta inexistente, ruta ya finalizada) |

---

## Rutas sugeridas (toda la API)

Los parámetros de creación/modificación se pasan como segmentos de URL.

### Envíos

| Ruta Flask | Método del servicio | Descripción |
|------------|---------------------|-------------|
| `/shipments` | `shipment_service.list_shipments()` | Lista todos los envíos |
| `/shipments/<tracking_code>` | `shipment_service.get_shipment(tracking_code)` | Detalle de un envío |
| `/shipments/nuevo/<tracking_code>/<tipo>/<descripcion>` | `shipment_service.register_shipment(tracking_code, tipo, descripcion)` | Registra un nuevo envío (`tipo`: STANDARD / EXPRESS / FRAGILE) |
| `/shipments/<tracking_code>/estado/<nuevo_estado>` | `shipment_service.update_shipment_status(tracking_code, nuevo_estado)` | Actualiza el estado de un envío |
| `/shipments/<tracking_code>/prioridad/aumentar` | `shipment_service.increase_shipment_priority(tracking_code)` | Aumenta la prioridad de un envío |
| `/shipments/<tracking_code>/prioridad/disminuir` | `shipment_service.decrease_shipment_priority(tracking_code)` | Disminuye la prioridad de un envío |

### Centros

| Ruta Flask | Método del servicio | Descripción |
|------------|---------------------|-------------|
| `/centers` | `center_service.list_centers()` | Lista todos los centros logísticos |
| `/centers/<center_id>/shipments` | `center_service.list_shipments_in_center(center_id)` | Lista los envíos almacenados en un centro |
| `/centers/nuevo/<center_id>/<nombre>/<ciudad>` | `center_service.register_center(center_id, nombre, ciudad)` | Registra un nuevo centro logístico |

### Rutas

| Ruta Flask | Método del servicio | Descripción |
|------------|---------------------|-------------|
| `/routes` | `route_service.list_routes()` | Lista todas las rutas |
| `/routes/nuevo/<route_id>/<center_origen>/<center_destino>/<tipo>` | `route_service.create_route(route_id, center_origen, center_destino, tipo)` | Crea una nueva ruta |
| `/routes/<route_id>/asignar/<tracking_code>` | `route_service.assign_shipment_to_route(tracking_code, route_id)` | Asigna un envío a una ruta |
| `/routes/<route_id>/quitar/<tracking_code>` | `route_service.remove_shipment_from_route(tracking_code, route_id)` | Quita un envío de una ruta |
| `/routes/<route_id>/despachar` | `route_service.dispatch_route(route_id)` | Despacha una ruta |
| `/routes/<route_id>/completar` | `route_service.complete_route(route_id)` | Completa una ruta |

---

### Ejemplo: cómo quedaría `app.py` con dos rutas ya hechas

El siguiente fragmento muestra la estructura mínima de `app.py` con dos rutas implementadas
para que puedas tomar el patrón y aplicarlo al resto:

```python
from flask import Flask
from logistica.infrastructure.seed_data import seed_repository
from logistica.application.shipment_service import ShipmentService
from logistica.application.route_service import RouteService
from logistica.application.center_service import CenterService

app = Flask(__name__)

repos = seed_repository()
shipment_service = ShipmentService(repos["shipments"])
center_service = CenterService(repos["centers"], repos["shipments"])
route_service = RouteService(repos["routes"], repos["shipments"], repos["centers"])


@app.route("/")
def bienvenida():
    return (
        "Bienvenido al sistema de logística\n"
        "  /shipments          → lista todos los envíos\n"
        "  /centers            → lista todos los centros logísticos\n"
        "  /routes             → lista todas las rutas\n"
    )


@app.route("/shipments")
def listar_envios():
    envios = shipment_service.list_shipments()
    if not envios:
        return "No hay envíos registrados."
    return "\n".join(str(e) for e in envios)


if __name__ == "__main__":
    app.run(debug=True)
```

**Lo que hace cada parte:**

- Los repositorios y los servicios se crean **una sola vez** fuera de las vistas, al arrancar la
  aplicación. Así todas las rutas comparten el mismo estado en memoria.
- Cada función de vista llama al método del servicio correspondiente y devuelve texto plano.
- Para rutas que pueden lanzar `ValueError` puedes devolver una tupla `(mensaje, código)`:
  `return "No encontrado", 404` o `return "Datos inválidos", 400`.

---

## Métodos del servicio a añadir (o verificar antes de usar en Flask)

| Método propuesto | Servicio | Motivo |
|------------------|----------|--------|
| `list_shipments_in_route(route_id)` | `RouteService` | No existe. Delegaría en `route.list_shipment()`. Útil para `/routes/<route_id>/shipments`. |

> `get_center(center_id)` en `CenterService` y `get_route(route_id)` en `RouteService` ya existen en el código. Verifica que devuelven el objeto completo antes de usarlos en rutas de detalle.

### Discrepancia crítica detectada en `menu.py`

La opción 3 del menú llama:

```python
route_service.remove_shipment_from_route(tracking_code)   # un solo argumento
```

La firma real del método es:

```python
def remove_shipment_from_route(self, tracking_code, route_id):  # dos argumentos
```

En la ruta Flask (`/routes/<route_id>/quitar/<tracking_code>`) ambos parámetros llegan de la URL, así que **la API no tiene este problema**. El bug existe en el menú de consola, pero no te afecta para ut4e1.

---

## Advertencias

### Herencia Shipment → ExpressShipment / FragileShipment

`get_shipment()` devuelve el objeto de dominio real (puede ser cualquiera de los tres tipos).
La propiedad `shipment.shipment_type` devuelve la cadena `"STANDARD"`, `"EXPRESS"` o
`"FRAGILE"` según la clase; es el discriminador natural para distinguirlos en la respuesta.
Los atributos específicos de cada subclase (p. ej. plazo garantizado en Express, indicador
de fragilidad en Fragile) deben consultarse directamente en los ficheros de dominio antes
de incluirlos en el texto de respuesta del route.

### `status_history` como lista

El detalle de un envío expone el historial mediante `shipment.get_status_history()`, que
devuelve una lista de strings. En el route Flask se puede mostrar con un simple `join`:
`"\n".join(shipment.get_status_history())`.

### Estado del envío como máquina de estados

Las únicas transiciones válidas son `REGISTERED → IN_TRANSIT → DELIVERED`. No hay marcha
atrás. Cualquier intento de transición inválida levanta `ValueError` en el dominio (método
`can_change_to()`). Las rutas Flask de cambio de estado deben capturar ese `ValueError` y
devolver `400 Bad Request` con el mensaje descriptivo del error.

### Relación N:M Route-Shipment

Una ruta puede contener múltiples envíos; un envío solo puede estar en una ruta a la vez
(RN-016). La relación es bidireccional: `Route._shipments` contiene objetos `Shipment`, y
`Shipment._assigned_route` almacena el `route_id` (string, no la referencia al objeto).
Al mostrar la ruta asignada de un envío, usar `shipment.assigned_route` (string o `None`),
nunca acceder directamente al objeto `Route`.

### Ubicación actual del envío

No existe un método `get_ubicacion()` en ningún servicio. La ubicación se infiere:

- Si `assigned_route is None` y `current_status == "REGISTERED"`: el envío aún no tiene
  ruta; desconocida o en depósito inicial.
- Si `assigned_route is not None` y `current_status == "REGISTERED"`: asignado a ruta,
  físicamente en el centro de origen (el envío aparece en `center.list_shipments()`).
- Si `current_status == "IN_TRANSIT"`: en tránsito entre centros.
- Si `current_status == "DELIVERED"`: en el centro de destino de la última ruta.

Para `ut4e1` es suficiente mostrar `assigned_route` (string o `None`).

### Excepción única: `ValueError` estándar

El proyecto no tiene módulo `errores.py` propio. Todos los servicios y el dominio lanzan
`ValueError` con mensajes descriptivos en español. La regla de mapeo para rutas Flask es:

- `ValueError` por entidad no encontrada → `404 Not Found`
- `ValueError` por datos de entrada inválidos o transición no permitida → `400 Bad Request`

En el route, captura con `try/except ValueError as e: return str(e), 404`.

### Instanciación de servicios en Flask

Actualmente `menu.py` crea los tres servicios dentro de `main()`. En Flask se crean
los repositorios y los servicios fuera de las funciones de vista (como variables del módulo),
de modo que estén disponibles en todas las rutas sin reinstanciarlos por petición — igual
que en el lab A2.

### Patrón de `route_id`

El dominio valida el formato `ORIGEN-DESTINO-TIPO-NNN` (ej. `MAD01-BCN02-EXP-001`) mediante
regex en `Route.__init__`. Si la URL Flask recibe un `route_id` que no cumple el patrón, el
`ValueError` se lanzará dentro de `create_route()` y debe capturarse como `400`.
