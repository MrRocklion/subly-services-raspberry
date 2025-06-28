from classes.HikVision import HikVision
import os
from dotenv import load_dotenv
from database.db_manager import SqliteManager
load_dotenv(dotenv_path=".env", override=True)
isapi_url = os.getenv("ISAPI_URL")
isapi_username = os.getenv("ISAPI_USERNAME")
isapi_password = os.getenv("ISAPI_PASSWORD")

db = SqliteManager()
def listar_imagenes_en_diccionario():
    imagenes = []
    for idx, archivo in enumerate(os.listdir('./dataset')):
        if archivo.lower().endswith('.jpg'):
            nombre_sin_extension = os.path.splitext(archivo)[0]
            imagenes.append(nombre_sin_extension)
    return imagenes

diccionario_imagenes = listar_imagenes_en_diccionario()
isapi = HikVision(isapi_url, isapi_username, isapi_password)
for imagen in diccionario_imagenes:
    print(f"Procesando imagen: {imagen}")
    if isapi.enroll_face(imagen):
        db.update_face_load_state(imagen, True)
        print(f"Imagen {imagen} procesada correctamente.")
    else:
        print(f"Error al procesar la imagen {imagen}.")

