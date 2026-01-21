# domain/shipment.py

# _current_status: str : "REGISTERED", "IN_TRANSIT", "DELIVERED"
# _status_history: list[str]
# _priority: int : 1 (normal), 2 (mid), 3 (high)

class Shipment:
    def __init__(self, tracking_code, sender, recipient, priority=1, assigned_route=None):
        self.__tracking_code = tracking_code
        self.__sender = sender
        self.__recipient = recipient
        self._current_status = "REGISTERED"
        self._status_history = [self._current_status]
        self._priority = priority
        self._assigned_route = assigned_route

    @property
    def tracking_code(self):
        return self.__tracking_code

    @tracking_code.setter
    def tracking_code(self, new_tracking_code):
        self.__tracking_code = new_tracking_code

    @property
    def sender(self):
        return self.__sender

    @sender.setter
    def sender(self, new_sender):
        self.__sender = new_sender

    @property
    def recipient(self):
        return self.__recipient

    @recipient.setter
    def recipient(self, new_recipient):
        self.__recipient = new_recipient

    @property
    def current_status(self):
        return self._current_status

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, new_priority):
        if new_priority < 1 or new_priority > 3:
            raise ValueError("La prioridad debe estar entre 1 y 3.")
        self._priority = new_priority

    @property
    def assigned_route(self):
        return self._assigned_route

    def update_status(self, new_status):
        new_status_format = new_status.upper()
        self.can_change_to(new_status_format)
        self._current_status = new_status_format
        self._status_history.append(self._current_status)

    def can_change_to(self, new_status):
        new_status_format = new_status.upper()
        valid_transitions = {"REGISTERED": "IN_TRANSIT",
                             "IN_TRANSIT": "DELIVERED"}
        if valid_transitions.get(self._current_status) != new_status_format:
            raise ValueError(f"Transición no permitida: de {self._current_status} a {new_status_format}")

    def assign_route(self, new_assigned_route):
        self._assigned_route = new_assigned_route

    def remove_route(self):
        if not self.is_assigned_to_route():
            raise ValueError("No hay ruta asignada para eliminar.")
        self._assigned_route = None

    def is_assigned_to_route(self):
        return self._assigned_route is not None

    def is_delivered(self):
        return self._current_status == "DELIVERED"

    def get_status_history(self):
        return self._status_history.copy()

    def increase_priority(self):
        if self._priority > 2:
            raise ValueError("No se puede aumentar la prioridad del envío.")
        self._priority += 1

    def decrease_priority(self):
        if self._priority < 2:
            raise ValueError("No se puede disminuir la prioridad del envío.")
        self._priority -= 1