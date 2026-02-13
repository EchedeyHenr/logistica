# tests/test_shipment_types.py

import unittest
from logistica.domain.fragile_shipment import FragileShipment
from logistica.domain.express_shipment import ExpressShipment

class TestFragileShipment(unittest.TestCase):

    def test_create_valid_fragile(self):
        f = FragileShipment("FRG123", "A", "B", 2)
        self.assertEqual(f.priority, 2)
        self.assertEqual(f.shipment_type, "FRAGILE")
        self.assertTrue(f.is_fragile())

    def test_create_fragile_priority_below_2_raises(self):
        with self.assertRaises(ValueError):
            FragileShipment("FRG123", "A", "B", 1)

    def test_decrease_priority_from_2_raises(self):
        f = FragileShipment("FRG123", "A", "B", 2)
        with self.assertRaises(ValueError):
            f.decrease_priority()

    def test_decrease_priority_from_3_allowed(self):
        f = FragileShipment("FRG123", "A", "B", 3)
        f.decrease_priority()
        self.assertEqual(f.priority, 2)

    def test_increase_priority(self):
        f = FragileShipment("FRG123", "A", "B", 2)
        f.increase_priority()
        self.assertEqual(f.priority, 3)
        with self.assertRaises(ValueError):
            f.increase_priority()


class TestExpressShipment(unittest.TestCase):

    def test_create_express(self):
        e = ExpressShipment("EXP123", "A", "B")
        self.assertEqual(e.priority, 3)
        self.assertEqual(e.shipment_type, "EXPRESS")

    def test_priority_always_3(self):
        e = ExpressShipment("EXP123", "A", "B")
        self.assertEqual(e.priority, 3)
        # Intentar cambiar prioridad no debería funcionar (aunque no hay setter público)
        # Pero increase_priority debe lanzar error
        with self.assertRaises(ValueError):
            e.increase_priority()
        with self.assertRaises(ValueError):
            e.decrease_priority()

    def test_express_does_not_accept_priority_parameter(self):
        with self.assertRaises(TypeError):
            ExpressShipment("EXP002", "Samsung", "Lucía", priority=1)

if __name__ == '__main__':
    unittest.main()