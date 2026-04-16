# infrastructure/sqlite_shipment.py
import sqlite3
from logistica.domain.shipment_repository import ShipmentRepository
from logistica.domain.shipment import Shipment
from logistica.domain.fragile_shipment import FragileShipment
from logistica.domain.express_shipment import ExpressShipment
from logistica.infrastructure.errores import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PersistenceError
)

class ShipmentRepositorySQLite(ShipmentRepository):
    def __init__(self, db_path="logistica.db"):
        self._db_path = db_path

    def add(self, shipment):
        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                
                # Check assigned route and center
                # Since the Shipment object only holds the string ID for route (_assigned_route) and doesn't hold center natively,
                # we determine its physical location. Wait, domain Shipment doesn't have current_center_id natively!
                # Wait, the DB has current_center_id to map Center._shipments. 
                # If we save a shipment from ShipmentRepository, it doesn't know its center!
                # In Logistica, the center's inventory is saved via CenterRepository.update(center).
                # So ShipmentRepository.add() inserts the basic shipment info with NULL for current_center_id initially.
                # Route assignment: _assigned_route is present in Shipment!
                
                cursor.execute("""
                    INSERT INTO shipments (tracking_code, sender, recipient, priority, current_status, shipment_type, assigned_route_id, current_center_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                """, (
                    shipment.tracking_code,
                    shipment.sender,
                    shipment.recipient,
                    shipment.priority,
                    shipment.current_status,
                    shipment.shipment_type.upper(),
                    shipment.assigned_route
                ))
                
                # History (only first item since it's just created)
                cursor.execute("INSERT INTO shipment_status_history (tracking_code, status) VALUES (?, ?)", (shipment.tracking_code, "REGISTERED"))
                
        except sqlite3.IntegrityError as e:
            raise EntityAlreadyExistsError(f"Ya existe un envío con el código '{shipment.tracking_code}'.")
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al guardar el envío: {e}")
        finally:
            conn.close()

    def update(self, shipment):
        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                
                cursor.execute("""
                    UPDATE shipments 
                    SET sender = ?, recipient = ?, priority = ?, current_status = ?, assigned_route_id = ?
                    WHERE tracking_code = ?
                """, (
                    shipment.sender,
                    shipment.recipient,
                    shipment.priority,
                    shipment.current_status,
                    shipment.assigned_route,
                    shipment.tracking_code
                ))

                if cursor.rowcount == 0:
                    raise EntityNotFoundError(f"No existe el envío '{shipment.tracking_code}'.")

                # The shipment history might have new states.
                # To sync, we can just delete and recreate history, or insert missing.
                # Let's delete and recreate to be safe and simple.
                cursor.execute("DELETE FROM shipment_status_history WHERE tracking_code = ?", (shipment.tracking_code,))
                for s in shipment.get_status_history():
                    cursor.execute("INSERT INTO shipment_status_history (tracking_code, status) VALUES (?, ?)", (shipment.tracking_code, s))
                    
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al actualizar el envío: {e}")
        finally:
            conn.close()

    def remove(self, tracking_code):
        tracking_code = (tracking_code or "").strip()
        if not tracking_code:
            raise EntityNotFoundError("El código de seguimiento no puede estar vacío.")

        conn = sqlite3.connect(self._db_path)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute("DELETE FROM shipment_status_history WHERE tracking_code = ?", (tracking_code,))
                cursor.execute("DELETE FROM shipments WHERE tracking_code = ?", (tracking_code,))
                if cursor.rowcount == 0:
                    raise EntityNotFoundError(f"No existe un envío con el código '{tracking_code}'.")
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al eliminar el envío: {e}")
        finally:
            conn.close()

    def get_by_tracking_code(self, tracking_code):
        tracking_code = (tracking_code or "").strip()
        if not tracking_code:
            raise EntityNotFoundError("El código de seguimiento no puede estar vacío.")

        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT tracking_code, sender, recipient, priority, current_status, shipment_type, assigned_route_id FROM shipments WHERE tracking_code = ?", (tracking_code,))
            row = cursor.fetchone()
            
            if row is None:
                raise EntityNotFoundError(f"No existe un envío con el código '{tracking_code}'.")
            
            tc, sender, recipient, priority, status, stype, route_id = row
            
            cursor.execute("SELECT status FROM shipment_status_history WHERE tracking_code = ? ORDER BY id ASC", (tracking_code,))
            history = [r[0] for r in cursor.fetchall()]

            # Determine type and create object
            if stype == "FRAGILE":
                shipment = FragileShipment(tc, sender, recipient, priority)
            elif stype == "EXPRESS":
                shipment = ExpressShipment(tc, sender, recipient)
                # express ignores priority setting manually if not needed, or force it
            else:
                shipment = Shipment(tc, sender, recipient, priority)
            
            # Since the domain initiates history with REGISTERED, and status with REGISTERED, we override it internally:
            shipment._current_status = status
            shipment._status_history = history
            shipment._assigned_route = route_id
            
            return shipment
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al recuperar el envío: {e}")
        finally:
            conn.close()

    def list_all(self):
        conn = sqlite3.connect(self._db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT tracking_code FROM shipments")
            rows = cursor.fetchall()
            shipments = []
            for (tc,) in rows:
                shipments.append(self.get_by_tracking_code(tc))
            return shipments
        except sqlite3.OperationalError as e:
            raise PersistenceError(f"Error al listar envíos: {e}")
        finally:
            conn.close()
