# domain/center_repository.py

class CenterRepository:
    def add(self, center):
        raise NotImplementedError

    def remove(self, center_id):
        raise NotImplementedError

    def get_by_center_id(self, center_id):
        raise NotImplementedError

    def list_all(self):
        raise NotImplementedError
