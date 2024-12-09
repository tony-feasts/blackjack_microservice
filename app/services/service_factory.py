# app/services/service_factory.py

from framework.services import BaseServiceFactory, Config
from framework.services.data_access.mysql_rdb_data_service \
    import MySQLRDBDataService

# We may want to handle resources here too
class ServiceFactory(BaseServiceFactory):
    _services = {}

    @classmethod
    def get_service(cls, service_name: str):
        if service_name not in cls._services:
            if service_name == 'DataService':
                config = Config()
                cls._services[service_name] = MySQLRDBDataService(config)
            else:
                raise ValueError(f"Service '{service_name}' not recognized.")
        return cls._services[service_name]
