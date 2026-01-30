# domain/express_shipment.py

from logisticaEnvios.domain.shipment import Shipment

class ExpressShipment(Shipment):
    def __init__(self, tracking_code, sender, recipient):

        super().__init__(
            tracking_code=tracking_code,
            sender=sender,
            recipient=recipient,
            priority=3,
        )

    @property
    def priority(self):
        return 3

    def increase_priority(self):
        raise ValueError("Un envío express ya tiene prioridad máxima.")

    @property
    def shipment_type(self):
        return "EXPRESS"