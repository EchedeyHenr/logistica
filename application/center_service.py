# application/center_service.py

from logistica.domain.center import Center

class CenterService:
    """
    Servicio de aplicación para la gestión de centros logísticos.

    Responsabilidades:
    - Orquestar casos de uso relacionados con centros
    - Gestionar inventario de centros (envíos almacenados)
    - Coordinar operaciones de entrada/salida de mercancía
    - Actuar como mediador entre centros y otros servicios

    Características:
    - Menos complejo que RouteService (solo dos repositorios)
    - Enfocado en operaciones CRUD y consultas
    - Poco estado compartido entre métodos
    """

    def __init__(self, center_repo, shipment_repo):
        """
        Inicializa el servicio con los repositorios necesarios.

        Dependencias:
        - center_repo: CRUD de centros
        - shipment_repo: para consultar envíos (no modificarlos directamente)

        Nota: A diferencia de RouteService, este servicio no modifica envíos
        directamente. Las modificaciones se hacen a través de los centros.

        Args:
            center_repo: Repositorio de centros logísticos.
            shipment_repo: Repositorio de envíos (solo para consulta).
        """
        self._center_repo = center_repo
        self._shipment_repo = shipment_repo


    def register_center(self, center_id, name, location):
        """
        Registra un nuevo centro logístico en el sistema.

        Caso de uso: UC-06 (Registrar Nuevo Centro)
        Reglas de negocio aplicadas:
        - RN-009: center_id debe ser único (validación de aplicación)
        - RN-010: Todos los campos obligatorios (validación en dominio)

        Args:
            center_id (str): ID único del centro.
            name (str): Nombre descriptivo del centro.
            location (str): Ubicación geográfica o dirección del centro.

        Raises:
            ValueError: Si algún dato es inválido o el centro ya está registrado.
        """

        # Validaciones de aplicación: campos no vacíos
        # Esto es redundante con validaciones del dominio pero proporciona
        # mensajes de error más específicos y evita crear objetos inválidos
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")
        if not name.strip():
            raise ValueError("El nombre del centro no puede estar vacío.")
        if not location.strip():
            raise ValueError("La ubicación del centro no puede estar vacía.")

        # Regla de negocio RN-009: verificar unicidad de center_id
        # Consultar repositorio antes de crear
        center = self._center_repo.get_by_center_id(center_id)
        if center is not None:
            raise ValueError(f"Ya hay registrado un centro con el identificador '{center_id}'.")

        # Crear centro: delegar al dominio (valida RN-010 internamente)
        # Center.__init__ valida que los parámetros sean strings no vacíos
        center = Center(center_id, name, location)

        self._center_repo.add(center)

    def list_centers(self):
        """
        Obtiene una lista con la información básica de todos los centros.

        Caso de uso: UC-07 (Listar Centros Existentes)

        Returns:
            Lista de tuplas conteniendo (center_id, name, location).
        """
        centers = self._center_repo.list_all()

        result = []
        for center in centers:
            center_id = center.center_id
            name = center.name
            location = center.location
            result.append((center_id, name, location))
        return result

    def get_center(self, center_id):
        """
        Recupera un centro específico mediante su identificador único.

        Utilidad: Para consultas detalladas o uso interno de otros servicios

        Args:
            center_id (str): El identificador del centro a consultar.

        Returns:
            Center: El objeto del centro logístico encontrado.

        Raises:
            ValueError: Si el ID está vacío o el centro no existe en el repositorio.
        """
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")

        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError(f"No existe un centro con el identificador '{center_id}'.")
        return center

    def receive_shipment(self, tracking_code, center_id):
        """
        Procesa la recepción física de un envío en un centro determinado.

        Caso de uso: Parte de UC-11 y UC-15 (cuando se asignan/completan rutas)

        Reglas de negocio delegadas:
        - RN-011: No duplicar envíos en el mismo centro (en dominio)
        - Solo centros existentes pueden recibir envíos (validación de aplicación)

        Nota: Este método normalmente sería llamado por RouteService, no desde UI

        Args:
            tracking_code (str): Código de seguimiento del envío recibido.
            center_id (str): ID del centro que recibe el paquete.

        Raises:
            ValueError: Si los identificadores son inválidos o no se encuentran los registros.
        """
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

        # Delegar al dominio: Centro maneja la recepción
        # Center.receive_shipment() valida:
        # 1. Que el parámetro sea un Shipment
        # 2. RN-011: que el envío no esté ya en el centro
        center.receive_shipment(shipment)

        # Persistir cambios en el centro
        # El envío no se modifica, solo se agrega a la lista del centro
        self._center_repo.add(center)

    def dispatch_shipment(self, tracking_code, center_id):
        """
        Gestiona la salida de un envío desde un centro logístico.

        Caso de uso: Parte de UC-14 (cuando se despachan rutas)

        Reglas de negocio delegadas:
        - RN-012: Solo se pueden despachar envíos que están en el centro (en dominio)

        Nota: Este método normalmente sería llamado por RouteService.dispatch_route()

        Args:
            tracking_code (str): Código de seguimiento del envío a despachar.
            center_id (str): ID del centro desde donde sale el paquete.

        Raises:
            ValueError: Si el centro o el envío no existen o no se pueden procesar.
        """
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

        # Delegar al dominio: Centro maneja el despacho
        # Center.dispatch_shipment() valida:
        # 1. Que el parámetro sea un Shipment
        # 2. RN-012: que el envío esté en el centro
        # 3. Actualiza estado del envío a IN_TRANSIT
        center.dispatch_shipment(shipment)

        # Persistir cambios en el centro
        # El envío ya fue actualizado (estado) y persistido por el centro
        self._center_repo.add(center)

    def list_shipments_in_center(self, center_id):
        """
        Lista todos los envíos que se encuentran actualmente en un centro específico.

        Caso de uso: UC-08 (Consultar Inventario de Centro)

        Args:
            center_id (str): ID del centro a consultar.

        Returns:
            List[Shipment]: Colección de objetos de envío presentes en el centro.

        Raises:
            ValueError: Si el ID está vacío o el centro no existe.
        """
        if not center_id.strip():
            raise ValueError("El ID del centro no puede estar vacío.")

        center = self._center_repo.get_by_center_id(center_id)
        if center is None:
            raise ValueError(f"No existe un centro con el identificador '{center_id}'.")

        # Delegar al centro: devuelve su lista interna de envíos
        # Center.list_shipments() devuelve copia para encapsulamiento
        return center.list_shipments()