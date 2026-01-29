# application/route_service.py

from logisticaEnvios.domain.route import Route

class RouteService:

    def __init__(self, route_repo, shipment_repo, center_repo):
        self._route_repo = route_repo
        self._shipment_repo = shipment_repo
        self._center_repo = center_repo


    def create_route(self, route_id, origin_center_id, destination_center_id):
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is not None:
            raise ValueError(f"Ya existe una ruta con el identificador '{route_id}'.")

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
            result.append((route_id, origin_center.center_id, destination_center.center_id, "Activa" if route.is_active else "Finalizada"))
        return result


    def get_route(self, route_id):
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")
        return route


    def assign_shipment_to_route(self, tracking_code, route_id):
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")
        if not tracking_code.strip():
            raise ValueError("El código de seguimiento del envío no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        if not route.is_active:
            raise ValueError(f"La ruta '{route_id}' no está activa.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        if shipment.is_assigned_to_route():
            raise ValueError(f"El envío '{tracking_code}' ya está asignado a una ruta.")

        route.add_shipment(shipment)
        shipment.assign_route(route_id)

        self._route_repo.add(route)
        self._shipment_repo.add(shipment)


    def remove_shipment_from_route(self, tracking_code, route_id):
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")
        if not tracking_code.strip():
            raise ValueError("El código de seguimiento del envío no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        shipment = self._shipment_repo.get_by_tracking_code(tracking_code)
        if shipment is None:
            raise ValueError(f"No hay ningún envío con el código de seguimiento '{tracking_code}'.")

        if shipment.assigned_route != route_id:
            raise ValueError(f"El envío '{tracking_code}' no está asignado a la ruta '{route_id}'.")

        route.remove_shipment(shipment)
        shipment.remove_route()

        self._route_repo.add(route)
        self._shipment_repo.add(shipment)


    def dispatch_route(self, route_id):
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        if not route.is_active:
            raise ValueError(f"La ruta '{route_id}' ya ha sido completada y no se puede despachar.")

        if all(s.current_status == "IN_TRANSIT" for s in route.list_shipment()):
            raise ValueError(f"La ruta '{route_id}' ya ha sido despachada.")

        origin_center = route.origin_center

        for shipment in route.list_shipment():
            origin_center.dispatch_shipment(shipment)


    def complete_route(self, route_id):
        if not route_id.strip():
            raise ValueError("El ID de la ruta no puede estar vacío.")

        route = self._route_repo.get_by_route_id(route_id)
        if route is None:
            raise ValueError(f"No existe una ruta con el identificador '{route_id}'.")

        if not route.is_active:
            raise ValueError(f"La ruta '{route_id}' ya se encuentra finalizada.")

        route.complete_route()
        self._route_repo.add(route)