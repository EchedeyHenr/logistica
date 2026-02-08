# test_domain_routes.py

from logistica.domain.route import Route
from logistica.domain.center import Center
from logistica.domain.shipment import Shipment

print("=== TEST DE RUTAS Y FLUJO ENTRE CENTROS ===\n")

# Preparación de datos
c_origen = Center("ORG", "Centro Origen", "Sevilla")
c_destino = Center("DST", "Centro Destino", "Barcelona")
envio = Shipment("TRK-RUTA", "Pedro", "Juan")

# --- CASO 1: Creación de ruta válida ---
print("Caso 1: Creación de ruta válida")
ruta = Route("RUTA-01", c_origen, c_destino)
print("ID Ruta:", ruta.route_id)
print("Origen:", ruta.origin_center.name)
print("Destino:", ruta.destination_center.name)
print("¿Activa?:", ruta.is_active)
print("---\n")

# --- CASO 2: Error centros iguales ---
print("Caso 2: Error si origen y destino son iguales")
try:
    Route("R-ERR", c_origen, c_origen)
except ValueError as e:
    print("Error esperado:", e)
print("---\n")

# --- CASO 3: Añadir envío a la ruta ---
print("Caso 3: Añadir envío a la ruta")
# Esto debe: asignar ruta al envío y meterlo en el centro de origen
ruta.add_shipment(envio)
print("Ruta del envío:", envio.assigned_route)
print("¿Está el envío en el centro de origen?", c_origen.has_shipment(envio.tracking_code))
print("Envíos en ruta:", len(ruta.list_shipment()))
print("---\n")

# --- CASO 4: Completar la ruta ---
print("Caso 4: Completar ruta (Llegada al destino)")
# Al completar: la ruta se inactiva, el envío llega al destino y se marca DELIVERED
# PASO INTERMEDIO NECESARIO:
# Los envíos deben salir del centro de origen (ponerse IN_TRANSIT) antes de llegar al destino
for s in ruta.list_shipment():
    c_origen.dispatch_shipment(s)

print("Estado del envío antes de completar:", envio.current_status) # Debería ser IN_TRANSIT

# Ahora podemos completar la ruta
ruta.complete_route()
print("¿Ruta activa?:", ruta.is_active)
print("Estado final del envío:", envio.current_status)
print("¿Está el envío en el centro de destino?", c_destino.has_shipment("TRK-RUTA"))
print("Lista de envíos en ruta tras completar (debe ser 0):", len(ruta.list_shipment()))
print("---\n")

# --- CASO 5: Intentar añadir envío a ruta finalizada ---
print("Caso 5: Error al añadir envío a ruta inactiva")
try:
    s_nuevo = Shipment("TRK-NUEVO", "A", "B")
    ruta.add_shipment(s_nuevo)
except ValueError as e:
    print("Error esperado:", e)
print("---\n")

print("¡Tests de Route finalizados!")