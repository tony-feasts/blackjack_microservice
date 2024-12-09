# framework/resources/base_resource.py

from abc import ABC, abstractmethod

class BaseResource(ABC):
    @abstractmethod
    def get_by_key(self, key):
        pass

    @abstractmethod
    def create(self, data):
        pass

    @abstractmethod
    def update(self, key, data):
        pass

    @abstractmethod
    def delete(self, key):
        pass
