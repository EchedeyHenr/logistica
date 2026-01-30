from logistica.application.shipment_service import ShipmentService
from logistica.application.route_service import RouteService
from logistica.application.center_service import CenterService
from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logistica.infrastructure.memory_center import CenterRepositoryMemory
from logistica.infrastructure.memory_route import RouteRepositoryMemory

# Setup
s_repo, c_repo, r_repo = ShipmentRepositoryMemory(), CenterRepositoryMemory(), RouteRepositoryMemory()
ship_service = ShipmentService(s_repo)
center_service = CenterService(c_repo, s_repo)
route_service = RouteService(r_repo, s_repo, c_repo)

print("=== TEST DE ROBUSTEZ Y VALIDACIONES ===\n")

# --- CASO 1: Identificadores vacíos o con espacios ---
print("Caso 1: Validar strings vacíos en servicios")
try:
    center_service.register_center("   ", "Nombre", "Ubicación")
except ValueError as e:
    print("Error capturado correctamente:", e)
print("---")

# --- CASO 2: Acciones sobre entidades que no existen ---
print("Caso 2: Operar con IDs inexistentes")
try:
    route_service.assign_shipment_to_route("TRK-NO-EXISTE", "RUTA-FANTASMA")
except ValueError as e:
    print("Error capturado (Envío/Ruta no existen):", e)
print("---")

# --- CASO 3: Lógica de Negocio - Ruta entre el mismo centro ---
print("Caso 3: Intentar crear ruta con origen y destino iguales")
center_service.register_center("MAD", "Madrid", "Centro")
try:
    route_service.create_route("R-ERROR", "MAD", "MAD")
except ValueError as e:
    print("Error capturado (Origen == Destino):", e)
print("---")

# --- CASO 4: Doble despacho de ruta ---
print("Caso 4: Intentar despachar una ruta ya despachada")
center_service.register_center("BCN", "Barcelona", "Norte")
ship_service.register_shipment("TRK-1", "A", "B")
route_service.create_route("R-1", "MAD", "BCN")
route_service.assign_shipment_to_route("TRK-1", "R-1")

route_service.dispatch_route("R-1") # Primer despacho OK
try:
    route_service.dispatch_route("R-1") # Segundo despacho
except ValueError as e:
    print("Error capturado (Ruta ya despachada):", e)
print("---")

print("¡Tests de robustez finalizados!")