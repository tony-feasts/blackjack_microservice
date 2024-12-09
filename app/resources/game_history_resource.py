# app/resources/game_history_resource.py

from framework.resources.base_resource import BaseResource
from app.services.service_factory import ServiceFactory
from app.models import GameHistory

class GameHistoryResource(BaseResource):
    def __init__(self):
        self.data_service = ServiceFactory.get_service('DataService')
        self.database = self.data_service.config.get_config('DB_NAME')
        self.collection = 'game_history'
        self.key_field = 'game_id'

    def get_by_key(self, key):
        data = self.data_service.get_data_object(
            self.database, self.collection, self.key_field, key
        )
        if data:
            return GameHistory(**data)
        else:
            return None

    def create(self, data: GameHistory):
        data_dict = data.model_dump(exclude={"links", "game_id"})
        new_id = self.data_service.create_data_object(
            self.database, self.collection, data_dict
        )
        return new_id

    def update(self, key, data: GameHistory):
        data_dict = data.model_dump(exclude={"links", "game_id"})
        result = self.data_service.update_data_object(
            self.database, self.collection, self.key_field, key, data_dict
        )
        return result

    def delete(self, key):
        result = self.data_service.delete_data_object(
            self.database, self.collection, self.key_field, key
        )
        return result

    def get_by_username(self, username, skip, limit):
        results = self.data_service.get_data_objects_by_field(self.collection,
                                                              "username",
                                                              username, skip,
                                                              limit)
        return [GameHistory(**data) for data in results]
