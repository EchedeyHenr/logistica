import unittest
import os
import sqlite3
from logistica.infrastructure.sqlite_center import CenterRepositorySQLite
from logistica.infrastructure.sqlite_route import RouteRepositorySQLite
from logistica.infrastructure.sqlite_shipment import ShipmentRepositorySQLite
from logistica.domain.center import Center
from logistica.domain.route import Route
from logistica.domain.shipment import Shipment
from logistica.infrastructure.errores import EntityAlreadyExistsError, EntityNotFoundError

class TestSQLiteRepositories(unittest.TestCase):
    
    def setUp(self):
        self.db_path = "test_logistica.db"
        # Destruir db anterior si queda
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        # Crear esquema
        conn = sqlite3.connect(self.db_path)
        with conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("CREATE TABLE centers (center_id TEXT PRIMARY KEY, name TEXT NOT NULL, location TEXT NOT NULL)")
            cursor.execute("CREATE TABLE routes (route_id TEXT PRIMARY KEY, origin_center_id TEXT NOT NULL, destination_center_id TEXT NOT NULL, active INTEGER NOT NULL, FOREIGN KEY (origin_center_id) REFERENCES centers(center_id), FOREIGN KEY (destination_center_id) REFERENCES centers(center_id))")
            cursor.execute("CREATE TABLE shipments (tracking_code TEXT PRIMARY KEY, sender TEXT NOT NULL, recipient TEXT NOT NULL, priority INTEGER NOT NULL, current_status TEXT NOT NULL, shipment_type TEXT NOT NULL, assigned_route_id TEXT, current_center_id TEXT, FOREIGN KEY (assigned_route_id) REFERENCES routes(route_id), FOREIGN KEY (current_center_id) REFERENCES centers(center_id))")
            cursor.execute("CREATE TABLE shipment_status_history (id INTEGER PRIMARY KEY AUTOINCREMENT, tracking_code TEXT NOT NULL, status TEXT NOT NULL, FOREIGN KEY (tracking_code) REFERENCES shipments(tracking_code))")
        conn.close()
        
        self.center_repo = CenterRepositorySQLite(self.db_path)
        self.route_repo = RouteRepositorySQLite(self.db_path)
        self.shipment_repo = ShipmentRepositorySQLite(self.db_path)

    def tearDown(self):
        # Limpieza de db tras test
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_center_crud(self):
        # Create
        c = Center("MAD01", "Madrid", "Calle 1")
        self.center_repo.add(c)
        
        # Read
        c2 = self.center_repo.get_by_center_id("MAD01")
        self.assertEqual(c2.name, "Madrid")
        
        # Update
        c2._Center__name = "Madrid Editado"
        self.center_repo.update(c2)
        c3 = self.center_repo.get_by_center_id("MAD01")
        self.assertEqual(c3.name, "Madrid Editado")
        
        # Delete
        self.center_repo.remove("MAD01")
        with self.assertRaises(EntityNotFoundError):
            self.center_repo.get_by_center_id("MAD01")

    def test_center_duplicate_raises(self):
        c = Center("MAD01", "Madrid", "Calle 1")
        self.center_repo.add(c)
        with self.assertRaises(EntityAlreadyExistsError):
            self.center_repo.add(c)

    def test_shipment_crud(self):
        s = Shipment("ABC111", "Sender", "Recipient", 1)
        self.shipment_repo.add(s)
        
        s2 = self.shipment_repo.get_by_tracking_code("ABC111")
        self.assertEqual(s2.sender, "Sender")
        self.assertEqual(len(s2.get_status_history()), 1)
        
        s2.update_status("IN_TRANSIT")
        self.shipment_repo.update(s2)
        
        s3 = self.shipment_repo.get_by_tracking_code("ABC111")
        self.assertEqual(s3.current_status, "IN_TRANSIT")
        self.assertEqual(len(s3.get_status_history()), 2)
        
        self.shipment_repo.remove("ABC111")
        with self.assertRaises(EntityNotFoundError):
            self.shipment_repo.get_by_tracking_code("ABC111")

if __name__ == '__main__':
    unittest.main()
