# test_domain_centers.py

from logistica.domain.center import Center
from logistica.domain.shipment import Shipment

print("=== TEST DE CENTROS LOGÍSTICOS ===\n")

# --- CASO 1: Creación de centro válido ---
print("Caso 1: Creación de centro válido")
centro_a = Center("C-MAD", "Madrid Central", "Calle Mayor 1")
print("ID:", centro_a.center_id)
print("Nombre:", centro_a.name)
print("Ubicación:", centro_a.location)
print("Envíos iniciales:", len(centro_a.list_shipments()))
print("---\n")

# --- CASO 2: Validaciones de inicialización ---
print("Caso 2: Validaciones de campos obligatorios")
try:
    Center("", "Nombre", "Ubicación")
except ValueError as e:
    print("Error esperado (ID vacío):", e)
print("---\n")

# --- CASO 3: Recibir un envío ---
print("Caso 3: Recibir un envío")
s1 = Shipment("TRK001", "Remitente A", "Destinatario B")
centro_a.receive_shipment(s1)
print("¿Tiene el envío TRK001?", centro_a.has_shipment("TRK001"))
print("Total envíos en centro:", len(centro_a.list_shipments()))
print("---\n")

# --- CASO 4: Error al recibir duplicado ---
print("Caso 4: Error al recibir envío ya presente")
try:
    centro_a.receive_shipment(s1)
except ValueError as e:
    print("Error esperado:", e)
print("---\n")

# --- CASO 5: Despachar un envío ---
print("Caso 5: Despachar un envío (Salida hacia tránsito)")
# El despacho debe cambiar el estado del envío a IN_TRANSIT
despachado = centro_a.dispatch_shipment(s1)
print("Estado del envío tras despacho:", despachado.current_status)
print("¿Sigue en el centro?", centro_a.has_shipment("TRK001"))
print("---\n")

# --- CASO 6: Error al despachar algo que no existe ---
print("Caso 6: Error al despachar envío inexistente")
try:
    s2 = Shipment("TRK999", "X", "Y")
    centro_a.dispatch_shipment(s2)
except ValueError as e:
    print("Error esperado:", e)
print("---\n")

