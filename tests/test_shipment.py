# tests/test_shipment.py

import unittest
from logistica.domain.shipment import Shipment

class TestShipment(unittest.TestCase):

    def test_create_valid_shipment(self):
        s = Shipment("XYZ789", "Alice", "Bob", 3)
        self.assertEqual(s.tracking_code, "XYZ789")
        self.assertEqual(s.sender, "Alice")
        self.assertEqual(s.recipient, "Bob")
        self.assertEqual(s.priority, 3)
        self.assertEqual(s.current_status, "REGISTERED")
        self.assertEqual(s.shipment_type, "STANDARD")
        self.assertIsNone(s.assigned_route)
        self.assertEqual(s.get_status_history(), ["REGISTERED"])

    def test_create_invalid_tracking_code(self):
        with self.assertRaises(ValueError):
            Shipment("", "A", "B", 1)

        with self.assertRaises(ValueError):
            Shipment("ABC12", "A", "B", 1)  # debe tener 3 letras + 3 dígitos

    def test_create_invalid_sender_empty(self):
        with self.assertRaises(ValueError):
            Shipment("ABC123", "", "B", 1)

    def test_create_invalid_recipient_empty(self):
        with self.assertRaises(ValueError):
            Shipment("ABC123", "A", "", 1)

    def test_create_invalid_priority(self):
        with self.assertRaises(ValueError):
            Shipment("ABC123", "A", "B", 0)

    def test_update_status_valid_transitions(self):
        s = Shipment("ABC123", "A", "B", 1)
        s.update_status("IN_TRANSIT")
        self.assertEqual(s.current_status, "IN_TRANSIT")
        s.update_status("DELIVERED")
        self.assertEqual(s.current_status, "DELIVERED")
        self.assertEqual(s.get_status_history(), ["REGISTERED", "IN_TRANSIT", "DELIVERED"])

    def test_update_status_invalid_transition(self):
        s = Shipment("ABC123", "A", "B", 1)
        with self.assertRaises(ValueError):
            s.update_status("DELIVERED")  # salta IN_TRANSIT

    def test_can_change_to_valid(self):
        s = Shipment("ABC123", "A", "B", 1)
        # No debe lanzar excepción
        s.can_change_to("IN_TRANSIT")
        s.update_status("IN_TRANSIT")
        s.can_change_to("DELIVERED")

    def test_can_change_to_invalid(self):
        s = Shipment("ABC123", "A", "B", 1)
        with self.assertRaises(ValueError):
            s.can_change_to("DELIVERED")

    def test_increase_priority(self):
        s = Shipment("ABC123", "A", "B", 1)
        s.increase_priority()
        self.assertEqual(s.priority, 2)
        s.increase_priority()
        self.assertEqual(s.priority, 3)
        with self.assertRaises(ValueError):
            s.increase_priority()

    def test_decrease_priority(self):
        s = Shipment("ABC123", "A", "B", 3)
        s.decrease_priority()
        self.assertEqual(s.priority, 2)
        s.decrease_priority()
        self.assertEqual(s.priority, 1)
        with self.assertRaises(ValueError):
            s.decrease_priority()

    def test_assign_route(self):
        s = Shipment("ABC123", "A", "B", 1)
        s.assign_route("RUTA-001")
        self.assertEqual(s.assigned_route, "RUTA-001")
        self.assertTrue(s.is_assigned_to_route())

    def test_assign_route_none_raises(self):
        s = Shipment("ABC123", "A", "B", 1)
        with self.assertRaises(ValueError):
            s.assign_route(None)

    def test_remove_route(self):
        s = Shipment("ABC123", "A", "B", 1)
        s.assign_route("RUTA-001")
        s.remove_route()
        self.assertIsNone(s.assigned_route)
        self.assertFalse(s.is_assigned_to_route())

    def test_remove_route_without_assignment_raises(self):
        s = Shipment("ABC123", "A", "B", 1)
        with self.assertRaises(ValueError):
            s.remove_route()

    def test_is_delivered(self):
        s = Shipment("ABC123", "A", "B", 1)
        self.assertFalse(s.is_delivered())
        s.update_status("IN_TRANSIT")
        self.assertFalse(s.is_delivered())
        s.update_status("DELIVERED")
        self.assertTrue(s.is_delivered())

if __name__ == '__main__':
    unittest.main()