# application/services.py

from logisticaEnvios.domain.shipment import Shipment
from logisticaEnvios.domain.fragile_shipment import FragileShipment
from logisticaEnvios.domain.express_shipment import ExpressShipment
from logisticaEnvios.domain.shipment_repository import ShipmentRepository

class ShipmentService:

    def __init__(self, repo):
        self._repo = repo


    def register_shipment(self, tracking_code, sender, recipient, priority=1, shipment_type="standard"):
        if self._repo.get_by_tracking_code(tracking_code) is not None:
            raise ValueError(f"Ya existe un envío con el código de seguimiento '{tracking_code}'.")

        shipment_type = shipment_type.lower()

        if shipment_type == "standard":
            shipment = Shipment(tracking_code, sender, recipient, priority)
        elif shipment_type == "fragile":
            shipment = FragileShipment(tracking_code, sender, recipient, priority)
        elif shipment_type == "express":
            shipment = ExpressShipment(tracking_code, sender, recipient)
        else:
            raise ValueError("Tipo de envío no válido.")

        self._repo.add(shipment)


    def update_shipment_status(self, tracking_code, new_status):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")
        shipment.update_status(new_status)
        self._repo.add(shipment)


    def increase_shipment_priority(self, tracking_code):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")
        shipment.increase_priority()
        self._repo.add(shipment)


    def decrease_shipment_priority(self, tracking_code):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")
        shipment.decrease_priority()
        self._repo.add(shipment)


    def list_shipments(self):
        shipments = self._repo.list_all()

        result = []
        for shipment in shipments:
            tracking_code = shipment.tracking_code
            current_status = shipment.current_status
            priority = shipment.priority
            shipment_type = shipment.shipment_type
            assigned_route = shipment.assigned_route
            result.append((tracking_code, current_status, priority, shipment_type, assigned_route))
        result.sort(key=lambda item: item[0].lower())
        return result

    def get_shipment(self, tracking_code):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No existe el envío con código de seguimiento '{tracking_code}'.")
        return shipment
