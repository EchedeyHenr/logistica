from logistica.domain.center import Center
from logistica.domain.route import Route
from logistica.domain.shipment import Shipment
from logistica.infrastructure.memory_center import CenterRepositoryMemory
from logistica.infrastructure.memory_route import RouteRepositoryMemory
from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logistica.application.center_service import CenterService
from logistica.application.route_service import RouteService
from logistica.application.shipment_service import ShipmentService

# 1. Preparación de Infraestructura
center_repo = CenterRepositoryMemory()
route_repo = RouteRepositoryMemory()
shipment_repo = ShipmentRepositoryMemory()

# 2. Inicialización de Servicios
center_service = CenterService(center_repo, shipment_repo)
route_service = RouteService(route_repo, shipment_repo, center_repo)
ship_service = ShipmentService(shipment_repo)

print("=== TEST DE INFRAESTRUCTURA Y SERVICIOS ===\n")

# --- CASO 1: Persistencia en Repositorios de Centros ---
print("Caso 1: Registro de centros y persistencia en memoria")
center_service.register_center("C1", "Madrid Hub", "Calle Central 1")
center_service.register_center("C2", "Barcelona Hub", "Puerto BCN")

lista_centros = center_repo.list_all()
print(f"Centros en repo: {[c.center_id for c in lista_centros]}") # Esperado: ['C1', 'C2']
print("---")

# --- CASO 2: Registro de Envíos y Tipos ---
print("Caso 2: Registro de envíos a través del servicio")
ship_service.register_shipment("STD-01", "Alice", "Bob", priority=1, shipment_type="standard")
ship_service.register_shipment("FRG-01", "Charlie", "Diana", priority=2, shipment_type="fragile")

# Nota: El registro de 'express' fallará debido a la diferencia de parámetros
# en el constructor de ExpressShipment
try:
    ship_service.register_shipment("EXP-01", "Eva", "Frank", priority=3, shipment_type="express")
except TypeError as e:
    print(f"Error esperado en Express (Bug detectado en servicio): {e}")
print("---")

# --- CASO 3: Flujo de Ruta y Coordinación ---
print("Caso 3: Creación de ruta y asignación")
route_service.create_route("R-01", "C1", "C2")
route_service.assign_shipment_to_route("STD-01", "R-01")

# Verificamos que el envío se registró en el centro de origen
centro_origen = center_repo.get_by_center_id("C1")
print(f"¿Envío STD-01 en centro origen?: {centro_origen.has_shipment('STD-01')}")
print("---")

# --- CASO 4: El Ciclo de Vida Crítico (Dispatch -> Complete) ---
print("Caso 4: Despacho y finalización de ruta")
# Primero despachamos para que el envío pase a IN_TRANSIT
route_service.dispatch_route("R-01")
envio = shipment_repo.get_by_tracking_code("STD-01")
print(f"Estado tras despacho: {envio.current_status}") # Esperado: IN_TRANSIT

# Ahora completamos la ruta
route_service.complete_route("R-01")
print(f"Estado tras completar: {envio.current_status}") # Esperado: DELIVERED

# Verificamos llegada al destino
centro_destino = center_repo.get_by_center_id("C2")
print(f"¿Envío STD-01 en centro destino?: {centro_destino.has_shipment('STD-01')}")
print("---")

# --- CASO 5: Búsqueda y Errores de Infraestructura ---
print("Caso 5: Validaciones de búsqueda")
try:
    route_service.get_route("R-NONEXIST")
except ValueError as e:
    print(f"Error esperado (Ruta no existe): {e}")

print("\n¡Pruebas de infraestructura y servicios finalizadas!")