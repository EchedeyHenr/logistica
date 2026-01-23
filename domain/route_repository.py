# domain/route_repository.py

class RouteRepository:
    def add(self, route):
        raise NotImplementedError

    def remove(self, route_id):
        raise NotImplementedError

    def get_by_route_id(self, route_id):
        raise NotImplementedError

    def list_all(self):
        raise NotImplementedError