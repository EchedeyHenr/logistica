# test_domain_shipments.py
# Script para probar Shipment, FragileShipment y ExpressShipment

from logistica.domain.shipment import Shipment
from logistica.domain.fragile_shipment import FragileShipment
from logistica.domain.express_shipment import ExpressShipment

print("=== TEST DE ENVÍOS Y HERENCIA ===\n")

# --- CASO 1: Shipment estándar ---
print("Caso 1: Shipment estándar")
s1 = Shipment("STD001", "Alice", "Bob", priority=1)
print("Código:", s1.tracking_code)
print("Tipo:", getattr(s1, "shipment_type", "STANDARD"))
print("Prioridad:", s1.priority)
print("Ruta asignada:", s1.assigned_route)
print("---\n")

# --- CASO 2: FragileShipment válido ---
print("Caso 2: FragileShipment válido")
s2 = FragileShipment("FRG001", "Charlie", "Diana", priority=2)
print("Código:", s2.tracking_code)
print("Tipo:", s2.shipment_type)
print("Prioridad:", s2.priority)
print("¿Es frágil?", s2.is_fragile())
print("Ruta asignada:", s2.assigned_route)
print("---\n")

# --- CASO 3: FragileShipment con prioridad inválida ---
print("Caso 3: FragileShipment con prioridad inválida")
try:
    FragileShipment("FRG002", "Charlie", "Diana", priority=1)
except ValueError as e:
    print("Error esperado:", e)
print("---\n")

# --- CASO 4: ExpressShipment válido ---
print("Caso 4: ExpressShipment válido")
s3 = ExpressShipment("EXP001", "Apple", "Eve")
print("Código:", s3.tracking_code)
print("Tipo:", s3.shipment_type)
print("Prioridad:", s3.priority)
print("Ruta asignada:", s3.assigned_route)
print("---\n")

# --- CASO 5: ExpressShipment no acepta prioridad externa ---
print("Caso 5: ExpressShipment no acepta prioridad externa")
try:
    ExpressShipment("EXP002", "Samsung", "Lucía", priority=1)
except TypeError as e:
    print("Error esperado:", e)
print("---\n")

# --- CASO 6: Transiciones de estado válidas ---
print("Caso 6: Actualizar estado de s1")
s1.update_status("IN_TRANSIT")
print("Estado actual:", s1.current_status)
print("Historial:", s1.get_status_history())
s1.update_status("DELIVERED")
print("Estado final:", s1.current_status)
print("Historial final:", s1.get_status_history())
print("---\n")

# --- CASO 7: Intentar transición inválida ---
print("Caso 7: Transición inválida")
try:
    s2.update_status("DELIVERED")  # desde REGISTERED → DELIVERED no permitido
except ValueError as e:
    print("Error esperado:", e)
print("---\n")

# --- CASO 8: Asignar y quitar rutas ---
print("Caso 8: Asignar y eliminar ruta en s2")
s2.assign_route("Ruta-1")
print("Ruta asignada:", s2.assigned_route)
print("¿Asignado a ruta?", s2.is_assigned_to_route())
s2.remove_route()
print("Ruta tras remove:", s2.assigned_route)
print("¿Asignado a ruta?", s2.is_assigned_to_route())
print("---\n")

# --- CASO 9: Incrementar y decrementar prioridad ---
print("Caso 9: Incrementar y decrementar prioridad")
s2.increase_priority()
print("Prioridad después de increase:", s2.priority)
try:
    s2.increase_priority()
except ValueError as e:
    print("Error esperado al aumentar prioridad:", e)
s2.decrease_priority()
print("Prioridad después de decrease:", s2.priority)
try:
    s2.decrease_priority()
    s2.decrease_priority()  # intenta ir por debajo de 2
except ValueError as e:
    print("Error esperado al disminuir prioridad:", e)
print("---\n")

# --- CASO 10: Verificación polimórfica ---
print("Caso 10: Verificación polimórfica")
envios = [s1, s2, s3]
for s in envios:
    tipo = getattr(s, "shipment_type", "STANDARD")
    print(f"{s.tracking_code} → Tipo: {tipo}, Prioridad: {s.priority}")
print("---\n")

print("¡Todos los tests de envíos y herencia completados correctamente!")
