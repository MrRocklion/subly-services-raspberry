from Subly import SublyBackend
from HikVision import HikVision
from dotenv import load_dotenv
import os
from logger_config import logger

load_dotenv(dotenv_path=".env", override=True)
api_url = os.getenv("API_URL")
tenant = os.getenv("TENANT_ID")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

#datos de ISAPI
isapi_url = os.getenv("ISAPI_URL", api_url)
isapi_username = os.getenv("ISAPI_USERNAME", username)
isapi_password = os.getenv("ISAPI_PASSWORD", password)



backend = SublyBackend(tenant, api_url, username, password)

# test1 = {
#         "user_id": 26,
#         "name": "MARIA DOLORES",
#         "lastname": "CRESPO",
#         "start_date": "2025-05-22T00:00:00.000Z",
#         "end_date": "2025-06-12T00:00:00.000Z"
#         }
# isapi = HikVision(isapi_url, isapi_username, isapi_password)

users = backend.get_users()
print(f"Total users: {len(users)}")
# for user in users:
#     isapi.enroll_user(user)