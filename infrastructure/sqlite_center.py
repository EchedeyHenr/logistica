# infrastructure/sqlite_center.py
import sqlite3
from logistica.domain.center_repository import CenterRepository
from logistica.domain.center import Center
from logistica.infrastructure.errores import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PersistenceError
)

class CenterRepositorySQLite(CenterRepository):
    def __init__(self, db_path="logistica.db"):
        self._db_path = db_path

    def add(self, center):
        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute(
                    "INSERT INTO centers (center_id, name, location) VALUES (?, ?, ?)",
                    (center.center_id, center.name, center.location)
                )
        except sqlite3.IntegrityError:
            raise EntityAlreadyExistsError(f"Ya existe un centro con identificador '{center.center_id}'.")
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al guardar el centro: {e}")
        finally:
            conn.close()

    def update(self, center):
        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute(
                    "UPDATE centers SET name = ?, location = ? WHERE center_id = ?",
                    (center.name, center.location, center.center_id)
                )
                if cursor.rowcount == 0:
                    raise EntityNotFoundError(f"No existe un centro con identificador '{center.center_id}'.")
                
                # Reconciliar inventario (shipments presentes físicamente en el centro)
                # Primero, quitar de todos los que lo tenian
                cursor.execute("UPDATE shipments SET current_center_id = NULL WHERE current_center_id = ?", (center.center_id,))
                
                # Segundo, asignar a los actuales
                for shipment in center.list_shipments():
                    cursor.execute(
                        "UPDATE shipments SET current_center_id = ? WHERE tracking_code = ?", 
                        (center.center_id, shipment.tracking_code)
                    )
                    
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al actualizar el centro: {e}")
        finally:
            conn.close()

    def remove(self, center_id):
        center_id = (center_id or "").strip()
        if not center_id:
            raise EntityNotFoundError("El ID del centro no puede estar vacío.")

        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                # Fallará por foreing_keys si existen dependencias en routes
                cursor.execute("DELETE FROM centers WHERE center_id = ?", (center_id,))
                if cursor.rowcount == 0:
                    raise EntityNotFoundError(f"No existe un centro con el identificador '{center_id}'.")
        except sqlite3.IntegrityError as e:
            raise PersistenceError(f"No se puede eliminar el centro '{center_id}' porque está referenciado por operaciones activas.")
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al eliminar el centro: {e}")
        finally:
            conn.close()

    def get_by_center_id(self, center_id):
        center_id = (center_id or "").strip()
        if not center_id:
            raise EntityNotFoundError("El ID del centro no puede estar vacío.")

        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT center_id, name, location FROM centers WHERE center_id = ?", (center_id,))
            row = cursor.fetchone()
            if row is None:
                raise EntityNotFoundError(f"No existe un centro con el identificador '{center_id}'.")
            
            center = Center(row[0], row[1], row[2])
            
            # Recuperar inventario de shipments
            cursor.execute("SELECT tracking_code FROM shipments WHERE current_center_id = ?", (center_id,))
            tracking_rows = cursor.fetchall()
            
            # Para evitar dependencias circulares costosas al nivel de la conexion, 
            # delegamos la resolucion total al shipment repo en este scope.
            from logistica.infrastructure.sqlite_shipment import ShipmentRepositorySQLite
            shipment_repo = ShipmentRepositorySQLite(self._db_path)
            
            for (t_code,) in tracking_rows:
                # Obtenemos sus entidades
                shipment = shipment_repo.get_by_tracking_code(t_code)
                # Reconstruimos bypass de negocio manual, pues receive_shipment valora _shipments logic:
                center._shipments.append(shipment)

            return center
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al recuperar el centro: {e}")
        finally:
            conn.close()

    def list_all(self):
        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT center_id FROM centers")
            rows = cursor.fetchall()
            centers = []
            for row in rows:
                centers.append(self.get_by_center_id(row[0]))
            return centers
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al listar los centros: {e}")
        finally:
            conn.close()
