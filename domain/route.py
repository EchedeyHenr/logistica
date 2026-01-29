# domain/route.py
from logisticaEnvios.domain.shipment import Shipment

class Route:
    def __init__(self, route_id, origin_center, destination_center):
        if origin_center is None or destination_center is None:
            raise ValueError("Los centros de origen y destino deben estar definidos.")
        if origin_center == destination_center:
            raise ValueError("El centro de origen y destino no pueden ser el mismo.")

        self.__route_id = route_id
        self.__origin_center = origin_center
        self.__destination_center = destination_center
        self._shipments = []
        self._active = True

    @property
    def route_id(self):
        return self.__route_id

    @property
    def origin_center(self):
        return self.__origin_center

    @property
    def destination_center(self):
        return self.__destination_center

    @property
    def is_active(self):
        return self._active

    def add_shipment(self, shipment):
        if not self.is_active:
            raise ValueError("La ruta no está activa.")
        self._shipments.append(shipment)
        shipment.assign_route(self.route_id)

        self.origin_center.receive_shipment(shipment)

    def remove_shipment(self, shipment):
        self._shipments.remove(shipment)
        shipment.remove_route()

    def complete_route(self):
        if not self._active:
            raise ValueError("La ruta no está activa.")
        self._active = False

        for shipment in self._shipments:
            self.__destination_center.receive_shipment(shipment)
            shipment.update_status("DELIVERED")
        self._shipments.clear()

    def list_shipment(self):
        return self._shipments.copy()