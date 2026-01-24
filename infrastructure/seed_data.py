# infrastructure/seed_data.py

from logisticaEnvios.domain.shipment import Shipment
from logisticaEnvios.infrastructure.memory_shipment import ShipmentRepositoryMemory

def seed_repository():
    repo = ShipmentRepositoryMemory()

    envio1 = Shipment(
        tracking_code="ABC123",
        sender="Amazon",
        recipient="Juan Pérez",
        priority=1
    )

    envio2 = Shipment(
        tracking_code="EXP456",
        sender="Zara",
        recipient="María López",
        priority=2
    )

    envio3 = Shipment(
        tracking_code="URG789",
        sender="Apple",
        recipient="Carlos Gómez",
        priority=3
    )

    # Simulamos algo de vida del sistema
    envio2.assign_route("RUTA-01")
    envio2.update_status("IN_TRANSIT")

    envio3.assign_route("RUTA-EXPRESS")
    envio3.update_status("IN_TRANSIT")

    repo.add(envio1)
    repo.add(envio2)
    repo.add(envio3)

    return repo
