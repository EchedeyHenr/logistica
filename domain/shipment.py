# domain/shipment.py
"""Dominio: Entidad base que representa un envío en el sistema logístico."""

class Shipment:
    """
    Representa un envío estándar dentro del sistema logístico.

    Esta clase encapsula las reglas de negocio fundamentales para el manejo de envíos:
    - Validación de datos de entrada (código, remitente, destinatario, prioridad)
    - Gestión del ciclo de vida (estados REGISTERED → IN_TRANSIT → DELIVERED)
    - Control de prioridades (1-3) con incrementos/decrementos validados
    - Trazabilidad mediante historial de estados

    Invariantes del dominio:
    1. El código de seguimiento debe ser único en el sistema
    2. La prioridad siempre está en el rango {1, 2, 3}
    3. Las transiciones de estado siguen una secuencia estricta
    4. El historial de estados es completo e inmutable para consulta
    """

    def __init__(self, tracking_code, sender, recipient, priority=1):
        """
        Inicializa una nueva instancia de Shipment con validaciones de negocio.

        Reglas de negocio aplicadas:
        - RN-002: Campos obligatorios no vacíos
        - RN-003: Prioridad en rango válido (1, 2 o 3)
        - RN-008: Estado inicial siempre REGISTERED

        Args:
            tracking_code (str): Identificador único del envío.
            sender (str): Nombre del remitente.
            recipient (str): Nombre del destinatario.
            priority (int, opcional): Prioridad del envío (1, 2 o 3). Por defecto es 1.

        Raises:
            ValueError: Si los datos de entrada están vacíos, no son cadenas o la prioridad es inválida.
        """
        # Regla de negocio: datos básicos son obligatorios y deben ser strings no vacíos
        # Esto previene envíos sin información esencial que romperían la trazabilidad
        if not tracking_code or not isinstance(tracking_code, str):
            raise ValueError("El código de seguimiento no puede estar vacío.")
        if not sender or not isinstance(sender, str):
            raise ValueError("El remitente no puede estar vacío.")
        if not recipient or not isinstance(recipient, str):
            raise ValueError("El destinatario no puede estar vacío.")
        if priority not in (1, 2, 3):
            raise ValueError("La prioridad debe ser 1, 2 o 3.")

        # Atributos inmutables después de la creación (garantizan consistencia)
        self.__tracking_code = tracking_code
        self.__sender = sender
        self.__recipient = recipient

        # Regla de negocio: estado inicial siempre REGISTERED (RN-008)
        self._current_status = "REGISTERED"

        # Historial de estados para trazabilidad completa
        # Se inicializa con el primer estado para mantener registro desde la creación
        self._status_history = [self._current_status]

        # Prioridad mutable pero con validaciones en métodos específicos
        self._priority = priority

        # Ruta asignada, None indica que no está asignado a ninguna ruta
        # Se mantiene como string (ID de ruta) para evitar acoplamiento circular
        self._assigned_route = None

    @property
    def tracking_code(self):
        """Devuelve el código de seguimiento único."""
        return self.__tracking_code

    @property
    def sender(self):
        """Devuelve el nombre del remitente."""
        return self.__sender

    @property
    def recipient(self):
        """Devuelve el nombre del destinatario."""
        return self.__recipient

    @property
    def current_status(self):
        """Devuelve el estado actual (REGISTERED, IN_TRANSIT, DELIVERED)."""
        return self._current_status

    @property
    def priority(self):
        """Devuelve el nivel de prioridad actual.

        Regla de negocio: prioridad siempre en {1, 2, 3}
        Los cambios se realizan mediante increase_priority/decrease_priority
        para mantener las validaciones de negocio.
        """
        return self._priority

    @property
    def assigned_route(self):
        """Devuelve el ID de la ruta asignada o None.

        Nota: Se almacena como string para mantener bajo acoplamiento.
        La relación bidireccional se gestiona en la clase Route.
        """
        return self._assigned_route

    @property
    def shipment_type(self):
        """Identifica el tipo de envío. Por defecto 'STANDARD'.

        Método polimórfico: las subclases (FragileShipment, ExpressShipment)
        sobrescriben este método para retornar su tipo específico.
        """
        return "STANDARD"

    def update_status(self, new_status):
        """
        Actualiza el estado actual del envío y lo registra en el historial.

        Regla de negocio aplicada: RN-007 (Secuencia de estados válida)
        Solo se permiten transiciones:
        - REGISTERED → IN_TRANSIT
        - IN_TRANSIT → DELIVERED

        Esta restricción garantiza un ciclo de vida coherente y trazable.

        Args:
            new_status (str): Nuevo estado (ej. 'IN_TRANSIT', 'DELIVERED').

        Raises:
            ValueError: Si la transición de estado no es válida.
        """
        new_status_format = new_status.upper()

        # Validar que la transición sea permitida antes de modificar estado
        self.can_change_to(new_status_format)

        self._current_status = new_status_format

        # Registrar en historial para trazabilidad completa
        # El historial es de solo consulta, no se puede modificar externamente
        self._status_history.append(self._current_status)

    def can_change_to(self, new_status):
        """
        Valida si una transición de estado es aceptada según reglas de negocio.

        Flujo: REGISTERED -> IN_TRANSIT -> DELIVERED.
        Esta validación previene estados inconsistentes (ej: saltar a DELIVERED sin pasar por IN_TRANSIT)

        Args:
            new_status (str): Estado destino a validar.

        Raises:
            ValueError: Si la transición no es permitida.
        """
        new_status_format = new_status.upper()
        valid_transitions = {
            "REGISTERED": "IN_TRANSIT",
            "IN_TRANSIT": "DELIVERED"
        }

        # Regla de negocio: solo transiciones definidas en valid_transitions son permitidas
        # Esto asegura un flujo de trabajo lógico y predecible
        if valid_transitions.get(self._current_status) != new_status_format:
            raise ValueError(f"Transición no permitida: de {self._current_status} a {new_status_format}")

    def assign_route(self, new_assigned_route):
        """
        Asocia el envío a una ruta específica.

        Regla de negocio: un envío solo puede estar asignado a una ruta a la vez
        La validación de esta restricción se realiza en RouteService.assign_shipment_to_route()

        Args:
            new_assigned_route (str): Identificador de la ruta a asignar.

        Raises:
            ValueError: Si la ruta proporcionada es None.
        """
        if new_assigned_route is None:
            raise ValueError("La ruta asignada no puede ser None.")

        self._assigned_route = new_assigned_route

    def remove_route(self):
        """
        Elimina la asociación con la ruta actual.

        Utilizado cuando un envío se retira de una ruta o cuando la ruta se completa.
        Mantiene la integridad de la relación bidireccional con Route.

        Raises:
            ValueError: Si el envío no tiene ninguna ruta asignada.
        """
        if not self.is_assigned_to_route():
            raise ValueError("No hay ruta asignada para eliminar.")
        self._assigned_route = None

    def is_assigned_to_route(self):
        """
        Indica si el envío ya tiene una ruta vinculada.

        Returns:
            bool: True si tiene ruta asignada, False en caso contrario.
        """
        return self._assigned_route is not None

    def is_delivered(self):
        """
        Indica si el envío ha llegado a su destino.

        Returns:
            bool: True si el estado es DELIVERED (estado final del ciclo de vida).
        """
        return self._current_status == "DELIVERED"

    def get_status_history(self):
        """
        Devuelve una copia del historial de estados por los que ha pasado el envío.

        Returns:
            List[str]: Copia del historial (para prevenir modificaciones externas).

        Nota: Devuelve copia para mantener encapsulamiento. El historial es
        inmutable desde fuera de la clase para garantizar trazabilidad confiable.
        """
        return self._status_history.copy()

    def increase_priority(self):
        """
        Aumenta en 1 el nivel de prioridad.

        Reglas de negocio:
        - No se puede aumentar si ya está en prioridad máxima (3)
        - Para envíos Express (prioridad fija 3), este método es sobrescrito
        - Para envíos Frágiles, hay restricción adicional (no implementada aquí)

        Raises:
            ValueError: Si la prioridad ya es la máxima (3).
        """
        if self._priority > 2:
            raise ValueError("No se puede aumentar la prioridad del envío.")
        self._priority += 1

    def decrease_priority(self):
        """
        Disminuye en 1 el nivel de prioridad.

        Reglas de negocio:
        - No se puede disminuir si ya está en prioridad mínima (1)
        - Para envíos Frágiles, no puede bajar de 2 (restricción en subclase)

        Raises:
            ValueError: Si la prioridad ya es la mínima (1).
        """
        if self._priority < 2:
            raise ValueError("No se puede disminuir la prioridad del envío.")
        self._priority -= 1