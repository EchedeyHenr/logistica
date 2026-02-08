# domain/fragile_shipment.py
"""Dominio: Especialización de Shipment para mercancía delicada con reglas de prioridad específicas."""

from logistica.domain.shipment import Shipment

class FragileShipment(Shipment):
    """
    Envío de mercancía delicada con restricciones de seguridad en su prioridad.

    Reglas de negocio específicas para envíos frágiles (RN-004, RN-006):
    1. Prioridad mínima: 2 (no puede tener prioridad 1)
    2. No puede disminuir prioridad por debajo de 2

    Justificación de negocio:
    - Mercancía frágil requiere manejo especial y mayor atención
    - Prioridad mínima garantiza que no se trate como envío estándar de baja prioridad
    - Previene degradación accidental a prioridad 1 que podría causar daños
    """

    def __init__(self, tracking_code, sender, recipient, priority=2):
        """
        Inicializa un envío frágil con validación de prioridad mínima.

        Args:
            tracking_code (str): Código único de seguimiento.
            sender (str): Remitente del envío.
            recipient (str): Destinatario del envío.
            priority (int): Prioridad mínima de 2. Por defecto 2.

        Raises:
            ValueError: Si se intenta asignar una prioridad inferior a 2 (RN-004).
        """

        # Regla de negocio RN-004: Prioridad mínima para frágiles es 2
        # Esto asegura que los envíos frágiles reciban al menos un nivel de atención media
        if priority < 2:
            raise ValueError("Un envío frágil no puede tener prioridad inferior a 2.")

        super().__init__(tracking_code, sender, recipient, priority)

        # Marcar como frágil para identificación rápida
        # Atributo privado para mantener encapsulamiento
        self._fragile = True


    @property
    def shipment_type(self):
        """
        Identifica el tipo de envío. Devuelve 'FRAGILE'.

        Sobrescribe el método de la clase base para proporcionar
        identificación específica del tipo de envío.

        Returns:
            str: 'FRAGILE' - identificador constante para este tipo.
        """
        return "FRAGILE"


    def decrease_priority(self):
        """
        Reduce la prioridad sin bajar del nivel 2.

        Regla de negocio RN-006: La prioridad de un envío frágil no puede ser inferior a 2.
        Esta restricción protege la mercancía delicada de ser tratada con baja prioridad.

        Raises:
            ValueError: Si la prioridad ya está en el límite inferior permitido (2).
        """

        # Validar que no se intente bajar de prioridad 2
        # Esta es una regla de negocio específica para envíos frágiles
        if self._priority <= 2:
            raise ValueError("La prioridad de un envío frágil no puede ser inferior a 2.")

        # Si pasa la validación, delegar al método padre para el decremento real
        self._priority -= 1


    def is_fragile(self):
        """
        Indica que el envío es frágil .Devuelve True.

        Método de conveniencia para verificación rápida de tipo.
        En un diseño con polimorfismo, normalmente se usaría shipment_type,
        pero este método proporciona una interfaz más semántica.

        Returns:
            bool: Siempre True para instancias de FragileShipment.
        """
        return True