# tests/test_center.py

import unittest
from logistica.domain.center import Center
from logistica.domain.shipment import Shipment
from logistica.domain.fragile_shipment import FragileShipment

class TestCenter(unittest.TestCase):

    def setUp(self):
        self.center = Center("MAD01", "Madrid Central", "Calle Mayor 1")
        self.shipment1 = Shipment("ABC123", "A", "B", 1)
        self.shipment2 = FragileShipment("FRG123", "C", "D", 2)

    def test_create_center(self):
        self.assertEqual(self.center.center_id, "MAD01")
        self.assertEqual(self.center.name, "Madrid Central")
        self.assertEqual(self.center.location, "Calle Mayor 1")
        self.assertEqual(self.center.list_shipments(), [])

    def test_create_center_invalid_id_pattern(self):
        with self.assertRaises(ValueError):
            Center("MAD1", "C", "L")  # debe ser 3-4 letras + 2 dígitos

    def test_create_center_empty_id_raises(self):
        with self.assertRaises(ValueError):
            Center("", "Nombre", "Ubicación")

    def test_create_center_empty_name(self):
        with self.assertRaises(ValueError):
            Center("MAD01", "", "L")

    def test_receive_shipment(self):
        self.center.receive_shipment(self.shipment1)
        self.assertIn(self.shipment1, self.center.list_shipments())
        self.assertTrue(self.center.has_shipment("ABC123"))

    def test_receive_duplicate_shipment_raises(self):
        self.center.receive_shipment(self.shipment1)
        with self.assertRaises(ValueError):
            self.center.receive_shipment(self.shipment1)

    def test_receive_non_shipment_raises(self):
        with self.assertRaises(ValueError):
            self.center.receive_shipment("not a shipment")

    def test_dispatch_shipment(self):
        self.center.receive_shipment(self.shipment1)
        dispatched = self.center.dispatch_shipment(self.shipment1)
        self.assertIs(dispatched, self.shipment1)
        self.assertEqual(self.shipment1.current_status, "IN_TRANSIT")
        self.assertNotIn(self.shipment1, self.center.list_shipments())

    def test_dispatch_shipment_not_in_center_raises(self):
        with self.assertRaises(ValueError):
            self.center.dispatch_shipment(self.shipment1)

    def test_has_shipment(self):
        self.center.receive_shipment(self.shipment1)
        self.assertTrue(self.center.has_shipment("ABC123"))
        self.assertFalse(self.center.has_shipment("NONEXISTENT"))

    def test_list_shipments_returns_copy(self):
        self.center.receive_shipment(self.shipment1)
        lista = self.center.list_shipments()
        lista.append(self.shipment2)  # modificar copia
        self.assertEqual(len(self.center.list_shipments()), 1)  # original no se afecta

if __name__ == '__main__':
    unittest.main()