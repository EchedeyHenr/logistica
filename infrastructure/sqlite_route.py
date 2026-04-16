# infrastructure/sqlite_route.py
import sqlite3
from logistica.domain.route_repository import RouteRepository
from logistica.domain.route import Route
from logistica.infrastructure.errores import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PersistenceError
)

class RouteRepositorySQLite(RouteRepository):
    def __init__(self, db_path="logistica.db"):
        self._db_path = db_path

    def add(self, route):
        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute(
                    "INSERT INTO routes (route_id, origin_center_id, destination_center_id, active) VALUES (?, ?, ?, ?)",
                    (route.route_id, route.origin_center.center_id, route.destination_center.center_id, 1 if route.is_active else 0)
                )
        except sqlite3.IntegrityError:
            raise EntityAlreadyExistsError(f"Ya existe una ruta con identificador '{route.route_id}'.")
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al guardar la ruta: {e}")
        finally:
            conn.close()

    def update(self, route):
        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute(
                    "UPDATE routes SET active = ? WHERE route_id = ?",
                    (1 if route.is_active else 0, route.route_id)
                )
                if cursor.rowcount == 0:
                    raise EntityNotFoundError(f"No existe una ruta con identificador '{route.route_id}'.")
                
                # Actualizar los envíos que están en esta ruta
                # Primero, los quitamos
                cursor.execute("UPDATE shipments SET assigned_route_id = NULL WHERE assigned_route_id = ?", (route.route_id,))
                
                # Despues los añadimos de nuevo a los presentes
                for tracking_code in route.list_shipments():
                    cursor.execute(
                        "UPDATE shipments SET assigned_route_id = ? WHERE tracking_code = ?", 
                        (route.route_id, tracking_code)
                    )
                    
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al actualizar la ruta: {e}")
        finally:
            conn.close()

    def remove(self, route_id):
        route_id = (route_id or "").strip()
        if not route_id:
            raise EntityNotFoundError("El ID de la ruta no puede estar vacío.")

        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute("DELETE FROM routes WHERE route_id = ?", (route_id,))
                if cursor.rowcount == 0:
                    raise EntityNotFoundError(f"No existe una ruta con el identificador '{route_id}'.")
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"No se puede eliminar la ruta '{route_id}' por relaciones activas en bbdd.")
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al eliminar la ruta: {e}")
        finally:
            conn.close()

    def get_by_route_id(self, route_id):
        route_id = (route_id or "").strip()
        if not route_id:
            raise EntityNotFoundError("El ID de la ruta no puede estar vacío.")

        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT route_id, origin_center_id, destination_center_id, active FROM routes WHERE route_id = ?", (route_id,))
            row = cursor.fetchone()
            if row is None:
                raise EntityNotFoundError(f"No existe una ruta con el identificador '{route_id}'.")
            
            rid, o_id, d_id, active = row
            
            # Reconstruir los centros inyectándolos
            from logistica.infrastructure.sqlite_center import CenterRepositorySQLite
            center_repo = CenterRepositorySQLite(self._db_path)
            
            origin = center_repo.get_by_center_id(o_id)
            dest = center_repo.get_by_center_id(d_id)
            
            route = Route(rid, origin, dest)
            route._active = bool(active)
            
            # Recuperar asignaciones de envios a esta ruta (tracking codes string list!)
            cursor.execute("SELECT tracking_code FROM shipments WHERE assigned_route_id = ?", (route_id,))
            for (t_code,) in cursor.fetchall():
                route._shipments.append(t_code)

            return route
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al recuperar la ruta: {e}")
        finally:
            conn.close()

    def list_all(self):
        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT route_id FROM routes")
            rows = cursor.fetchall()
            routes = []
            for (r_id,) in rows:
                routes.append(self.get_by_route_id(r_id))
            return routes
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al listar las rutas: {e}")
        finally:
            conn.close()
