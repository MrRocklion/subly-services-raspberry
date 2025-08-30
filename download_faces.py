from classes.HikVision import HikVision
import os
from dotenv import load_dotenv
from database.db_manager import SqliteManager
load_dotenv(dotenv_path=".env", override=True)
isapi_url = os.getenv("ISAPI_URL")
isapi_username = os.getenv("ISAPI_USERNAME")
isapi_password = os.getenv("ISAPI_PASSWORD")


isapi = HikVision(isapi_url, isapi_username, isapi_password)
for i in range(0,20):
    result = isapi.get_all_image_device(number=i)




