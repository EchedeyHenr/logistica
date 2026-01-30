from logistica.application.shipment_service import ShipmentService
from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory

ship_service = ShipmentService(ShipmentRepositoryMemory())

print("=== TEST DE LÓGICA ESPECÍFICA POR TIPO DE ENVÍO ===\n")

# --- CASO 1: Restricciones de Envío Frágil ---
print("Caso 1: Prioridad mínima en envíos frágiles")
try:
    # Prioridad 1 es ilegal para frágiles (mínimo 2)
    ship_service.register_shipment("FRG-LOW", "A", "B", priority=1, shipment_type="fragile")
except ValueError as e:
    print("Error capturado (Prioridad frágil < 2):", e)

ship_service.register_shipment("FRG-OK", "A", "B", priority=2, shipment_type="fragile")
try:
    ship_service.decrease_shipment_priority("FRG-OK")
except ValueError as e:
    print("Error capturado (No se puede bajar de 2 en frágil):", e)
print("---")

# --- CASO 2: Inmutabilidad de Prioridad Express ---
print("Caso 2: Prioridad máxima en envíos express")
try:
    ship_service.register_shipment("EXP-01", "A", "B", shipment_type="express")
    print("Envío Express registrado.")
    ship_service.increase_shipment_priority("EXP-01")
except (TypeError, ValueError) as e:
    print("Error capturado en Express:", e)
print("---")

# --- CASO 3: Persistencia de historial de estados ---
print("Caso 3: Verificación del historial de estados")
ship_service.register_shipment("STD-HIST", "A", "B")
ship_service.update_shipment_status("STD-HIST", "IN_TRANSIT")
ship_service.update_shipment_status("STD-HIST", "DELIVERED")

# Obtenemos el objeto directamente para ver su historial
envio = ship_service.get_shipment("STD-HIST")
print(f"Historial de estados: {envio.get_status_history()}")
# Esperado: ['REGISTERED', 'IN_TRANSIT', 'DELIVERED']
print("---")

print("¡Tests de lógica de envíos finalizados!")