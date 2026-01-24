# application/services.py

from logisticaEnvios.domain.shipment import Shipment
from logisticaEnvios.domain.shipment_repository import ShipmentRepository

class ShipmentService:
    def __init__(self, repo):
        self._repo = repo

    def register_shipment(self, tracking_code, sender, recipient, priority=1):
        if self._repo.get_by_tracking_code(tracking_code) is not None:
            raise ValueError("Ya existe un envío con ese código.")
        shipment = Shipment(tracking_code, sender, recipient, priority)
        self._repo.add(shipment)

    def assign_shipment_to_route(self, tracking_code, route_id):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código")
        shipment.assign_route(route_id)
        self._repo.add(shipment)

    def remove_shipment_from_route(self, tracking_code):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None or not shipment.is_assigned_to_route():
            raise ValueError("No hay ningún envío con ese código o ruta")
        shipment.remove_route()
        self._repo.add(shipment)

    def update_shipment_status(self, tracking_code, new_status):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código")
        shipment.update_status(new_status)
        self._repo.add(shipment)

    def increase_shipment_priority(self, tracking_code):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código")
        shipment.increase_priority()
        self._repo.add(shipment)

    def decrease_shipment_priority(self, tracking_code):
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código")
        shipment.decrease_priority()
        self._repo.add(shipment)

    def list_shipments(self):
        shipments = self._repo.list_all()

        result = []
        for shipment in shipments:
            tracking_code = shipment.tracking_code
            current_status = shipment.current_status
            priority = shipment.priority
            assigned_route = shipment.assigned_route
            result.append((tracking_code, current_status, priority, assigned_route))
        result.sort(key=lambda item: item[0].lower())
        return result

