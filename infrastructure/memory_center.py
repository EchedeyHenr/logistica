# infrastructure/memory_center.py
"""
Repositorio en memoria para la gestión persistente de centros logísticos.

Implementa la interfaz CenterRepository utilizando un diccionario en memoria
como almacenamiento temporal, adecuado para entornos de desarrollo, pruebas
o demostraciones donde no se requiere persistencia permanente.

Esta implementación normaliza todos los identificadores de centro a minúsculas
para proporcionar búsquedas case-insensitive, garantizando consistencia en
las operaciones de consulta y eliminación.

Attributes:
    _by_center_id (dict): Diccionario que mapea IDs de centros (en minúsculas)
    a objetos Center.
"""

from logistica.domain.center_repository import CenterRepository

class CenterRepositoryMemory(CenterRepository):
    """
    Implementación en memoria del repositorio de centros logísticos.

    Proporciona operaciones CRUD para la entidad Center utilizando
    una estructura de diccionario Python. Los datos se pierden al finalizar
    la ejecución del programa, por lo que no es adecuado para producción
    sin mecanismos de persistencia adicionales.

    Características:
        - Búsquedas insensibles a mayúsculas/minúsculas
        - Almacenamiento temporal en memoria RAM
        - Implementación ligera y rápida para desarrollo

    Notes:
        El método `remove()` no valida si el centro contiene envíos activos, y no se usa por el momento.
    """
    def __init__(self):
        """
        Inicializa un nuevo repositorio en memoria para centros logísticos.

        Crea un diccionario vacío que almacenará los centros indexados por
        sus identificadores normalizados a minúsculas.
        """
        self._by_center_id = {}

    def add(self, center):
        """
        Almacena o actualiza un centro logístico en el repositorio.

        Si ya existe un centro con el mismo ID (ignorando mayúsculas/minúsculas),
        será sobrescrito sin generar advertencia. Esta operación es O(1).

        Args:
            center (Center): Instancia del centro a almacenar.

        Raises:
        TypeError: Si el parámetro `center` no es una instancia válida de Center.
        """
        key = center.center_id.lower()
        self._by_center_id[key] = center

    def remove(self, center_id):
        """
        Elimina un centro logístico del repositorio por su ID.

        Args:
            center_id (str): Identificador del centro a eliminar.

        Returns:
            True si el centro existía y fue eliminado exitosamente, False si el ID está vacío o el centro no existe.

        Notes:
            Esta operación no verifica si el centro contiene envíos activos.
            La integridad referencial debe gestionarse a nivel de aplicación.
        """
        center_id = (center_id or "").strip()
        if not center_id:
            return False

        key = center_id.lower()
        if key in self._by_center_id:
            del self._by_center_id[key]
            return True
        return False

    def get_by_center_id(self, center_id):
        """
        Recupera un centro logístico por su identificador único.

        Args:
            center_id (str): ID del centro a buscar.

        Returns:
            La instancia del centro si se encuentra, None si no existe o el ID está vacío.
        """
        center_id = (center_id or "").strip()
        if not center_id:
            return None
        return self._by_center_id.get(center_id.lower())

    def list_all(self):
        """
        Obtiene todos los centros logísticos almacenados en el repositorio.

        Returns:
            Lista con todas las instancias de centros almacenadas.

        Notes:
            La lista devuelta es una copia superficial. Modificar los objetos
            en la lista afectará a los objetos almacenados en el repositorio.
        """
        return list(self._by_center_id.values())