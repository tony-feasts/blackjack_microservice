# app/services/data_access/mysql_rdb_data_service.py

import mysql.connector
from framework.services.data_access.base_data_service import BaseDataService
from framework.services.config import Config
from typing import Any


class MySQLRDBDataService(BaseDataService):
    def __init__(self, config: Config):
        super().__init__(config)
        self.connection = self._get_connection()

    def _get_connection(self):
        db_host = self.config.get_config("DB_HOST")
        db_user = self.config.get_config("DB_USER")
        db_password = self.config.get_config("DB_PASSWORD")
        db_name = self.config.get_config("DB_NAME")

        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return connection

    def get_data_object(self, database_name: str, collection_name: str,
                        key_field: str, key_value: Any):
        cursor = self.connection.cursor(dictionary=True)
        query = f"SELECT * FROM {collection_name} WHERE {key_field} = %s"
        cursor.execute(query, (key_value,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def create_data_object(self, database_name: str, collection_name: str,
                           data: dict):
        cursor = self.connection.cursor()
        keys = ', '.join(data.keys())
        values_placeholder = ', '.join(['%s'] * len(data))
        query =(f"INSERT INTO {collection_name} ({keys}) VALUES "
                f"({values_placeholder})")
        cursor.execute(query, tuple(data.values()))
        self.connection.commit()
        cursor.close()
        return cursor.lastrowid

    def update_data_object(self, database_name: str, collection_name: str,
                           key_field: str, key_value: Any, data: dict):
        cursor = self.connection.cursor()
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = (f"UPDATE {collection_name} SET {set_clause} "
                 f"WHERE {key_field} = %s")
        params = tuple(data.values()) + (key_value,)
        cursor.execute(query, params)
        self.connection.commit()
        cursor.close()
        return cursor.rowcount

    def delete_data_object(self, database_name: str, collection_name: str,
                           key_field: str, key_value: Any):
        cursor = self.connection.cursor()
        query = f"DELETE FROM {collection_name} WHERE {key_field} = %s"
        cursor.execute(query, (key_value,))
        self.connection.commit()
        cursor.close()
        return cursor.rowcount

    def get_data_objects_by_field(self, collection_name: str, field_name: str,
                                  field_value: Any, skip: int, limit: int):
        cursor = self.connection.cursor(dictionary=True)
        if field_value is not None:
            query = (f"SELECT * FROM {collection_name} WHERE "
                     f"{field_name} = %s LIMIT %s OFFSET %s")
            cursor.execute(query, (field_value, limit, skip))
        else:
            query = f"SELECT * FROM {collection_name} LIMIT %s OFFSET %s"
            cursor.execute(query, (limit, skip))
        results = cursor.fetchall()
        cursor.close()
        return results

    def update_by_field(self, collection_name: str, field_name: str,
                        old_value: Any, new_value: Any) -> int:
        cursor = self.connection.cursor()
        query = (f"UPDATE {collection_name} SET {field_name} = %s WHERE "
                 f"{field_name} = %s")
        cursor.execute(query, (new_value, old_value))
        affected_rows = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return affected_rows
