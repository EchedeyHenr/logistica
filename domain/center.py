# domain/center.py

"""Dominio: Representa un nodo en la red logística con capacidad de almacenamiento."""

from logistica.domain.shipment import Shipment

class Center:
    """
    Representa un nodo central en la red logística encargado de la recepción y despacho de envíos.

    Responsabilidades:
    - Almacenar físicamente envíos en tránsito o entregados
    - Validar operaciones de entrada/salida de mercancía
    - Mantener inventario consistente con el estado del sistema

    Invariantes del dominio:
    1. Un envío no puede estar en dos centros simultáneamente
    2. Solo se pueden despachar envíos que están físicamente en el centro
    3. Los atributos básicos (ID, nombre, ubicación) son inmutables
    """

    def __init__(self, center_id, name, location):
        """
        Inicializa una nueva instancia de Center.

        Reglas de negocio aplicadas:
        - RN-010: Todos los campos son obligatorios y no vacíos
        - RN-009: center_id debe ser único (validado externamente en el repositorio)

        Args:
            center_id (str): ID único del centro.
            name (str): Nombre del centro.
            location (str): Ubicación física.

        Raises:
            ValueError: Si alguno de los argumentos está vacío o no es una cadena.
        """

        # Reglas de negocio: validación de datos obligatorios
        # Esto previene centros "fantasma" sin información esencial
        if not center_id or not isinstance(center_id, str):
            raise ValueError("El ID del centro no puede estar vacío.")
        if not name or not isinstance(name, str):
            raise ValueError("El nombre del centro no puede estar vacío.")
        if not location or not isinstance(location, str):
            raise ValueError("La ubicación del centro no puede estar vacía.")

        # Atributos inmutables después de creación
        # Esto garantiza identificación consistente en todo el sistema
        self.__center_id = center_id
        self.__name = name
        self.__location = location

        # Inventario de envíos almacenados físicamente en este centro
        # Se usa lista en lugar de dict porque el orden de inserción puede ser relevante
        # y el acceso por código se hace mediante búsqueda lineal (válido por ahora)
        self._shipments = []

    @property
    def center_id(self):
        """Devuelve el identificador único del centro. Propiedad de solo lectura."""
        return self.__center_id

    @property
    def name(self):
        """Devuelve el nombre del centro. Propiedad de solo lectura."""
        return self.__name

    @property
    def location(self):
        """Devuelve la ubicación del centro. Propiedad de solo lectura."""
        return self.__location

    def receive_shipment(self, shipment):
        """
        Registra la entrada de un envío en el centro logístico.

        Reglas de negocio aplicadas:
        - RN-011: No permite duplicados (mismo envío dos veces en el mismo centro)
        - Solo acepta objetos Shipment (o subtipos) válidos

        Este método se llama cuando:
        1. Un envío se asigna a una ruta (va al centro origen)
        2. Una ruta se completa (envíos van al centro destino)

        Args:
            shipment (Shipment): El objeto envío que se va a recibir.

        Raises:
            ValueError: Si el objeto no es una instancia de Shipment o si el envío ya está registrado en este centro.
        """

        # Validación de tipo: solo se pueden recibir objetos Shipment
        # Previene errores de tipo que podrían corromper el inventario
        if not isinstance(shipment, Shipment):
            raise ValueError("No es un envío, no se puede añadir al centro.")

        # Regla de negocio: no duplicar envíos en el mismo centro
        # Un envío físico no puede estar en dos lugares a la vez
        if self.has_shipment(shipment.tracking_code):
            raise ValueError("El envío ya se encuentra en el centro.")

        # Agregar al inventario
        self._shipments.append(shipment)

    def dispatch_shipment(self, shipment):
        """
        Gestiona la salida de un envío del centro, actualizando su estado.

        Reglas de negocio aplicadas:
        - RN-012: Solo se pueden despachar envíos que están en el inventario
        - Actualiza el estado del envío a IN_TRANSIT automáticamente

        Este método se llama cuando:
        1. Una ruta es despachada (todos sus envíos salen del centro origen)

        Args:
            shipment (Shipment): El envío que saldrá del centro.

        Returns:
            El objeto envío con el estado actualizado a 'IN_TRANSIT'.

        Raises:
            ValueError: Si el objeto no es un Shipment o si el envío no existe actualmente en el inventario del centro.
        """

        # Validación de tipo
        if not isinstance(shipment, Shipment):
            raise ValueError("No es un envío, no se puede eliminar del centro.")

        # Regla de negocio: solo despachar envíos que están físicamente presentes
        # Previene "despachos fantasma" de envíos que no están en el centro
        if not self.has_shipment(shipment.tracking_code):
            raise ValueError("El envío no se encuentra en el centro.")

        # Actualizar estado del envío a IN_TRANSIT
        # Esto sincroniza el estado lógico con el físico (sale del centro)
        shipment.update_status("IN_TRANSIT")

        # Remover del inventario (ya no está físicamente en el centro)
        self._shipments.remove(shipment)

        return shipment

    def list_shipments(self):
        """
        Proporciona una lista de todos los envíos almacenados en el centro.

        Returns:
            Una copia de la lista de envíos actuales.

        Nota: Devuelve copia para mantener encapsulamiento. Las modificaciones
        a la lista devuelta no afectan el inventario interno.
        """
        return self._shipments.copy()

    def has_shipment(self, tracking_code):
        """
        Verifica si un envío específico se encuentra en el centro mediante su código.

        Args:
            tracking_code (str): El código de seguimiento a buscar.

        Returns:
            True si el envío está presente, False en caso contrario.
        """

        # Búsqueda lineal: adecuado para inventarios pequeños
        # Para grandes volúmenes, se podrá optimizar con dict indexado
        return any(s.tracking_code == tracking_code for s in self._shipments)
