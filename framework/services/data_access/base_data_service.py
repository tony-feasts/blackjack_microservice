# framework/services/base_data_service.py

from abc import ABC, abstractmethod
from typing import Any


class BaseDataService(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_data_object(self, database_name: str, collection_name: str,
                        key_field: str, key_value: Any):
        pass

    @abstractmethod
    def create_data_object(self, database_name: str, collection_name: str,
                           data: dict):
        pass

    @abstractmethod
    def update_data_object(self, database_name: str, collection_name: str,
                           key_field: str, key_value: Any, data: dict):
        pass

    @abstractmethod
    def delete_data_object(self, database_name: str, collection_name: str,
                           key_field: str, key_value: Any):
        pass
