# infrastructure/memory_route.py

from logisticaEnvios.domain.route_repository import RouteRepository

class RouteRepositoryMemory(RouteRepository):
    def __init__(self):
        self._by_route_id = {}

    def add(self, route):
        key = route.route_id.lower()
        self._by_route_id[key] = route

    def remove(self, route_id):
        route_id = (route_id or "").strip()
        if not route_id:
            return False

        key = route_id.lower()
        if key in self._by_route_id:
            del self._by_route_id[key]
            return True
        return False

    def get_by_route_id(self, route_id):
        route_id = (route_id or "").strip()
        if not route_id:
            return None
        return self._by_route_id.get(route_id.lower())

    def list_all(self):
        return list(self._by_route_id.values())