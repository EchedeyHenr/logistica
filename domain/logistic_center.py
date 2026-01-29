# domain/logistic_center.py
from logisticaEnvios.domain.shipment import Shipment

class LogisticCenter:
    def __init__(self, center_id, name, location):
        if not center_id or not isinstance(center_id, str):
            raise ValueError("El ID del centro no puede estar vacío.")
        if not name or not isinstance(name, str):
            raise ValueError("El nombre del centro no puede estar vacío.")
        if not location or not isinstance(location, str):
            raise ValueError("La ubicación del centro no puede estar vacía.")

        self.__center_id = center_id
        self.__name = name
        self.__location = location
        self._shipments = []

    @property
    def center_id(self):
        return self.__center_id

    @property
    def name(self):
        return self.__name

    @property
    def location(self):
        return self.__location

    def receive_shipment(self, shipment):
        if not isinstance(shipment, Shipment):
            raise ValueError("No es un envío, no se puede añadir al centro.")
        if self.has_shipment(shipment.tracking_code):
            raise ValueError("El envío ya se encuentra en el centro.")
        self._shipments.append(shipment)

    def dispatch_shipment(self, shipment):
        if not isinstance(shipment, Shipment):
            raise ValueError("No es un envío, no se puede eliminar del centro.")
        if not self.has_shipment(shipment.tracking_code):
            raise ValueError("El envío no se encuentra en el centro.")
        shipment.update_status("IN_TRANSIT")
        self._shipments.remove(shipment)
        return shipment

    def list_shipments(self):
        return self._shipments.copy()

    def has_shipment(self, tracking_code):
        return any(s.tracking_code == tracking_code for s in self._shipments)
