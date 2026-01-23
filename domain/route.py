# domain/route.py

class Route:
    def __init__(self, route_id, origin_center, destination_center):
        self.__route_id = route_id
        self.__origin_center = origin_center                    # LogisticCenter
        self.__destination_center = destination_center          # LogisticCenter
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
        pass

    def remove_shipment(self, shipment):
        pass

    def complete_route(self):
        pass

    def list_shipment(self):
        pass