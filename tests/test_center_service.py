import unittest
from logistica.application.center_service import CenterService
from logistica.infrastructure.memory_center import CenterRepositoryMemory
from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logistica.domain.shipment import Shipment

class TestCenterService(unittest.TestCase):

    def setUp(self):
        self.center_repo = CenterRepositoryMemory()
        self.shipment_repo = ShipmentRepositoryMemory()
        self.service = CenterService(self.center_repo, self.shipment_repo)


    # Test register_center
    def test_register_center_valid(self):
        self.service.register_center("MAD01", "Madrid Central", "Calle Mayor 1")
        center = self.center_repo.get_by_center_id("MAD01")
        self.assertIsNotNone(center)
        self.assertEqual(center.name, "Madrid Central")
        self.assertEqual(center.location, "Calle Mayor 1")

    def test_register_center_duplicate_id_raises(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        with self.assertRaises(ValueError) as cm:
            self.service.register_center("MAD01", "Barcelona", "Calle B")
        self.assertIn("Ya hay registrado un centro", str(cm.exception))

    def test_register_center_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.register_center("   ", "Nombre", "Ubicación")

    def test_register_center_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.service.register_center("MAD01", "", "Ubicación")

    def test_register_center_empty_location_raises(self):
        with self.assertRaises(ValueError):
            self.service.register_center("MAD01", "Nombre", "")


    # Test list_centers
    def test_list_centers(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        self.service.register_center("BCN02", "Barcelona", "Calle B")
        centers = self.service.list_centers()
        self.assertEqual(len(centers), 2)
        self.assertIn(("MAD01", "Madrid", "Calle A"), centers)
        self.assertIn(("BCN02", "Barcelona", "Calle B"), centers)


    # Test get_center
    def test_get_center_existing(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        center = self.service.get_center("MAD01")
        self.assertEqual(center.center_id, "MAD01")

    def test_get_center_non_existing_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.service.get_center("NOEXIST")
        self.assertIn("No existe un centro", str(cm.exception))

    def test_get_center_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_center("   ")


    # Test receive_shipment
    def test_receive_shipment_valid(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        shipment = Shipment("ABC123", "Alice", "Bob")
        self.shipment_repo.add(shipment)

        self.service.receive_shipment("ABC123", "MAD01")
        center = self.center_repo.get_by_center_id("MAD01")
        self.assertTrue(center.has_shipment("ABC123"))

    def test_receive_shipment_center_not_found_raises(self):
        shipment = Shipment("ABC123", "Alice", "Bob")
        self.shipment_repo.add(shipment)
        with self.assertRaises(ValueError) as cm:
            self.service.receive_shipment("ABC123", "NOEXIST")
        self.assertIn("No existe un centro", str(cm.exception))

    def test_receive_shipment_shipment_not_found_raises(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        with self.assertRaises(ValueError) as cm:
            self.service.receive_shipment("NOEXIST", "MAD01")
        self.assertIn("No hay ningún envío", str(cm.exception))

    def test_receive_shipment_empty_tracking_code_raises(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        with self.assertRaises(ValueError):
            self.service.receive_shipment("   ", "MAD01")

    def test_receive_shipment_empty_center_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.receive_shipment("ABC123", "   ")


    # Test dispatch_shipment
    def test_dispatch_shipment_valid(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        shipment = Shipment("ABC123", "Alice", "Bob")
        self.shipment_repo.add(shipment)
        # Primero recibimos
        self.service.receive_shipment("ABC123", "MAD01")

        self.service.dispatch_shipment("ABC123", "MAD01")
        center = self.center_repo.get_by_center_id("MAD01")
        self.assertFalse(center.has_shipment("ABC123"))
        # El estado del envío debe ser IN_TRANSIT
        self.assertEqual(shipment.current_status, "IN_TRANSIT")

    def test_dispatch_shipment_not_in_center_raises(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        shipment = Shipment("ABC123", "Alice", "Bob")
        self.shipment_repo.add(shipment)
        # No se recibe
        with self.assertRaises(ValueError) as cm:
            self.service.dispatch_shipment("ABC123", "MAD01")
        self.assertIn("no se encuentra en el centro", str(cm.exception))

    def test_dispatch_shipment_center_not_found_raises(self):
        shipment = Shipment("ABC123", "Alice", "Bob")
        self.shipment_repo.add(shipment)
        with self.assertRaises(ValueError):
            self.service.dispatch_shipment("ABC123", "NOEXIST")

    def test_dispatch_shipment_shipment_not_found_raises(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        with self.assertRaises(ValueError):
            self.service.dispatch_shipment("NOEXIST", "MAD01")


    # Test list_shipments_in_center
    def test_list_shipments_in_center(self):
        self.service.register_center("MAD01", "Madrid", "Calle A")
        s1 = Shipment("ABC123", "A", "B")
        s2 = Shipment("XYZ789", "C", "D")
        self.shipment_repo.add(s1)
        self.shipment_repo.add(s2)
        self.service.receive_shipment("ABC123", "MAD01")
        self.service.receive_shipment("XYZ789", "MAD01")

        shipments = self.service.list_shipments_in_center("MAD01")
        self.assertEqual(len(shipments), 2)
        codes = [s.tracking_code for s in shipments]
        self.assertIn("ABC123", codes)
        self.assertIn("XYZ789", codes)

    def test_list_shipments_in_center_center_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.service.list_shipments_in_center("NOEXIST")

    def test_list_shipments_in_center_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.list_shipments_in_center("   ")