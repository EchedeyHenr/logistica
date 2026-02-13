# infrastructure/seed_data.py

from logistica.domain.shipment import Shipment
from logistica.domain.fragile_shipment import FragileShipment
from logistica.domain.express_shipment import ExpressShipment
from logistica.domain.center import Center
from logistica.domain.route import Route

from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logistica.infrastructure.memory_center import CenterRepositoryMemory
from logistica.infrastructure.memory_route import RouteRepositoryMemory


def seed_repository():

    shipment_repo = ShipmentRepositoryMemory()
    center_repo = CenterRepositoryMemory()
    route_repo = RouteRepositoryMemory()

    center_madrid = Center("MAD16", "Madrid Centro", "Calle inventada 16")
    center_barcelona = Center("BCN03", "Barcelona Centro", "Carrer inventat 03")
    center_gran_canaria = Center("LPA06", "Las Palmas de Gran Canaria", "Calle León y Castillo 06")

    center_repo.add(center_madrid)
    center_repo.add(center_barcelona)
    center_repo.add(center_gran_canaria)

    route_01 = Route("MAD16-BCN03-STD-001", center_madrid, center_barcelona)
    route_express = Route("MAD16-BCN03-EXP-006", center_madrid, center_barcelona)
    route_02 = Route("MAD16-LPA06-STD-003", center_madrid, center_gran_canaria)
    route_express_02 = Route("MAD16-LPA06-EXP-009", center_madrid, center_gran_canaria)

    route_repo.add(route_01)
    route_repo.add(route_express)
    route_repo.add(route_02)
    route_repo.add(route_express_02)

    envio1 = Shipment("ABC123", "Amazon", "Juan Pérez", 1)
    envio2 = Shipment("EXP456", "Zara", "María López", 2)
    envio3 = ExpressShipment("URG789", "Apple", "Carlos Gómez")
    envio4 = Shipment("ALB882", "Alibaba", "Victor Aldama", 1)
    envio5 = FragileShipment("SHN114", "Shein", "Atteneri López", 2)

    shipment_repo.add(envio1)
    shipment_repo.add(envio2)
    shipment_repo.add(envio3)
    shipment_repo.add(envio4)
    shipment_repo.add(envio5)

    return {
        "shipments": shipment_repo,
        "routes": route_repo,
        "centers": center_repo
    }
