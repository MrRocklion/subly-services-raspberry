import os
import shutil
from database.db_manager import SqliteManager
from classes.Subly import SublyBackend
from dotenv import load_dotenv

db = SqliteManager()

load_dotenv(dotenv_path=".env", override=True)
api_url = os.getenv("API_URL")
tenant = os.getenv("TENANT_ID")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

subly = SublyBackend(tenant, api_url, username, password)

carpeta_origen = "dataset_v1"
carpeta_destino = "dataset_v1_renombrado"
os.makedirs(carpeta_destino, exist_ok=True)

def listar_imagenes_en_diccionario(path):
    imagenes = []
    for idx, archivo in enumerate(os.listdir(path)):
        if archivo.lower().endswith('.jpg'):
            nombre_sin_extension = os.path.splitext(archivo)[0]
            imagenes.append(nombre_sin_extension)
    return imagenes

lista_imagenes = listar_imagenes_en_diccionario(path='./dataset_v1')
counter = 0
for nombre in lista_imagenes:
    user = db.get_subscription_by_user_id(int(nombre))
    if user:
        nuevo_nombre = f"{user['dni']}.jpg"
        origen = os.path.join(carpeta_origen, nombre+".jpg")
        destino = os.path.join(carpeta_destino, nuevo_nombre)
        shutil.copy2(origen, destino)
    else:
        user_info = subly.get_user_info(int(nombre))
        nuevo_nombre = f"{user_info['dni']}.jpg"
        print(nuevo_nombre)
        origen = os.path.join(carpeta_origen, nombre+".jpg")
        destino = os.path.join(carpeta_destino, nuevo_nombre)
        shutil.copy2(origen, destino)


print("Copia y renombrado completado.")

