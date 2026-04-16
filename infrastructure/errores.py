# infrastructure/errores.py
"""Excepciones de dominio para el manejo de la capa de persistencia."""

class RepositoryError(Exception):
    """Excepción base para todos los errores de persistencia."""
    pass

class EntityAlreadyExistsError(RepositoryError):
    """Se lanza cuando se intenta guardar una entidad con un ID que ya existe."""
    pass

class EntityNotFoundError(RepositoryError):
    """Se lanza cuando se busca una entidad que no existe en el origen de datos."""
    pass

class PersistenceError(RepositoryError):
    """Se lanza ante cualquier error inesperado de infraestructura/BBDD."""
    pass
