import unittest
from logistica.application.route_service import RouteService
from logistica.application.center_service import CenterService
from logistica.application.shipment_service import ShipmentService
from logistica.infrastructure.memory_route import RouteRepositoryMemory
from logistica.infrastructure.memory_center import CenterRepositoryMemory
from logistica.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logistica.domain.shipment import Shipment

class TestRouteService(unittest.TestCase):

    def setUp(self):
        self.route_repo = RouteRepositoryMemory()
        self.center_repo = CenterRepositoryMemory()
        self.shipment_repo = ShipmentRepositoryMemory()
        self.center_service = CenterService(self.center_repo, self.shipment_repo)
        self.shipment_service = ShipmentService(self.shipment_repo)
        self.service = RouteService(self.route_repo, self.shipment_repo, self.center_repo)

        # Crear centros de prueba con IDs válidos
        self.center_service.register_center("MAD01", "Madrid", "Calle A")
        self.center_service.register_center("BCN02", "Barcelona", "Calle B")

    # Test create_route
    def test_create_route_valid(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        route = self.route_repo.get_by_route_id(route_id)
        self.assertIsNotNone(route)
        self.assertEqual(route.origin_center.center_id, "MAD01")
        self.assertEqual(route.destination_center.center_id, "BCN02")
        self.assertTrue(route.is_active)

    def test_create_route_duplicate_id_raises(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        with self.assertRaises(ValueError) as cm:
            self.service.create_route(route_id, "MAD01", "BCN02")
        self.assertIn("Ya existe una ruta", str(cm.exception))

    def test_create_route_origin_not_found_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.service.create_route("MAD01-BCN02-STD-001", "NOEXIST", "BCN02")
        self.assertEqual(str(cm.exception), "El centro de origen no existe.")

    def test_create_route_destination_not_found_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.service.create_route("MAD01-BCN02-STD-001", "MAD01", "NOEXIST")
        self.assertEqual(str(cm.exception), "El centro de destino no existe.")

    def test_create_route_same_origin_dest_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.service.create_route("MAD01-MAD01-STD-001", "MAD01", "MAD01")
        self.assertIn("no pueden ser el mismo", str(cm.exception))

    def test_create_route_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.create_route("   ", "MAD01", "BCN02")


    # Test list_routes
    def test_list_routes(self):
        self.service.create_route("MAD01-BCN02-STD-001", "MAD01", "BCN02")
        self.service.create_route("BCN02-MAD01-STD-002", "BCN02", "MAD01")
        routes = self.service.list_routes()
        self.assertEqual(len(routes), 2)
        ids = [r[0] for r in routes]
        self.assertIn("MAD01-BCN02-STD-001", ids)
        self.assertIn("BCN02-MAD01-STD-002", ids)
        # Verificar que el estado se muestra como "Activa"
        self.assertEqual(routes[0][3], "Activa")


    # Test get_route
    def test_get_route_existing(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        route = self.service.get_route(route_id)
        self.assertEqual(route.route_id, route_id)

    def test_get_route_non_existing_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_route("MAD01-BCN02-STD-999")  # no existe

    def test_get_route_empty_id_raises(self):
        with self.assertRaises(ValueError):
            self.service.get_route("   ")


    # Test assign_shipment_to_route
    def test_assign_shipment_valid(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)

        route = self.service.get_route(route_id)
        self.assertEqual(len(route.list_shipment()), 1)
        self.assertEqual(route.list_shipment()[0].tracking_code, "ABC123")

        shipment = self.shipment_service.get_shipment("ABC123")
        self.assertEqual(shipment.assigned_route, route_id)

        # Verificar que está en el centro de origen
        center = self.center_service.get_center("MAD01")
        self.assertTrue(center.has_shipment("ABC123"))

    def test_assign_shipment_route_not_found_raises(self):
        self.shipment_service.register_shipment("ABC123", "A", "B")
        with self.assertRaises(ValueError):
            self.service.assign_shipment_to_route("ABC123", "MAD01-BCN02-STD-999")

    def test_assign_shipment_shipment_not_found_raises(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        with self.assertRaises(ValueError):
            self.service.assign_shipment_to_route("NOEXIST", route_id)

    def test_assign_shipment_route_inactive_raises(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        # Despachamos y completamos para inactivar
        self.service.assign_shipment_to_route("ABC123", route_id)
        self.service.dispatch_route(route_id)
        self.service.complete_route(route_id)

        new_shipment = Shipment("XYZ789", "C", "D")
        self.shipment_repo.add(new_shipment)
        with self.assertRaises(ValueError) as cm:
            self.service.assign_shipment_to_route("XYZ789", route_id)
        self.assertIn("no está activa", str(cm.exception))

    def test_assign_shipment_already_assigned_raises(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)
        with self.assertRaises(ValueError) as cm:
            self.service.assign_shipment_to_route("ABC123", route_id)
        self.assertIn("ya está asignado", str(cm.exception))

    # Test remove_shipment_from_route
    def test_remove_shipment_valid(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)
        self.service.remove_shipment_from_route("ABC123", route_id)

        route = self.service.get_route(route_id)
        self.assertEqual(len(route.list_shipment()), 0)
        shipment = self.shipment_service.get_shipment("ABC123")
        self.assertIsNone(shipment.assigned_route)
        # El envío sigue en el centro de origen
        center = self.center_service.get_center("MAD01")
        self.assertTrue(center.has_shipment("ABC123"))

    def test_remove_shipment_not_in_route_raises(self):
        route_id1 = "MAD01-BCN02-STD-001"
        route_id2 = "BCN02-MAD01-STD-002"
        self.service.create_route(route_id1, "MAD01", "BCN02")
        self.service.create_route(route_id2, "BCN02", "MAD01")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id1)
        with self.assertRaises(ValueError) as cm:
            self.service.remove_shipment_from_route("ABC123", route_id2)
        self.assertIn("no está asignado", str(cm.exception))

    def test_remove_shipment_route_not_found_raises(self):
        self.shipment_service.register_shipment("ABC123", "A", "B")
        with self.assertRaises(ValueError):
            self.service.remove_shipment_from_route("ABC123", "MAD01-BCN02-STD-999")

    # Test dispatch_route
    def test_dispatch_route_valid(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)

        self.service.dispatch_route(route_id)
        shipment = self.shipment_service.get_shipment("ABC123")
        self.assertEqual(shipment.current_status, "IN_TRANSIT")
        # El envío ya no está en el centro de origen
        center = self.center_service.get_center("MAD01")
        self.assertFalse(center.has_shipment("ABC123"))

    def test_dispatch_route_already_dispatched_raises(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)
        self.service.dispatch_route(route_id)
        with self.assertRaises(ValueError) as cm:
            self.service.dispatch_route(route_id)
        self.assertIn("ya ha sido despachada", str(cm.exception))

    def test_dispatch_route_inactive_raises(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)
        self.service.dispatch_route(route_id)
        self.service.complete_route(route_id)  # ahora inactiva
        with self.assertRaises(ValueError) as cm:
            self.service.dispatch_route(route_id)
        self.assertIn("ya ha sido completada", str(cm.exception))

    def test_dispatch_route_no_shipments(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        # No hay envíos, despachar no debería hacer nada (ni lanzar error)
        self.service.dispatch_route(route_id)
        route = self.service.get_route(route_id)
        self.assertTrue(route.is_active)  # sigue activa porque no se completa

    def test_dispatch_route_route_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.service.dispatch_route("MAD01-BCN02-STD-999")

    # Test complete_route
    def test_complete_route_valid(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)
        self.service.dispatch_route(route_id)
        self.service.complete_route(route_id)

        route = self.service.get_route(route_id)
        self.assertFalse(route.is_active)
        shipment = self.shipment_service.get_shipment("ABC123")
        self.assertEqual(shipment.current_status, "DELIVERED")
        # Debe estar en centro destino
        dest_center = self.center_service.get_center("BCN02")
        self.assertTrue(dest_center.has_shipment("ABC123"))

    def test_complete_route_already_inactive_raises(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        self.shipment_service.register_shipment("ABC123", "A", "B")
        self.service.assign_shipment_to_route("ABC123", route_id)
        self.service.dispatch_route(route_id)
        self.service.complete_route(route_id)
        with self.assertRaises(ValueError) as cm:
            self.service.complete_route(route_id)
        self.assertIn("ya se encuentra finalizada", str(cm.exception))

    def test_complete_route_no_shipments(self):
        route_id = "MAD01-BCN02-STD-001"
        self.service.create_route(route_id, "MAD01", "BCN02")
        # Completar una ruta sin envíos debería funcionar (solo desactivarla)
        self.service.complete_route(route_id)
        route = self.service.get_route(route_id)
        self.assertFalse(route.is_active)

    def test_complete_route_route_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.service.complete_route("MAD01-BCN02-STD-999")