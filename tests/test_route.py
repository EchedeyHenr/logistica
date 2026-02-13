# tests/test_route.py

import unittest
from logistica.domain.center import Center
from logistica.domain.shipment import Shipment
from logistica.domain.route import Route

class TestRoute(unittest.TestCase):

    def setUp(self):
        self.origin = Center("MAD01", "Madrid", "Calle A")
        self.dest = Center("BCN02", "Barcelona", "Calle B")
        self.route = Route("MAD01-BCN02-STD-001", self.origin, self.dest)
        self.shipment = Shipment("ABC123", "A", "B", 1)

    def test_create_route(self):
        self.assertEqual(self.route.route_id, "MAD01-BCN02-STD-001")
        self.assertIs(self.route.origin_center, self.origin)
        self.assertIs(self.route.destination_center, self.dest)
        self.assertTrue(self.route.is_active)
        self.assertEqual(self.route.list_shipment(), [])

    def test_create_route_invalid_id_pattern(self):
        with self.assertRaises(ValueError):
            Route("BAD-ID", self.origin, self.dest)

    def test_create_route_same_origin_dest_raises(self):
        with self.assertRaises(ValueError):
            Route("MAD01-MAD01-STD-001", self.origin, self.origin)

    def test_create_route_with_none_center_raises(self):
        with self.assertRaises(ValueError):
            Route("MAD01-BCN02-STD-001", None, self.dest)

    def test_add_shipment(self):
        self.route.add_shipment(self.shipment)
        self.assertIn(self.shipment, self.route.list_shipment())
        self.assertEqual(self.shipment.assigned_route, self.route.route_id)
        # Verificar que el envío se ha registrado en el centro de origen
        self.assertTrue(self.origin.has_shipment("ABC123"))

    def test_add_shipment_to_inactive_route_raises(self):
        # Preparamos la ruta para que quede inactiva
        self.route.add_shipment(self.shipment)
        self.origin.dispatch_shipment(self.shipment)  # despachamos la ruta
        self.route.complete_route()  # ahora la ruta queda inactiva

        # Intentar añadir un nuevo envío a la ruta inactiva debe fallar
        new_shipment = Shipment("XYZ789", "C", "D", 2)
        with self.assertRaises(ValueError):
            self.route.add_shipment(new_shipment)

    def test_remove_shipment(self):
        self.route.add_shipment(self.shipment)
        self.route.remove_shipment(self.shipment)
        self.assertNotIn(self.shipment, self.route.list_shipment())
        self.assertIsNone(self.shipment.assigned_route)
        # El envío sigue en el centro de origen (no se elimina de allí)
        self.assertTrue(self.origin.has_shipment("ABC123"))

    def test_complete_route(self):
        self.route.add_shipment(self.shipment)
        self.origin.dispatch_shipment(self.shipment)
        self.route.complete_route()

        self.assertFalse(self.route.is_active)
        self.assertEqual(self.route.list_shipment(), [])
        # El envío debe estar en el centro destino y con estado DELIVERED
        self.assertTrue(self.dest.has_shipment("ABC123"))
        self.assertEqual(self.shipment.current_status, "DELIVERED")
        # Ya no está en el origen
        self.assertFalse(self.origin.has_shipment("ABC123"))

    def test_complete_route_already_inactive_raises(self):
        self.route.add_shipment(self.shipment)
        self.origin.dispatch_shipment(self.shipment)  # se despacha la ruta
        self.route.complete_route()  # primera vez, correcto

        with self.assertRaises(ValueError):
            self.route.complete_route()  # segunda vez debe fallar

    def test_list_shipment_returns_copy(self):
        self.route.add_shipment(self.shipment)
        lista = self.route.list_shipment()
        lista.append(self.shipment)  # modificar copia (aunque sea el mismo objeto)
        self.assertEqual(len(self.route.list_shipment()), 1)

if __name__ == '__main__':
    unittest.main()