from enum import Enum
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .logging_helpers import setup_logger
from .constants import MONGO_URL_CONNECTION
from .models import User, Service
import os
from bson import json_util

logger = setup_logger(__name__)

# Get the environment variables
mongo_db_username = os.getenv("MONGO_DB_USERNAME")
mongo_db_password = os.getenv("MONGO_DB_PASSWORD")
mongo_db_name = os.getenv("MONGO_DB_NAME")

DATABASE_CONNECTION = None

class DatabaseType(Enum):
    UserDatabase = 1,
    CarServicesDatabase = 2,
    OrderDatabase = 3,
    AdminDatabase = 4

database_mappping = {
    DatabaseType.UserDatabase: "UserInfoNew",
    DatabaseType.CarServicesDatabase: "CarServices",
    DatabaseType.OrderDatabase: "Orders",
    DatabaseType.AdminDatabase: "AdminInfo"
}

class DatabaseConnector:
    """
    Class to connect to the database
    """
    def __init__(self):
        logger.debug("Connecting to the database")

        # Check if the environment variables are set
        if mongo_db_username is None or mongo_db_password is None or mongo_db_name is None:
            raise ValueError("MongoDB environment variables are not set")

        # Use a global variable to store the connection
        global DATABASE_CONNECTION
        if DATABASE_CONNECTION is None:
            logger.debug("Creating a new connection")
            uri = MONGO_URL_CONNECTION.format(mongo_db_username=mongo_db_username,
                                              mongo_db_password=mongo_db_password,
                                              mongo_db_name=mongo_db_name)
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            DATABASE_CONNECTION = self.client
        else:
            logger.debug("Using the existing connection")
            self.client = DATABASE_CONNECTION

        logger.debug("Connection established")
        # Use the global connection
        self.db = self.client[mongo_db_name]


class AuthenticationDatabaseConnector(DatabaseConnector):
    """
    Class to connect to the authentication database
    """
    def __init__(self):
        super().__init__()
        self.collection = self.db[database_mappping[DatabaseType.UserDatabase]]
 
    def get_users(self):
        logger.debug("Getting users from the database")
        return [user['username'] for user in self.collection.find()]

    def get_user(self, username: str):
        logger.debug(f"Getting user {username} from the database")
        return self.collection.find_one({"username": username})

    def add_user(self, user: User):
        if self.get_user(user.username):
            logger.error(f"User {user.username} already exists")
            return ''
        logger.debug(f"Adding user {user} to the database")
        return str(self.collection.insert_one(user.dict()).inserted_id)

    def delete_user(self, username: str):
        logger.debug(f"Deleting user {username} from the database")
        return self.collection.delete_one({"username": username}).deleted_count

    def update_user(self, username: str, new_user: User):
        logger.debug(f"Updating user {username} in the database")
        return self.collection.update_one({"username": username}, {"$set": new_user}).modified_count

    def get_admins(self):
        logger.debug("Getting admins from the database")
        return [admin['username'] for admin in self.collection.find() if admin['isAdmin']]

    def get_admin(self, username: str):
        logger.debug(f"Getting admin {username} from the database")
        return self.collection.find_one({"username": username})

    def add_admin(self, admin: User):
        logger.debug(f"Adding admin {admin} to the database")
        return self.collection.insert_one(
            {
                "username": admin.username, 
                "password": admin.password, 
                "isAdmin": True
            }).inserted_id

    def delete_admin(self, username):
        logger.debug(f"Deleting admin {username} from the database")
        return self.collection.delete_one({"username": username}).deleted_count

    def update_admin(self, username, new_admin: User):
        logger.debug(f"Updating admin {username} in the database")
        return self.collection.update_one(
                {"username": username},
                {
                    "$set": {
                        "username": new_admin.username,
                        "password": new_admin.password,
                        "isAdmin": True
                    }
                }
            ).modified_count


class CarServicesDatabase(DatabaseConnector):
    """
    Class to connect to the car services database
    """
    def __init__(self):
        super().__init__()
        self.collection = self.db[database_mappping[DatabaseType.CarServicesDatabase]]

    def get_services(self):
        logger.debug("Getting services from the database")
        return [service for service in self.collection.find()]

    def get_service(self, service_name: str):
        logger.debug(f"Getting service {service_name} from the database")
        return self.collection.find_one({"service_name": service_name})

    def add_service(self, service: Service):
        logger.debug(f"Adding service {service} to the database")
        return self.collection.insert_one(
            {
                "service_name": service.service_name, 
                "service_price": service.service_price, 
                "service_description": service.service_description, 
                "service_duration": service.service_duration
            }).inserted_id

    def delete_service(self, service_name: str):
        logger.debug(f"Deleting service {service_name} from the database")
        return self.collection.delete_one({"service_name": service_name}).deleted_count

    def update_service(self, service_name: str, new_service: Service):
        logger.debug(f"Updating service {service_name} in the database")
        return self.collection.update_one({"service_name": service_name}, 
                                   {"$set": 
                                       {
                                           "service_name": new_service.service_name,
                                           "service_price": new_service.service_price,
                                           "service_description": new_service.service_description,
                                           "service_duration": new_service.service_duration
                                       }
                                   }).modified_count
