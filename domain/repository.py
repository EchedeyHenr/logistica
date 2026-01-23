# domain/repository.py
#from logisticaEnvios.domain.shipment import Shipment
class Repository:
    def add(self, shipment):
        raise NotImplementedError

    def remove(self, tracking_code):
        raise NotImplementedError

    def get_by_tracking_code(self, tracking_code):
        raise NotImplementedError

    def list_all(self):
        raise NotImplementedError