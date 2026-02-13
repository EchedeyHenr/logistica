# application/route_service.py

from logistica.domain.route import Route

class RouteService:
    """
    Servicio de aplicación encargado de coordinar la lógica de negocio de las rutas.

    Responsabilidades:
    - Orquestar casos de uso relacionados con rutas
    - Coordinar múltiples entidades (Route, Shipment, Center)
    - Validar reglas de negocio que involucran múltiples agregados
    - Mantener consistencia en operaciones transaccionales implícitas

    Complejidad: Este es el servicio más complejo porque:
    1. Coordina tres repositorios diferentes
    2. Maneja relaciones bidireccionales
    3. Implementa operaciones transaccionales sin mecanismo explícito
    """

    def __init__(self, route_repo, shipment_repo, center_repo):
        """
        Inicializa el servicio con los repositorios necesarios.

        Dependencias múltiples: Necesita tres repositorios porque:
        - route_repo: para operaciones CRUD de rutas
        - shipment_repo: para actualizar estado de envíos
        - center_repo: para validar existencia de centros

        Patrón: Constructor Injection
        - Todas las dependencias se inyectan al crear el servicio
        - Facilita testing (mockear cada repositorio)

        Args:
            route_repo: Instancia del repositorio de rutas.
            shipment_repo: Instancia del repositorio de envíos.
            center_repo: Instancia del repositorio de centros logísticos.
        """
        self._route_repo = route_repo
        self._shipment_repo = shipment_repo
        self._center_repo = center_repo


    def create_route(self, route_id, origin_center_id, destination_center_id):
        """
        Crea una nueva ruta y la persiste en el sistema.

        Caso de uso: UC-09 (Crear Nueva Ruta)
        Reglas de negocio aplicadas:
        - RN-013: Origen y destino deben ser diferentes (valida en dominio)
        - RN-014: Centros deben existir (validación de aplicación)
        - Unicidad de route_id (validación de aplicación)

        Validaciones en dos niveles:
        1. Aplicación: existencia de centros, unicidad de ID
        2. Dominio: origen ≠ destino (RN-013 en Route.__init__)

        Args:
            route_id (str): Identificador único para la nueva ruta.
            origin_center_id (str): ID del centro logístico de origen.
            destination_center_id (str): ID del centro logístico de destino.

        Raises:
            ValueError: Si los datos son inválidos o los centros no existen.
        """

        # Validación de aplicación: route_id no vacío
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        # Validación de aplicación: unicidad de route_id
        # Consultar antes de crear para evitar duplicados
        route = self._route_repo.get_by_route_id(route_id)
        if route is not None:
            raise ValueError(f"Ya existe una ruta con el identificador '{route_id}'.")

        # Validación de aplicación: centros deben existir
        # El servicio valida esto porque requiere coordinación entre repositorios
        origin = self._center_repo.get_by_center_id(origin_center_id)
        if not origin:
            raise ValueError("El centro de origen no existe.")

        destination = self._center_repo.get_by_center_id(destination_center_id)
        if not destination:
            raise ValueError("El centro de destino no existe.")

        # Crear ruta: delegar al dominio (constructor valida RN-013)
        # Route.__init__ valida que origen ≠ destino
        route = Route(route_id, origin, destination)

        # Persistir: guardar en repositorio
        self._route_repo.add(route)


    def list_routes(self):
        """
        Obtiene un resumen de todas las rutas registradas.

        Caso de uso: UC-10 (Listar Rutas Disponibles)

        Transformación de datos: Convierte objetos de dominio a tuplas simples
        para presentación. Esto evita exponer objetos complejos a la capa UI.

        Returns:
            Lista de tuplas conteniendo (route_id, origin_id, destination_id, status).
        """
        routes = self._route_repo.list_all()

        result = []
        for route in routes:
            route_id = route.route_id
            origin_center = route.origin_center
            destination_center = route.destination_center

            # Crear tupla con datos mínimos necesarios
            result.append((route_id, origin_center.center_id, destination_center.center_id, "Activa" if route.is_active else "Finalizada"))
        return result


    def get_route(self, route_id):
        """
        Recupera una ruta específica del sistema por su identificador.

        Utilidad: Principalmente para uso interno del servicio
        También podría usarse para consultas detalladas desde presentación

        Args:
            route_id (str): El identificador único de la ruta a consultar.

        Returns:
            El objeto de la ruta encontrada.

        Raises:
            ValueError: Si el route_id está vacío o solo contiene espacios.
            ValueError: Si no se encuentra ninguna ruta con ese identificador en el repositorio.
        """
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")
        return route


    def assign_shipment_to_route(self, tracking_code, route_id):
        """
        Asigna un envío específico a una ruta de transporte.

         Caso de uso: UC-11 (Asignar Envío a Ruta)
        Reglas de negocio aplicadas:
        - RN-016: Un envío solo puede estar en una ruta a la vez
        - RN-015: Solo rutas activas aceptan envíos
        - Existencia de envío y ruta (validación de aplicación)

        Operación transaccional implícita:
        Actualiza dos entidades (Route y Shipment) que deben mantenerse consistentes.
        En un sistema con BD, esto requeriría transacción explícita.

        Args:
            tracking_code (str): Código de seguimiento del envío.
            route_id (str): ID de la ruta a la que se desea asignar.

        Raises:
            ValueError: Si la ruta no está activa o el envío ya tiene ruta.
        """
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")
        if not tracking_code.strip():
            raise ValueError("El código de seguimiento del envío no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        # Regla de negocio RN-015: solo rutas activas aceptan envíos
        if not route.is_active:
            raise ValueError(f"La ruta '{route_id}' no está activa.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        # Regla de negocio RN-016: verificar que el envío no esté ya asignado
        # Esta validación podría estar en el dominio, pero requiere acceso al repositorio
        # Por eficiencia, se hace aquí a nivel de aplicación
        if shipment.is_assigned_to_route():
            raise ValueError(f"El envío '{tracking_code}' ya está asignado a una ruta.")

        # Operación bidireccional: actualizar ambos lados de la relación
        route.add_shipment(shipment)

        # Esta línea es redundante pero se mantiene por claridad (route.add_shipment(shipment)
        # ya llama a shipment.assign_route() internamente)
        shipment.assign_route(route_id)

        # Persistir cambios en ambas entidades
        # Orden: primero route (contiene la lista), luego shipment
        # En transacción real, esto sería atómico (o se guarda todo, o no se guarda nada)
        self._route_repo.add(route)
        self._shipment_repo.add(shipment)


    def remove_shipment_from_route(self, tracking_code, route_id):
        """
        Elimina la vinculación entre un envío y su ruta asignada.

        Caso de uso: UC-13 (Retirar Envío de Ruta)

        Validación: El envío debe pertenecer a la ruta especificada
        Esto previene desvinculaciones incorrectas o maliciosas

        Args:
            tracking_code (str): Código de seguimiento del envío.
            route_id (str): ID de la ruta asignada.

        Raises:
            ValueError: Si los identificadores son vacíos o el envío no pertenece a la ruta.
        """

        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")
        if not tracking_code.strip():
            raise ValueError("El código de seguimiento del envío no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        # Validación crítica: el envío debe estar asignado a ESTA ruta
        # Previene retirar un envío de una ruta a la que no pertenece
        if shipment.assigned_route != route_id:
            raise ValueError(f"El envío '{tracking_code}' no está asignado a la ruta '{route_id}'.")

        # Operación bidireccional: actualizar ambos lados
        route.remove_shipment(shipment)  # ya llama a shipment.remove_route() internamente

        self._route_repo.add(route)
        self._shipment_repo.add(shipment)


    def dispatch_route(self, route_id):
        """
        Coordina el despacho de todos los envíos asociados a la ruta.

        Caso de uso: UC-14 (Despachar Ruta)
        Operación compleja: Involucra múltiples entidades y repositorios

        Flujo:
        1. Validar ruta activa y no despachada previamente
        2. Para cada envío en la ruta:
           a. Centro origen despacha envío (actualiza estado a IN_TRANSIT)
           b. Envío se remueve del inventario del centro origen

        Nota: No persiste cambios en centros porque Center.dispatch_shipment()
        ya actualiza el estado del envío, y ShipmentRepository persiste ese cambio.

        Args:
            route_id (str): ID de la ruta a despachar.

        Raises:
            ValueError: Si la ruta no existe, está inactiva o ya fue despachada.
        """
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        if not route.is_active:
            raise ValueError(f"La ruta '{route_id}' ya ha sido completada y no se puede despachar.")

        # Validar que no esté ya despachada (todos los envíos en IN_TRANSIT)
        # Esto es una optimización, no una regla de negocio estricta
        shipments = route.list_shipment()
        if shipments and all(s.current_status == "IN_TRANSIT" for s in shipments):
            raise ValueError(f"La ruta '{route_id}' ya ha sido despachada.")

        origin_center = route.origin_center

        # Despachar cada envío
        # Nota: No usamos for-each directo porque route.list_shipment() devuelve copia
        # Necesitamos los objetos reales para modificarlos
        for shipment in shipments:
            # Delegar al dominio: Centro maneja el despacho físico
            # Center.dispatch_shipment():
            # 1. Valida que el envío esté en el centro (RN-012)
            # 2. Actualiza estado del envío a IN_TRANSIT
            # 3. Remueve del inventario del centro
            origin_center.dispatch_shipment(shipment)


    def complete_route(self, route_id):
        """
        Finaliza una ruta activa, procesando la entrega de todos los paquetes.

        Caso de uso: UC-15 (Completar Ruta)
        Operación más compleja: Cierra el ciclo de vida completo

        Flujo:
        1. Validar ruta activa
        2. Route.complete_route() (en dominio) hace:
           a. Marca ruta como inactiva
           b. Para cada envío:
              - Lo registra en centro destino
              - Actualiza estado a DELIVERED
           c. Limpia lista de envíos

        Args:
            route_id (str): ID de la ruta a completar.

        Raises:
            ValueError: Si la ruta no existe o ya se encontraba finalizada.
        """
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        if not route.is_active:
            raise ValueError(f"La ruta '{route_id}' ya se encuentra finalizada.")

        # Delegar al dominio: Route maneja toda la lógica de completado
        # Route.complete_route() implementa:
        # 1. Validación de estado activo
        # 2. Transferencia de envíos a centro destino
        # 3. Actualización de estados a DELIVERED
        # 4. Cambio de estado de la ruta a inactiva
        route.complete_route()

        # Persistir cambios en la ruta
        # Los envíos ya fueron actualizados y persistidos por el centro destino
        self._route_repo.add(route)