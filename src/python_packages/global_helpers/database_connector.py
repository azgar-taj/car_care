from enum import Enum
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .logging_helpers import setup_logger
import os

logger = setup_logger(__name__)

# Get the environment variables
mongo_db_username = os.getenv("MONGO_DB_USERNAME")
mongo_db_password = os.getenv("MONGO_DB_PASSWORD")
mongo_db_name = os.getenv("MONGO_DB_NAME")

# Constants
USER_COLLECTION = "UserInfo"
ADMIN_COLLECTION = "AdminInfo"
DATABASE_CONNECTION = None


class DatabaseType(Enum):
    """
    Enum to represent the type of database
    """
    USER = "user",
    ADMIN = "admin"


class DatabaseConnector:
    """
    Class to connect to the database
    """
    def __init__(self, database_type: DatabaseType):
        logger.debug("Connecting to the database")
        # Check if the environment variables are set
        if mongo_db_username is None or mongo_db_password is None or mongo_db_name is None:
            raise ValueError("MongoDB environment variables are not set")
        # Use a global variable to store the connection
        global DATABASE_CONNECTION
        if DATABASE_CONNECTION is None:
            logger.debug("Creating a new connection")
            uri = f"mongodb+srv://{mongo_db_username}:{mongo_db_password}@{mongo_db_name}.uvpl1by.mongodb.net/?retryWrites=true&w=majority"
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            DATABASE_CONNECTION = self.client
        else:
            logger.debug("Using the existing connection")
            self.client = DATABASE_CONNECTION

        logger.debug("Connection established")
        # Use the global connection
        self.db = self.client[mongo_db_name]
        self.collection = self.db[USER_COLLECTION] if database_type == DatabaseType.USER else self.db["AdminInfo"]
    
    def get_users(self):
        logger.debug("Getting users from the database")
        return [user['username'] for user in self.collection.find()]
