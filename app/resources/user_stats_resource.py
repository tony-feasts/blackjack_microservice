# app/resources/user_stats_resource.py

from framework.resources.base_resource import BaseResource
from app.services.service_factory import ServiceFactory
from app.models import UserStats

class UserStatsResource(BaseResource):
    def __init__(self):
        self.data_service = ServiceFactory.get_service('DataService')
        self.database = self.data_service.config.get_config('DB_NAME')
        self.collection = 'user_stats'
        self.key_field = 'username'

    def get_by_key(self, key):
        data = self.data_service.get_data_object(
            self.database, self.collection, self.key_field, key
        )
        if data:
            return UserStats(**data)
        else:
            return None

    def create(self, data: UserStats):
        data_dict = data.model_dump(exclude={"links"})
        self.data_service.create_data_object(
            self.database, self.collection, data_dict
        )

    def update(self, key, data: UserStats):
        data_dict = data.model_dump(exclude={"links", "username"})
        result = self.data_service.update_data_object(
            self.database, self.collection, self.key_field, key, data_dict
        )
        return result

    def delete(self, key):
        result = self.data_service.delete_data_object(
            self.database, self.collection, self.key_field, key
        )
        return result

    def change_username(self, old_username: str, new_username: str) -> None:
        existing_user_stats = self.get_by_key(old_username)
        new_user_stats = UserStats(username=new_username,
                                   wins=existing_user_stats.wins,
                                   losses=existing_user_stats.losses)
        self.create(new_user_stats)
        self.data_service.update_by_field('game_history', 'username',
                                          old_username, new_username)
        self.delete(old_username)
