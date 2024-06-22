import requests
from car_service_contracts.auth_service_contracts import AuthServiceContracts
from car_service_contracts.models import User

class CarAuthClient:
    def __init__(self, endpoint: str = "http://localhost:8000/"):
        self.endpoint = endpoint

    def get_token(self, username: str, password: str) -> str:
        response = requests.post(
            self.endpoint + AuthServiceContracts.TOKEN_URI,
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        return response.json()['access_token']

    def create_user(self, username: str, password: str):
        response = requests.post(
            self.endpoint + AuthServiceContracts.REGISTER_URI,
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        return response.json()

    def get_user_metadata(self, token: str):
        response = requests.get(
            self.endpoint + AuthServiceContracts.USER_METADATA_URI,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    def update_user(self, token: str, user: User):
        response = requests.patch(
            self.endpoint + AuthServiceContracts.UPDATE_URI,
            headers={"Authorization": f"Bearer {token}"},
            json=user.dict(),
        )
        response.raise_for_status()
        return response.json()

class CarAuthClientWrapper(CarAuthClient):
    def __init__(self, endpoint: str = "http://localhost:8000/", username: str = None, password: str = None):
        super().__init__(endpoint)
        self.token = self.get_token(username, password)

    def create_user(self, username: str, password: str):
        return super().create_user(username, password)

    def get_user_metadata(self):
        return super().get_user_metadata(self.token)

    def update_user(self, user: User):
        return super().update_user(self.token, user)