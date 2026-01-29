# application/center_service.py

from logisticaEnvios.domain.logistic_center import LogisticCenter

class CenterService:

    def __init__(self, center_repo, shipment_repo):
        self._center_repo = center_repo
        self._shipment_repo = shipment_repo


    def register_center(self, center_id, name, location):
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")
        if not name.strip():
            raise ValueError("El nombre del centro no puede estar vacío.")
        if not location.strip():
            raise ValueError("La ubicación del centro no puede estar vacía.")

        center = self._center_repo.get_by_center_id(center_id)
        if center is not None:
            raise ValueError(f"Ya hay registrado un centro con el identificador '{center_id}'.")

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
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")

        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError(f"No existe un centro con el identificador '{center_id}'.")
        return center

    def receive_shipment(self, tracking_code, center_id):
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")
        if not tracking_code.strip():
            raise ValueError("El código de seguimiento del envío no puede estar vacío.")

        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError(f"No existe un centro con el identificador '{center_id}'.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        center.receive_shipment(shipment)
        self._center_repo.add(center)

    def dispatch_shipment(self, tracking_code, center_id):
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")
        if not tracking_code.strip():
            raise ValueError("El código de seguimiento del envío no puede estar vacío.")

        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError(f"No existe un centro con el identificador '{center_id}'.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        center.dispatch_shipment(shipment)
        self._center_repo.add(center)

    def list_shipments_in_center(self, center_id):
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")

        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError(f"No existe un centro con el identificador '{center_id}'.")
        return center.list_shipments()