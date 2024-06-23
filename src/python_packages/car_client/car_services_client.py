from car_service_contracts.auth_service_contracts import CarServicesContracts
import requests

from car_service_contracts.models import Service
from .car_auth_client import CarAuthClientWrapper

class CarServicesClient:
    def __init__(self, service_endpoint, auth_endpoint, username, password):
        self.endpoint = service_endpoint
        self.auth_client = CarAuthClientWrapper(endpoint=auth_endpoint,
                                                username=username,
                                                password=password)
    
    def get_services(self):
        response = requests.get(
            self.endpoint + CarServicesContracts.SERVICES_URI,
            headers={"Authorization": f"Bearer {self.auth_client.token}"},
        )
        response.raise_for_status()
        return response.json()

    def add_service(self, service: Service):
        response = requests.post(
            self.endpoint + CarServicesContracts.SERVICE_URI,
            headers={"Authorization": f"Bearer {self.auth_client.token}"},
            json=service.dict(),
        )
        response.raise_for_status()
        return response.json()

    def delete_service(self, service_id):
        response = requests.delete(
            self.endpoint + CarServicesContracts.SERVICE_URI,
            headers={"Authorization": f"Bearer {self.auth_client.token}"},
            json={"service_id": service_id},
        )
        response.raise_for_status()
        return response.json()

    def update_service(self, service_id, service: Service):
        response = requests.put(
            self.endpoint + CarServicesContracts.SERVICE_URI,
            headers={"Authorization": f"Bearer {self.auth_client.token}"},
            json={"service_id": service_id, "service": service.dict()},
        )
        response.raise_for_status()
        return response.json()
