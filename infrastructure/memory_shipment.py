# infrastructure/memory.py
from logisticaEnvios.domain.shipment_repository import ShipmentRepository
from logisticaEnvios.domain.shipment import Shipment

class ShipmentRepositoryMemory(ShipmentRepository):
    def __init__(self):
        self._by_tracking_code = {}

    def add(self, shipment):
        key = shipment.tracking_code.lower()
        self._by_tracking_code[key] = shipment

    def remove(self, tracking_code):
        tracking_code = (tracking_code or "").strip()
        if not tracking_code:
            return False

        key = tracking_code.lower()
        if key in self._by_tracking_code:
            del self._by_tracking_code[key]
            return True
        return False

    def get_by_tracking_code(self, tracking_code):
        tracking_code = (tracking_code or "").strip()
        if not tracking_code:
            return None
        return self._by_tracking_code.get(tracking_code.lower())

    def list_all(self):
        return list(self._by_tracking_code.values())