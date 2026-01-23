# infrastructure/memory_center.py

from logisticaEnvios.domain.center_repository import CenterRepository

class CenterRepositoryMemory(CenterRepository):
    def __init__(self):
        self._by_center_id = {}

    def add(self, center):
        key = center.center_id.lower()
        self._by_center_id[key] = center

    def remove(self, center_id):
        center_id = (center_id or "").strip()
        if not center_id:
            return False

        key = center_id.lower()
        if key in self._by_center_id:
            del self._by_center_id[key]
            return True
        return False

    def get_by_center_id(self, center_id):
        center_id = (center_id or "").strip()
        if not center_id:
            return None
        return self._by_center_id.get(center_id.lower())

    def list_all(self):
        return list(self._by_center_id.values())