# domain/route.py

"""Dominio: Gestiona el transporte de envíos entre centros logísticos."""

import re
from logistica.domain.shipment import Shipment

class Route:
    """
    Gestiona el transporte de envíos entre un centro de origen y uno de destino.

    Responsabilidades:
    - Agrupar envíos para transporte conjunto entre dos centros
    - Coordinar el ciclo de vida de los envíos durante el transporte
    - Mantener consistencia entre estado de ruta y estado de envíos

    Invariantes del dominio:
    1. Origen y destino deben ser centros diferentes (RN-013)
    2. Solo rutas activas pueden recibir nuevos envíos (RN-015)
    3. Al completar ruta, todos los envíos pasan a estado DELIVERED
    """

    def __init__(self, route_id, origin_center, destination_center):
        """
        Crea una ruta activa entre dos centros distintos.

        Reglas de negocio aplicadas:
        - RN-014: Centros de origen y destino deben estar definidos (no None)
        - RN-013: Origen y destino no pueden ser el mismo centro
        - RN-035: El identificador de una ruta debe cumplir un patrón de forma.

        Args:
            route_id (str): Identificador único de la ruta.
            origin_center (Center): Centro donde inicia el trayecto.
            destination_center (Center): Centro donde finaliza el trayecto.

        Raises:
            ValueError: Si los centros o route_id no están definidos, si los centros son idénticos o si el route_id no
            cumple con el patrón de forma.
        """

        if not isinstance(route_id, str) or not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")
        route_id = route_id.upper().strip()
        # Patrón: origen (ej. MAD01) - destino (ej. BCN02) - tipo (STD/FRG/EXP) - 3 dígitos
        if not re.match(r'^[A-Z]{3,4}\d{2}-[A-Z]{3,4}\d{2}-(STD|FRG|EXP)-\d{3}$', route_id):
            raise ValueError("El ID de la ruta debe tener el formato ORIGEN-DESTINO-TIPO-999 (ej. MAD01-BCN02-FRG-001).")

        # Validación: ambos centros deben existir
        # Previene rutas "fantasma" sin puntos definidos
        if origin_center is None or destination_center is None:
            raise ValueError("Los centros de origen y destino deben estar definidos.")

        # Regla de negocio RN-013: origen y destino deben ser diferentes
        # Rutas circulares (mismo origen y destino) no tienen sentido logístico
        if origin_center == destination_center:
            raise ValueError("El centro de origen y destino no pueden ser el mismo.")

        # Atributos inmutables después de creación
        self.__route_id = route_id
        self.__origin_center = origin_center
        self.__destination_center = destination_center

        # Lista de envíos asignados a esta ruta
        # Se mantiene como lista para preservar orden de asignación
        self._shipments = []

        # Estado de la ruta: True = activa (puede recibir envíos), False = completada
        # Inicialmente todas las rutas están activas
        self._active = True

    @property
    def route_id(self):
        """Devuelve el identificador único de la ruta. Propiedad de solo lectura."""
        return self.__route_id

    @property
    def origin_center(self):
        """Devuelve el objeto del centro de origen. Propiedad de solo lectura."""
        return self.__origin_center

    @property
    def destination_center(self):
        """Devuelve el objeto del centro de destino. Propiedad de solo lectura."""
        return self.__destination_center

    @property
    def is_active(self):
        """
        Indica si la ruta está activa y permite añadir envíos.

        Returns:
            bool: True si la ruta está activa, False si está completada.
        """
        return self._active

    def add_shipment(self, shipment):
        """
        Añade un envío a la ruta y lo registra en el inventario del centro de origen.

        Reglas de negocio aplicadas:
        - RN-015: Solo rutas activas pueden recibir envíos
        - Mantiene relación bidireccional: ruta conoce envío y envío conoce ruta
        - Registra el envío en el centro de origen (físicamente llega al centro)

        Args:
            shipment (Shipment): El objeto envío a transportar.

        Raises:
            ValueError: Si la ruta ya ha sido completada (inactiva).
        """

        # Regla de negocio RN-015: solo rutas activas pueden recibir envíos
        # Rutas completadas no deben modificarse
        if not self.is_active:
            raise ValueError("La ruta no está activa.")

        # Agregar a la lista interna de envíos de esta ruta
        self._shipments.append(shipment)

        # Establecer relación bidireccional: envío conoce su ruta asignada
        shipment.assign_route(self.route_id)

        # Registrar el envío físicamente en el centro de origen
        # Esto sincroniza el estado lógico (asignación) con el físico (ubicación)
        self.origin_center.receive_shipment(shipment)

    def remove_shipment(self, shipment):
        """
        Elimina un envío de la ruta y desvincula la ruta del objeto envío.

        Utilizado cuando:
        1. Se cancela la asignación de un envío a la ruta
        2. Se necesita reasignar un envío a otra ruta

        Args:
            shipment (Shipment): El envío que se desea retirar de la ruta.
        """

        # Remover de la lista interna
        self._shipments.remove(shipment)

        # Desvincular la relación bidireccional
        shipment.remove_route()

    def complete_route(self):
        """
        Finaliza el trayecto, transfiere los paquetes al centro de destino y los marca como entregados.

        Flujo de operaciones:
        1. Marcar ruta como inactiva (no puede recibir más envíos)
        2. Transferir cada envío al centro de destino
        3. Actualizar estado de cada envío a DELIVERED
        4. Limpiar la lista de envíos (ya no están en tránsito)

        Reglas de negocio:
        - Solo rutas activas pueden completarse
        - Todos los envíos deben actualizarse a estado DELIVERED
        - Los envíos se registran físicamente en el centro destino

        Raises:
            ValueError: Si la ruta ya estaba inactiva.
        """

        # Validar que la ruta esté activa
        if not self._active:
            raise ValueError("La ruta no está activa.")

        # Cambiar estado de la ruta a inactiva
        # A partir de este punto, no se pueden añadir más envíos
        self._active = False

        # Procesar cada envío en la ruta
        for shipment in self._shipments:
            # 1. Registrar el envío en el centro de destino (llega físicamente)
            self.__destination_center.receive_shipment(shipment)

            # 2. Actualizar estado del envío a DELIVERED (ciclo de vida completo)
            shipment.update_status("DELIVERED")

        # Limpiar la lista de envíos
        # Los envíos ya no están "en la ruta", están en el centro destino
        self._shipments.clear()

    def list_shipment(self):
        """
        Devuelve una lista de los envíos asociados actualmente a la ruta.

        Returns:
            Copia de la lista de envíos en tránsito por esta ruta.

        Nota: Devuelve copia para mantener encapsulamiento. Las modificaciones
        a la lista devuelta no afectan la lista interna de la ruta.
        """
        return self._shipments.copy()