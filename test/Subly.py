import requests
from logger_config import logger
import json


class SublyBackend:
    def __init__(self, tenant, api_url,username, password):
        self.tenant = tenant
        self.api_url = api_url
        self.user_name = username
        self.pass_word = password
        self.jwt = self.get_jwt()
    

    def get_jwt(self):
        url = f"{self.api_url}/api/auth/login"
        payload = json.dumps({
            "email": self.user_name,
            "password": self.pass_word
        })
        headers = {
            'x-tenant-id': self.tenant,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            logger.info(response)
            if response.status_code == 201:
                data = response.json()
                return data['result']['token']
            else:
                logger.info(f"Error al obtener token: {response.status_code}")
        except Exception as e:
            logger.error(f"Excepción al obtener token: {e}")
        return ''

    def get_users(self):
        url = f"{self.api_url}/api/users/all/active-subscription"
        headers = {
            'x-tenant-id': self.tenant,
            'Authorization': f'Bearer {self.jwt}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('result', [])
            elif response.status_code == 401:
                logger.error("Token de autenticación no válido o expirado.")
                self.jwt = self.get_jwt()
            else:
                logger.warning(f"Error en la solicitud: {response.status_code}")
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {e}")
        return []