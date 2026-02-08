# application/services.py

from logistica.domain.shipment import Shipment
from logistica.domain.fragile_shipment import FragileShipment
from logistica.domain.express_shipment import ExpressShipment
from logistica.domain.shipment_repository import ShipmentRepository

class ShipmentService:
    """
    Servicio de aplicación para la gestión de envíos.

    RESPONSABILIDADES:
    - Orquestar casos de uso relacionados con envíos
    - Validar reglas de negocio a nivel de aplicación
    - Coordinar múltiples entidades del dominio para operaciones complejas
    - Actuar como punto único de entrada para operaciones de envío
    """

    def __init__(self, repo):
        """
        Inicializa el servicio con el repositorio de envíos.

        Patrón: Dependency Injection
        - el servicio no crea su propio repositorio, recibe una implementación concreta.
        - Esto permite:
        1. Testeo fácil (inyectar mock para tests unitarios)
        2. Cambiar implementación de persistencia sin modificar el servicio
        3. Cumplir con Dependency Inversion Principle (SOLID)

        Args:
            repo (ShipmentRepository): Instancia del repositorio de envíos que implementa ShipmentRepository.
        """
        # Almacenar referencia al repositorio para todas las operaciones
        # Nota: No se valida tipo en tiempo de ejecución por simplicidad,
        # pero en producción se podría usar isinstance(repo, ShipmentRepository)
        self._repo = repo


    def register_shipment(self, tracking_code, sender, recipient, priority=1, shipment_type="standard"):
        """
        Crea un nuevo envío en el sistema según su tipo y lo persiste.

        Caso de uso: UC-01 (Registrar Nuevo Envío)
        Reglas de negocio aplicadas:
        - RN-001: Código de seguimiento único en el sistema
        - Validación de tipo de envío (standard, fragile, express)
        - Prioridad adecuada según tipo (ej: frágil mínimo 2 por RN-004)

        Este método ilustra el patrón Factory Method a nivel de servicio:
        crea la instancia adecuada según el tipo especificado.

        Flujo:
        1. Validar unicidad del código (RN-001)
        2. Crear instancia del tipo adecuado
        3. Persistir en repositorio

        Args:
            tracking_code (str): Código único de seguimiento.
            sender (str): Información del remitente.
            recipient (str): Información del destinatario.
            priority (int, opcional): Nivel de prioridad (por defecto 1).
            shipment_type (str, opcional): Tipo de envío (por defecto "standard").

        Raises:
            ValueError: Si el código ya existe o el tipo de envío no es válido.
        """

        # Regla de negocio RN-001: unicidad del código de seguimiento
        # Consulta al repositorio antes de crear para evitar duplicados
        # Esto es validación a nivel de aplicación, no del dominio
        if self._repo.get_by_tracking_code(tracking_code) is not None:
            raise ValueError(f"Ya existe un envío con el código de seguimiento '{tracking_code}'.")

        # Normalizar tipo de envío para comparación case-insensitive
        shipment_type = shipment_type.lower()

        # Factory pattern: crea la instancia adecuada según el tipo
        # Cada constructor valida sus propias reglas de negocio
        if shipment_type == "standard":
            shipment = Shipment(tracking_code, sender, recipient, priority)
        elif shipment_type == "fragile":
            # FragileShipment valida internamente que priority ≥ 2 (RN-004)
            shipment = FragileShipment(tracking_code, sender, recipient, priority)
        elif shipment_type == "express":
            # ExpressShipment ignora el parámetro priority, siempre usa 3
            # Esto implementa RN-005 (prioridad fija para express)
            shipment = ExpressShipment(tracking_code, sender, recipient)
        else:
            raise ValueError("Tipo de envío no válido.")

        # Persistir el envío creado en el repositorio
        # El repositorio es responsable del almacenamiento, no el servicio
        self._repo.add(shipment)


    def update_shipment_status(self, tracking_code, new_status):
        """
        Actualiza el estado logístico de un envío específico.

        Caso de uso: UC-04 (Actualizar Estado de Envío)

        Regla de negocio delegadas:
        - RN-007: Validación de transiciones de estado (en dominio)
        - Existencia del envío (validación de aplicación)

        Flujo:
        1. Verificar existencia del envío
        2. Delegar actualización al dominio (Shipment.update_status)
        3. Persistir cambios en repositorio

        Args:
            tracking_code (str): Código de seguimiento del envío.
            new_status (str): Nuevo estado a asignar.

        Raises:
            ValueError: Si no se encuentra un envío con ese código.
        """

        # Validación de aplicación: el envío debe existir
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        # Delegar al dominio: El servicio no valida la transición
        # Shipment.update_status() valida RN-007 internamente
        # Esto mantiene las reglas de negocio en el dominio donde pertenecen
        shipment.update_status(new_status)

        # Persistir cambios (el envío ya fue modificado)
        self._repo.add(shipment)


    def increase_shipment_priority(self, tracking_code):
        """
        Incrementa el nivel de prioridad de un envío existente.

        Caso de uso: UC-05 parte 1 (Aumentar Prioridad)
        Reglas de negocio delegadas:
        - Validaciones específicas por tipo de envío (en dominio)
        - Límite máximo de prioridad 3 (en dominio)

        Nota: Para ExpressShipment, este método fallará (prioridad fija 3)

        Args:
            tracking_code (str): Código de seguimiento del envío.

        Raises:
            ValueError: Si el envío no existe en el sistema.
        """

        # Validación de aplicación: existencia del envío
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        # Delegar al dominio: Polimorfismo en acción
        # Cada tipo de envío (Shipment, FragileShipment, ExpressShipment)
        # implementa su propia lógica para increase_priority()
        # ExpressShipment lanzará ValueError (RN-005)
        shipment.increase_priority()

        self._repo.add(shipment)


    def decrease_shipment_priority(self, tracking_code):
        """
        Reduce el nivel de prioridad de un envío existente.

        Caso de uso: UC-05 parte 2 (Disminuir Prioridad)
        Reglas de negocio delegadas:
        - Validaciones específicas por tipo de envío (en dominio)
        - FragileShipment: no puede bajar de 2 (RN-006)
        - Límite mínimo de prioridad 1 (para estándar)

        Args:
            tracking_code (str): Código de seguimiento del envío.

        Raises:
            ValueError: Si el envío no existe en el sistema.
        """

        # Validación de aplicación: existencia del envío
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        # DELEGAR AL DOMINIO: Polimorfismo
        # FragileShipment.decrease_priority() valida RN-006
        shipment.decrease_priority()

        self._repo.add(shipment)


    def list_shipments(self):
        """
        Obtiene una lista ordenada de todos los envíos con su información básica.

        Caso de uso: UC-03 (Listar Todos los Envíos)
        Regla de aplicación: RN-022 (Ordenación alfabética case-insensitive)

        Returns:
            List[Tuple]: Lista de tuplas conteniendo (código, estado, prioridad, tipo, ruta),
            ordenada alfabéticamente por código de seguimiento.
        """

        # Obtener todos los envíos del repositorio
        shipments = self._repo.list_all()

        result = []
        for shipment in shipments:
            # Extraer información básica para presentación
            # Nota: No exponemos objetos de dominio directamente a la presentación
            # Esto sigue el principio de mínima exposición
            tracking_code = shipment.tracking_code
            current_status = shipment.current_status
            priority = shipment.priority
            shipment_type = shipment.shipment_type
            assigned_route = shipment.assigned_route
            result.append((tracking_code, current_status, priority, shipment_type, assigned_route))

        # Regla de aplicación RN-022: Ordenar alfabéticamente case-insensitive
        # Esto es una preferencia de UI, no una regla de negocio del dominio
        result.sort(key=lambda item: item[0].lower())
        return result

    def get_shipment(self, tracking_code):
        """
        Recupera un envío específico del repositorio para su consulta o manipulación.

        Caso de uso: UC-02 (Consultar Envío Específico)

        Patrón:
        - Este método es para consulta (query)
        - Otros métodos son para comandos (register, update, etc.)

        Nota: Devuelve el objeto de dominio completo. En una arquitectura más avanzada,
        se devolvería un DTO (Data Transfer Object) específico para consultas.

        Args:
            tracking_code (str): El código de seguimiento a buscar.

        Returns:
            Shipment: El objeto de dominio del envío encontrado.

        Raises:
            ValueError: Si el envío solicitado no existe.
        """

        # Consultar repositorio
        shipment = self._repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No existe el envío con código de seguimiento '{tracking_code}'.")
        return shipment
