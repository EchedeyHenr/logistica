# domain/logistic_center.py

class LogisticCenter:
    def __init__(self, center_id, name, location):
        self.__center_id = center_id
        self.__name = name
        self.__location = location
        self._shipment = []

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
        pass

    def dispatch_shipment(self, shipment):
        pass

    def list_shipments(self):
        pass

    def has_shipment(self, tracking_code):
        pass
