from classes.HikVision import HikVision
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env", override=True)

isapi_url = os.getenv("ISAPI_URL")
isapi_username = os.getenv("ISAPI_USERNAME")
isapi_password = os.getenv("ISAPI_PASSWORD")



isapi = HikVision(isapi_url, isapi_username, isapi_password)

if isapi.veirfy_user("15451"):
    print("User exists")
else:
    print("User does not exist")