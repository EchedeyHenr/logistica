# domain/fragile_shipment.py

from logisticaEnvios.domain.shipment import Shipment

class FragileShipment(Shipment):
    def __init__(self, tracking_code, sender, recipient, priority=2):
        if priority < 2:
            raise ValueError("Un envío frágil no puede tener prioridad inferior a 2.")

        super().__init__(tracking_code, sender, recipient, priority)
        self._fragile = True


    @property
    def shipment_type(self):
        return "FRAGILE"


    def decrease_priority(self):
        if self._priority <= 2:
            raise ValueError("La prioridad de un envío frágil no puede ser inferior a 2.")
        self._priority -= 1


    def is_fragile(self):
        return True