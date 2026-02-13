import unittest
from logistica.application.shipment_service import ShipmentService
from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logistica.domain.shipment import Shipment
from logistica.domain.fragile_shipment import FragileShipment
from logistica.domain.express_shipment import ExpressShipment

class TestShipmentService(unittest.TestCase):

    def setUp(self):
        self.repo = ShipmentRepositoryMemory()
        self.service = ShipmentService(self.repo)

    # Test register_shipment
    def test_register_standard_shipment(self):
        self.service.register_shipment("ABC123", "Alice", "Bob", priority=2)
        shipment = self.repo.get_by_tracking_code("ABC123")
        self.assertIsInstance(shipment, Shipment)
        self.assertEqual(shipment.priority, 2)
        self.assertEqual(shipment.shipment_type, "STANDARD")

    def test_register_fragile_shipment_valid(self):
        self.service.register_shipment("FRG123", "Alice", "Bob", priority=2, shipment_type="fragile")
        shipment = self.repo.get_by_tracking_code("FRG123")
        self.assertIsInstance(shipment, FragileShipment)
        self.assertEqual(shipment.priority, 2)

    def test_register_fragile_shipment_invalid_priority_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.service.register_shipment("FRG123", "Alice", "Bob", priority=1, shipment_type="fragile")
        self.assertIn("prioridad inferior a 2", str(cm.exception))

    def test_register_express_shipment(self):
        self.service.register_shipment("EXP123", "Alice", "Bob", shipment_type="express")
        shipment = self.repo.get_by_tracking_code("EXP123")
        self.assertIsInstance(shipment, ExpressShipment)
        self.assertEqual(shipment.priority, 3)
        self.assertEqual(shipment.shipment_type, "EXPRESS")

    def test_register_express_shipment_priority_parameter_ignored(self):
        # El servicio no pasa el parámetro priority al constructor Express
        self.service.register_shipment("EXP123", "Alice", "Bob", priority=2, shipment_type="express")
        shipment = self.repo.get_by_tracking_code("EXP123")
        self.assertEqual(shipment.priority, 3)

    def test_register_duplicate_tracking_code_raises(self):
        self.service.register_shipment("ABC123", "Alice", "Bob")
        with self.assertRaises(ValueError) as cm:
            self.service.register_shipment("ABC123", "Charlie", "Diana")
        self.assertIn("Ya existe un envío", str(cm.exception))

    def test_register_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            self.service.register_shipment("ABC123", "A", "B", shipment_type="unknown")


    # Test update_shipment_status
    def test_update_status_valid(self):
        self.service.register_shipment("ABC123", "A", "B")
        self.service.update_shipment_status("ABC123", "IN_TRANSIT")
        shipment = self.repo.get_by_tracking_code("ABC123")
        self.assertEqual(shipment.current_status, "IN_TRANSIT")
        self.service.update_shipment_status("ABC123", "DELIVERED")
        self.assertEqual(shipment.current_status, "DELIVERED")
        self.assertEqual(shipment.get_status_history(), ["REGISTERED", "IN_TRANSIT", "DELIVERED"])

    def test_update_status_invalid_transition_raises(self):
        self.service.register_shipment("ABC123", "A", "B")
        with self.assertRaises(ValueError):
            self.service.update_shipment_status("ABC123", "DELIVERED")

    def test_update_status_shipment_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.service.update_shipment_status("NOEXIST", "IN_TRANSIT")


    # Test increase_priority
    def test_increase_priority_standard(self):
        self.service.register_shipment("ABC123", "A", "B", priority=1)
        self.service.increase_shipment_priority("ABC123")
        shipment = self.repo.get_by_tracking_code("ABC123")
        self.assertEqual(shipment.priority, 2)

    def test_increase_priority_from_max_raises(self):
        self.service.register_shipment("ABC123", "A", "B", priority=3)
        with self.assertRaises(ValueError):
            self.service.increase_shipment_priority("ABC123")

    def test_increase_priority_fragile(self):
        self.service.register_shipment("FRG123", "A", "B", priority=2, shipment_type="fragile")
        self.service.increase_shipment_priority("FRG123")
        shipment = self.repo.get_by_tracking_code("FRG123")
        self.assertEqual(shipment.priority, 3)

    def test_increase_priority_express_raises(self):
        self.service.register_shipment("EXP123", "A", "B", shipment_type="express")
        with self.assertRaises(ValueError):
            self.service.increase_shipment_priority("EXP123")

    def test_increase_priority_shipment_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.service.increase_shipment_priority("NOEXIST")


    # Test decrease_priority
    def test_decrease_priority_standard(self):
        self.service.register_shipment("ABC123", "A", "B", priority=3)
        self.service.decrease_shipment_priority("ABC123")
        shipment = self.repo.get_by_tracking_code("ABC123")
        self.assertEqual(shipment.priority, 2)

    def test_decrease_priority_from_min_raises(self):
        self.service.register_shipment("ABC123", "A", "B", priority=1)
        with self.assertRaises(ValueError):
            self.service.decrease_shipment_priority("ABC123")

    def test_decrease_priority_fragile_from_2_raises(self):
        self.service.register_shipment("FRG123", "A", "B", priority=2, shipment_type="fragile")
        with self.assertRaises(ValueError) as cm:
            self.service.decrease_shipment_priority("FRG123")
        self.assertIn("no puede ser inferior a 2", str(cm.exception))

    def test_decrease_priority_fragile_from_3_allowed(self):
        self.service.register_shipment("FRG123", "A", "B", priority=3, shipment_type="fragile")
        self.service.decrease_shipment_priority("FRG123")
        shipment = self.repo.get_by_tracking_code("FRG123")
        self.assertEqual(shipment.priority, 2)

    def test_decrease_priority_express_raises(self):
        self.service.register_shipment("EXP123", "A", "B", shipment_type="express")
        with self.assertRaises(ValueError):
            self.service.decrease_shipment_priority("EXP123")


    # Test list_shipments
    def test_list_shipments_order(self):
        self.service.register_shipment("XYZ789", "A", "B")
        self.service.register_shipment("ABC123", "C", "D")
        self.service.register_shipment("MNO456", "E", "F")
        lista = self.service.list_shipments()
        # Orden alfabético por código
        self.assertEqual([item[0] for item in lista], ["ABC123", "MNO456", "XYZ789"])

    def test_list_shipments_content(self):
        self.service.register_shipment("ABC123", "A", "B", priority=2)
        lista = self.service.list_shipments()
        self.assertEqual(len(lista), 1)
        codigo, estado, prioridad, tipo, ruta = lista[0]
        self.assertEqual(codigo, "ABC123")
        self.assertEqual(estado, "REGISTERED")
        self.assertEqual(prioridad, 2)
        self.assertEqual(tipo, "STANDARD")
        self.assertIsNone(ruta)


    # Test get_shipment
    def test_get_shipment_existing(self):
        self.service.register_shipment("ABC123", "A", "B")
        shipment = self.service.get_shipment("ABC123")
        self.assertEqual(shipment.tracking_code, "ABC123")

    def test_get_shipment_non_existing_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_shipment("NOEXIST")