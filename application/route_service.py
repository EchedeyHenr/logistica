# application/route_service.py

from logisticaEnvios.domain.route import Route

class RouteService:

    def __init__(self, route_repo, shipment_repo, center_repo):
        self._route_repo = route_repo
        self._shipment_repo = shipment_repo
        self._center_repo = center_repo


    def create_route(self, route_id, origin_center_id, destination_center_id):
        route = self._route_repo.get_by_route_id(route_id)
        if route is not None:
            raise ValueError("Ya existe una ruta con ese identificador.")

        origin = self._center_repo.get_by_center_id(origin_center_id)
        if not origin:
            raise ValueError("El centro de origen no existe.")

        destination = self._center_repo.get_by_center_id(destination_center_id)
        if not destination:
            raise ValueError("El centro de destino no existe.")

        route = Route(route_id, origin, destination)
        self._route_repo.add(route)


    def list_routes(self):
        routes = self._route_repo.list_all()

        result = []
        for route in routes:
            route_id = route.route_id
            origin_center = route.origin_center
            destination_center = route.destination_center
            result.append((route_id, origin_center, destination_center))
        return result


    def get_route(self, route_id):
        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError("No existe una ruta con ese identificador.")
        return route


    def assign_shipment_to_route(self, tracking_code, route_id):
        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError("No existe una ruta con ese identificador.")

        if not route.is_active:
            raise ValueError("La ruta no está activa.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código.")

        if shipment.is_assigned_to_route():
            raise ValueError("El envío ya está asignado a una ruta.")

        route.add_shipment(shipment)
        shipment.assign_route(route_id)

        self._route_repo.add(route)
        self._shipment_repo.add(shipment)


    def remove_shipment_from_route(self, tracking_code, route_id):
        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError("No existe una ruta con ese identificador.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError("No hay ningún envío con ese código.")

        if shipment.assigned_route != route_id:
            raise ValueError("El envío no está asignado a esta ruta.")

        route.remove_shipment(shipment)
        shipment.remove_route()

        self._route_repo.add(route)
        self._shipment_repo.add(shipment)


    def dispatch_route(self, route_id):
        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError("No existe una ruta con ese identificador.")

        origin_center = route.origin_center

        for shipment in route.list_shipment():
            origin_center.dispatch_shipment(shipment)


    def complete_route(self, route_id):
        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError("No existe una ruta con ese identificador.")

        route.complete_route()
        self._route_repo.add(route)