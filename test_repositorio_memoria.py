# test_repositorio_memoria.py
# Script para probar ShipmentRepositoryMemory con casos posibles

from logisticaEnvios.domain.shipment import Shipment
from logisticaEnvios.infrastructure.memory_shipment import ShipmentRepositoryMemory

# Crear el repositorio
repo = ShipmentRepositoryMemory()

# --- CASOS DEL REPOSITORIO ---

# Caso 1: Listar cuando vacío → debe devolver []
print("Caso 1: Listar vacío")
envios = repo.list_all()
print("Lista:", envios)  # Esperado: []
print("Longitud:", len(envios))  # Esperado: 0
print("---")

# Caso 2: Guardar un envío válido
print("Caso 2: Guardar un envío")
envio1 = Shipment("ABC123", "Alice", "Bob")
repo.add(envio1)
print("Envío guardado:", envio1.tracking_code)  # Esperado: ABC123
print("---")

# Caso 3: Obtener por código existente (exacto)
print("Caso 3: Obtener existente (exacto)")
encontrado = repo.get_by_tracking_code("ABC123")
print("Encontrado:", encontrado.tracking_code if encontrado else None)  # Esperado: ABC123
print("---")

# --- CASOS DE MÉTODOS DE SHIPMENT ---

# Caso 4: Revisar estado inicial
print("Caso 4: Estado inicial")
print("Estado actual:", envio1.current_status)  # Esperado: REGISTERED
print("Historial:", envio1.get_status_history())  # Esperado: ['REGISTERED']
print("---")

# Caso 5: Actualizar estado a IN_TRANSIT
print("Caso 5: Actualizar estado a IN_TRANSIT")
envio1.update_status("in_transit")
print("Estado actual:", envio1.current_status)  # Esperado: IN_TRANSIT
print("Historial:", envio1.get_status_history())  # Esperado: ['REGISTERED', 'IN_TRANSIT']
print("---")

# Caso 6: Intentar transición inválida → ValueError
print("Caso 6: Transición inválida")
try:
    envio1.update_status("REGISTERED")
except ValueError as e:
    print("Error esperado:", e)
print("---")

# Caso 7: Comprobar is_delivered
print("Caso 7: Comprobar is_delivered")
print("¿Entregado?", envio1.is_delivered())  # Esperado: False
envio1.update_status("DELIVERED")
print("¿Entregado tras update?", envio1.is_delivered())  # Esperado: True
print("Historial:", envio1.get_status_history())  # ['REGISTERED', 'IN_TRANSIT', 'DELIVERED']
print("---")

# Caso 8: Asignar y eliminar ruta
print("Caso 8: Asignar y eliminar ruta")
envio1.assign_route("Ruta-1")
print("Ruta asignada:", envio1.assigned_route)  # Esperado: Ruta-1
print("¿Asignado a ruta?", envio1.is_assigned_to_route())  # Esperado: True
envio1.remove_route()
print("Ruta después de remove:", envio1.assigned_route)  # Esperado: None
print("¿Asignado a ruta?", envio1.is_assigned_to_route())  # Esperado: False
print("---")

# Caso 9: Incrementar y decrementar prioridad
print("Caso 9: Incrementar y decrementar prioridad")
envio1.priority = 2
print("Prioridad inicial:", envio1.priority)  # Esperado: 2
envio1.increase_priority()
print("Prioridad después de increase:", envio1.priority)  # Esperado: 3
try:
    envio1.increase_priority()  # Debe lanzar ValueError
except ValueError as e:
    print("Error esperado al aumentar prioridad:", e)
envio1.decrease_priority()
print("Prioridad después de decrease:", envio1.priority)  # Esperado: 2
try:
    envio1.decrease_priority()
    envio1.decrease_priority()  # Debe lanzar ValueError
except ValueError as e:
    print("Error esperado al disminuir prioridad:", e)
print("---")

# Caso 10: Guardar otro envío y listar
print("Caso 10: Guardar múltiple y listar")
envio2 = Shipment("XYZ789", "Charlie", "Diana")
repo.add(envio2)
envios = repo.list_all()
print("Lista de códigos:", [e.tracking_code for e in envios])  # Esperado: ['ABC123', 'XYZ789']
print("Longitud:", len(envios))  # Esperado: 2
print("---")

print("¡Pruebas de repositorio y Shipment completas!")