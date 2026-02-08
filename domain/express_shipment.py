# domain/express_shipment.py

"""Dominio: Especialización de Shipment para envíos urgentes con prioridad máxima fija."""

from logistica.domain.shipment import Shipment

class ExpressShipment(Shipment):
    """
    Envío urgente con prioridad máxima (3) bloqueada.

    Reglas de negocio específicas para envíos express (RN-005):
    1. Prioridad siempre es 3 (máxima)
    2. Prioridad no modificable (ni aumento ni disminución)

    Justificación de negocio:
    - Envíos express pagan premium por servicio prioritario
    - Prioridad fija garantiza tratamiento consistente como máxima urgencia
    - Elimina confusión sobre niveles de prioridad dentro de express
    """
    def __init__(self, tracking_code, sender, recipient):
        """
        Inicializa un envío express con prioridad automática de 3.

        Args:
            tracking_code (str): Código único de seguimiento.
            sender (str): Remitente del envío.
            recipient (str): Destinatario del envío.

        Nota: No recibe parámetro priority porque siempre es 3.
        """

        # Regla de negocio: prioridad siempre 3 para express
        # Se pasa 3 como valor fijo al constructor padre
        super().__init__(
            tracking_code=tracking_code,
            sender=sender,
            recipient=recipient,
            priority=3,  # Valor fijo, no parametrizable
        )

    @property
    def priority(self):
        """
        Prioridad fija: siempre devuelve 3.

        Sobrescribe la propiedad de la clase base para hacerla de solo lectura
        y con valor constante. Esto implementa la regla RN-005.

        Returns:
            int: Siempre 3 (prioridad máxima en el sistema).
        """
        return 3

    def increase_priority(self):
        """
        No permitido para envíos express.

        Regla de negocio: envíos express ya tienen prioridad máxima (3)
        No tiene sentido aumentar lo que ya está en el máximo.

        Raises:
            ValueError: Siempre, porque ya posee prioridad máxima.
        """
        raise ValueError("Un envío express ya tiene prioridad máxima.")

    @property
    def shipment_type(self):
        """
        Identifica el tipo de envío. Devuelve 'EXPRESS'.

        Sobrescribe el método de la clase base para proporcionar
        identificación específica del tipo de envío.

        Returns:
            str: 'EXPRESS' - identificador constante para este tipo.
        """
        return "EXPRESS"