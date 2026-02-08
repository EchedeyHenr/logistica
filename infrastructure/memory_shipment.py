# infrastructure/memory_shipment.py
"""
Repositorio en memoria para la gestión persistente de envíos logísticos.

Implementa la interfaz ShipmentRepository utilizando un diccionario en memoria
para almacenar y recuperar envíos de manera temporal, ideal para entornos de
desarrollo, pruebas unitarias o prototipos rápidos.

Este repositorio soporta todos los tipos de envíos (STANDARD, FRAGILE, EXPRESS)
y normaliza los códigos de seguimiento a minúsculas para garantizar búsquedas
case-insensitive. No persiste los datos entre ejecuciones del programa.

Attributes:
    _by_tracking_code (dict): Diccionario que mapea códigos de seguimiento
    (en minúsculas) a objetos Shipment o sus subtipos.
"""

from logistica.domain.shipment_repository import ShipmentRepository
from logistica.domain.shipment import Shipment

class ShipmentRepositoryMemory(ShipmentRepository):
    """
    Implementación en memoria del repositorio de envíos logísticos.

    Proporciona operaciones CRUD para entidades Shipment y sus subtipos (FragileShipment, ExpressShipment)
    utilizando un diccionario Python.

    Características:
        - Almacenamiento temporal en memoria RAM
        - Búsquedas insensibles a mayúsculas/minúsculas
        - Soporte para polimorfismo (todos los subtipos de Shipment)
        - Operaciones de tiempo constante O(1) para acceso por código

    Notes:
        La eliminación de envíos no valida si están asignados a rutas activas o si se encuentran en centros logísticos.
    """
    def __init__(self):
        """
        Inicializa un nuevo repositorio de envíos en memoria.

        Crea un diccionario vacío que almacenará los envíos indexados por
        sus códigos de seguimiento normalizados a minúsculas.
        """
        self._by_tracking_code = {}

    def add(self, shipment):
        """
        Almacena o actualiza un envío en el repositorio.

        Sobrescribe cualquier envío existente con el mismo código de seguimiento (ignorando mayúsculas/minúsculas)
        sin generar advertencia.

        Args:
            shipment (Shipment): Instancia del envío a almacenar. Puede ser Shipment, FragileShipment o ExpressShipment.
        """
        key = shipment.tracking_code.lower()
        self._by_tracking_code[key] = shipment

    def remove(self, tracking_code):
        """
        Elimina un envío del repositorio por su código de seguimiento.

        Args:
            tracking_code (str): Código de seguimiento del envío a eliminar.

        Returns:
            True si el envío existía y fue eliminado exitosamente, False si el código está vacío o el envío no existe.
        """
        tracking_code = (tracking_code or "").strip()
        if not tracking_code:
            return False

        key = tracking_code.lower()
        if key in self._by_tracking_code:
            del self._by_tracking_code[key]
            return True
        return False

    def get_by_tracking_code(self, tracking_code):
        """
        Recupera un envío por su código de seguimiento único.

        Args:
            tracking_code (str): Código de seguimiento del envío a buscar.

        Returns:
            La instancia del envío si se encuentra, None si no existe o el código está vacío.
            El tipo concreto puede ser Shipment, FragileShipment o ExpressShipment.
        """
        tracking_code = (tracking_code or "").strip()
        if not tracking_code:
            return None
        return self._by_tracking_code.get(tracking_code.lower())

    def list_all(self):
        """
        Obtiene todos los envíos almacenados en el repositorio.

        Returns:
            Lista con todas las instancias de envíos almacenadas. El orden no está garantizado
            y depende del diccionario interno.

        Notes:
            La lista devuelta es una copia superficial. Modificar los objetos en la lista afectará
            a los objetos almacenados en el repositorio. Para obtener una copia profunda, implemente
            la lógica en la capa de aplicación según sea necesario.
        """
        return list(self._by_tracking_code.values())