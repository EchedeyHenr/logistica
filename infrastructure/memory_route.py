# infrastructure/memory_route.py
"""
Repositorio en memoria para la gestión persistente de rutas de transporte.

Implementa la interfaz RouteRepository utilizando un diccionario en memoria como almacenamiento temporal, ideal para entornos de prueba o desarrollo.

Esta implementación es case-insensitive para las consultas por ID de ruta, normalizando todos los identificadores a minúsculas.

Attributes:
    _by_route_id (dict): Diccionario que mapea IDs de rutas (en minúsculas) a objetos Route.
"""

from logistica.domain.route_repository import RouteRepository
from logistica.infrastructure.errores import EntityAlreadyExistsError, EntityNotFoundError

class RouteRepositoryMemory(RouteRepository):
    """
    Implementación en memoria del repositorio de rutas.

    Proporciona operaciones CRUD básicas para la entidad Route utilizando
    una estructura de diccionario en memoria. No persiste los datos entre
    ejecuciones del programa.

    Características:
            - Búsquedas insensibles a mayúsculas/minúsculas
            - Almacenamiento temporal en memoria RAM
            - Implementación ligera y rápida para desarrollo
    """
    def __init__(self):
        """
        Inicializa un nuevo repositorio en memoria vacío.
        """
        self._by_route_id = {}

    def add(self, route):
        """
        Almacena una nueva ruta en el repositorio.

        Si ya existe una ruta con el mismo ID (ignorando mayúsculas/minúsculas), la sobrescribe sin generar advertencia.

        Args:
            route (Route): Instancia de la ruta a almacenar.

        Raises:
            TypeError: Si el parámetro `route` no es una instancia de Route.
        """
        key = route.route_id.lower()
        if key in self._by_route_id:
            raise EntityAlreadyExistsError(f"Ya existe una ruta con identificador '{route.route_id}'")
        self._by_route_id[key] = route

    def update(self, route):
        """
        En memoria el objeto ya está mutado por referencia; no hace nada.
        """
        pass

    def remove(self, route_id):
        """
        Elimina una ruta del repositorio mediante su identificador.

        Args:
            route_id (str): ID de la ruta a eliminar.

        Returns:
            True si la ruta existía y fue eliminada, False en caso contrario.
        """
        route_id = (route_id or "").strip()
        if not route_id:
            raise EntityNotFoundError("El ID de la ruta no puede estar vacío.")

        key = route_id.lower()
        if key in self._by_route_id:
            del self._by_route_id[key]
        else:
            raise EntityNotFoundError(f"No existe una ruta con el identificador '{route_id}'.")

    def get_by_route_id(self, route_id):
        """
        Recupera una ruta por su identificador único.

        Args:
            route_id (str): ID de la ruta a buscar.

        Returns:
            La instancia de Route si se encuentra, None si no existe o el ID está vacío.
        """
        route_id = (route_id or "").strip()
        if not route_id:
            raise EntityNotFoundError("El ID de la ruta no puede estar vacío.")
        route = self._by_route_id.get(route_id.lower())
        if route is None:
            raise EntityNotFoundError(f"No existe una ruta con el identificador '{route_id}'.")
        return route

    def list_all(self):
        """
        Obtiene todas las rutas almacenadas en el repositorio.

        Returns:
            Lista con todas las instancias de Route almacenadas, en el orden de inserción (dependiente del dict).
        """
        return list(self._by_route_id.values())