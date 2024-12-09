# framework/services/base_service_factory.py

from abc import ABC, abstractmethod

class BaseServiceFactory(ABC):
    @abstractmethod
    def get_service(self, service_name: str):
        pass
