# infrastructure/seed_data.py

"""
Módulo para inicializar datos de prueba en la logística.

Provee la función `seed_repository` que crea instancias de prueba de centros, rutas
y envíos, almacenándolas en repositorios en memoria para pruebas y ejecución inicial.
"""

from logistica.domain.shipment import Shipment
from logistica.domain.fragile_shipment import FragileShipment
from logistica.domain.express_shipment import ExpressShipment
from logistica.domain.center import Center
from logistica.domain.route import Route

from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logistica.infrastructure.memory_center import CenterRepositoryMemory
from logistica.infrastructure.memory_route import RouteRepositoryMemory


def seed_repository():
    """
    Inicializa los repositorios en memoria con datos de prueba.

    Crea centros logísticos, rutas entre ellos y envíos de distintos tipos
    para permitir la ejecución inmediata del sistema sin necesidad de entrada
    manual de datos.

    Returns:
        dict: Diccionario conteniendo instancias de repositorios inicializadas
              bajo las claves "shipments", "routes" y "centers".
    """

    shipment_repo = ShipmentRepositoryMemory()
    center_repo = CenterRepositoryMemory()
    route_repo = RouteRepositoryMemory()

    center_madrid = Center("MAD16", "Madrid Centro", "Calle inventada 16")
    center_barcelona = Center("BCN03", "Barcelona Centro", "Carrer inventat 03")
    center_gran_canaria = Center("LPA06", "Las Palmas de Gran Canaria", "Calle León y Castillo 06")

    center_repo.add(center_madrid)
    center_repo.add(center_barcelona)
    center_repo.add(center_gran_canaria)

    route_mad16_bcn03_standard = Route("MAD16-BCN03-STD-001", center_madrid, center_barcelona)
    route_mad16_bcn03_express = Route("MAD16-BCN03-EXP-006", center_madrid, center_barcelona)
    route_mad16_lpa06_standard = Route("MAD16-LPA06-STD-003", center_madrid, center_gran_canaria)
    route_mad16_lpa06_express = Route("MAD16-LPA06-EXP-009", center_madrid, center_gran_canaria)

    route_repo.add(route_mad16_bcn03_standard)
    route_repo.add(route_mad16_bcn03_express)
    route_repo.add(route_mad16_lpa06_standard)
    route_repo.add(route_mad16_lpa06_express)

    shipment_amazon_standard = Shipment("ABC123", "Amazon", "Juan Pérez", 1)
    shipment_zara_standard = Shipment("EXP456", "Zara", "María López", 2)
    shipment_apple_express = ExpressShipment("URG789", "Apple", "Carlos Gómez")
    shipment_alibaba_standard = Shipment("ALB882", "Alibaba", "Victor Aldama", 1)
    shipment_shein_fragile = FragileShipment("SHN114", "Shein", "Atteneri López", 2)

    shipment_repo.add(shipment_amazon_standard)
    shipment_repo.add(shipment_zara_standard)
    shipment_repo.add(shipment_apple_express)
    shipment_repo.add(shipment_alibaba_standard)
    shipment_repo.add(shipment_shein_fragile)

    return {
        "shipments": shipment_repo,
        "routes": route_repo,
        "centers": center_repo
    }
