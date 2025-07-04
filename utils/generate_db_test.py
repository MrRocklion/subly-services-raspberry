from classes.Subly import SublyBackend
from database.db_manager import SqliteManager
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env", override=True)
api_url = os.getenv("API_URL")
tenant = os.getenv("TENANT_ID")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

subly = SublyBackend(tenant, api_url, username, password)

db = SqliteManager()

users_subly = subly.get_users()
users = []
for user in users_subly:
    dni = user.get('dni', '')
    if not dni or not dni.strip():
        print(f"Usuario {user.get('user_id')} no tiene DNI, se omitirá.")
        continue
    user['dni'] = user['dni'].strip()
    users.append(user)

for user in users:
    total = len(users)
    try:
        user_db = db.get_subscription_by_dni(user['dni'])
        if user_db:
            if user['end_date'] < user_db['end_date']:
                continue
            db.update_subscription_dates(
                user['dni'].strip(),
                user['end_date']
            )
            user_updated = db.get_subscription_by_dni(user['dni'].strip())
        else:
            db.insert_subscription(user)
    except Exception as e:
        continue

