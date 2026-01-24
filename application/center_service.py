# application/center_service.py

from logisticaEnvios.domain.logistic_center import LogisticCenter

class CenterService:

    def __init__(self, center_repo, shipment_repo):
        self._center_repo = center_repo
        self._shipment_repo = shipment_repo


    def register_center(self, center_id, name, location):
        center = self._center_repo.get_by_center_id(center_id)
        if center is not None:
            raise ValueError("Ya hay registrado un centro con ese identificador.")

        center = LogisticCenter(center_id, name, location)
        self._center_repo.add(center)

    def list_centers(self):
        centers = self._center_repo.list_all()

        result = []
        for center in centers:
            center_id = center.center_id
            name = center.name
            location = center.location
            result.append((center_id, name, location))
        return result

    def get_center(self, center_id):
        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError("No existe un centro con ese identificador.")
        return center

    def receive_shipment(self, tracking_code, center_id):
        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError("No existe un centro con ese identificador.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código.")

        center.receive_shipment(shipment)
        self._center_repo.add(center)

    def dispatch_shipment(self, tracking_code, center_id):
        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError("No existe un centro con ese identificador.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código.")

        center.dispatch_shipment(shipment)
        self._center_repo.add(center)

    def list_shipments_in_center(self, center_id):
        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError("No existe un centro con ese identificador.")
        return center.list_shipments()