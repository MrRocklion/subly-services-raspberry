import threading
import time
from datetime import datetime, timedelta
from classes.HikVision import HikVision
from classes.Subly import SublyBackend
from classes.Logger import logger
from database.db_manager import SqliteManager
from dotenv import load_dotenv
import socketio
from flask import Flask, render_template, request, redirect, url_for, send_from_directory,jsonify
import os
import uuid
from werkzeug.utils import secure_filename


DATASET_FOLDER = 'dataset'

app = Flask(__name__)
app.config['DATASET_FOLDER'] = DATASET_FOLDER

sio = socketio.Client()
load_dotenv(dotenv_path=".env", override=True)
api_url = os.getenv("API_URL")
tenant = os.getenv("TENANT_ID")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Datos de ISAPI
isapi_url = os.getenv("ISAPI_URL", api_url)
isapi_username = os.getenv("ISAPI_USERNAME", username)
isapi_password = os.getenv("ISAPI_PASSWORD", password)

subly = SublyBackend(tenant, api_url, username, password)
isapi = HikVision(isapi_url, isapi_username, isapi_password)
db = SqliteManager()

def update_local_database():
    '''Este hilo se encarga de actualizar la db con los usuarios activos de Subly todos los días a las 9PM'''

    while True:
        now = datetime.now()
        next_run = now.replace(hour=4, minute=30, second=30, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)

        seconds_until_run = (next_run - now).total_seconds()
        time.sleep(seconds_until_run)
        users = []
        while not users:
            try:
                users = subly.get_users()
                if not users:
                    logger.warning("No se encontraron usuarios en Subly. Reintentando en 60 segundos...")
                    time.sleep(60)
            except Exception as e:
                logger.error(f"Error al obtener usuarios: {e}. Reintentando en 60 segundos...")
                time.sleep(60)
        for user in users:
            try:
                if db.get_subscription_by_user_id(user['user_id']):
                    db.update_subscription_dates(
                        user['user_id'],
                        user['start_date'],
                        user['end_date']
                    )
                    isapi.update_days(user)
                else:
                    db.insert_subscription(user)
                    if isapi.enroll_user(user):
                        logger.info(f"Usuario {user['user_id']} inscrito correctamente en HikVision.")
                        db.update_data_load_state(user['user_id'], True)
                    else:
                        logger.error(f"Error al inscribir usuario {user['user_id']} en HikVision.")
                        db.update_data_load_state(user['user_id'], False)
                    
            except Exception as e:
                logger.error(f"Error al procesar usuario {user['user_id']}: {e}")
                continue
        logger.info(f"Total de usuarios obtenidos de Subly: {len(users)}")



@sio.event
def connect():
    logger.info('Conectado al servidor Socket.IO')
    print('Conectado al servidor Socket.IO')

@sio.on('new-subscription')
def handle_new_subscription(data):
    logger.info('Nueva suscripción recibida: %s', data)
    try:
        if db.get_subscription_by_user_id(data['user_id']):
            db.update_subscription_dates(
                data['user_id'],
                data['start_date'],
                data['end_date']
            )
            isapi.update_days(data)
        else:
            db.insert_subscription(data)
            if isapi.enroll_user(data):
                logger.info(f"Usuario {data['user_id']} inscrito correctamente en HikVision.")
                db.update_data_load_state(data['user_id'], True)
            else:
                logger.error(f"Error al inscribir usuario {data['user_id']} en HikVision.")
                db.update_data_load_state(data['user_id'], False)
    except Exception as e:
        logger.error('Error al procesar la nueva suscripción: %s', e)
        return

@sio.event
def disconnect():
    logger.info('Desconectado del servidor Socket.IO')


def run_socket_client():
    try:
        sio.connect(api_url)  # Cambia por tu URL real si es necesario
        sio.wait()
    except Exception as e:
        logger.error('Error al conectar al servidor Socket.IO: %s', e)
        print("Error al conectar:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    image_url = None
    if request.method == 'POST':
        image = request.files.get('image')
        user_id = request.form.get('user')
        if image:
            # Extensión original
            orig_name = secure_filename(image.filename)
            name, ext = os.path.splitext(orig_name)
            logger.info(f"id detectado: {user_id}")
            if user_id:
                new_filename = f"{user_id}{ext}"
                filepath = os.path.join(app.config['DATASET_FOLDER'], new_filename)
                image.save(filepath)

                image_url = url_for('get_image', filename=new_filename)
                isapi.enroll_face(user_id)

            #isapi.enroll_face(user_id)
            
            
    return render_template('upload.html', image_url=image_url)


@app.route('/dataset/<filename>')
def get_image(filename):
    return send_from_directory(app.config['DATASET_FOLDER'], filename)

@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/search-users')
def search_users():
    query = request.args.get('q', '').lower()
    users = db.get_all_subscriptions()
    filtered = [
        u for u in users
        if query in u['name'].lower() or query in u['lastname'].lower()
    ]
    return jsonify(filtered)

if __name__ == '__main__':
    threading.Thread(target=run_socket_client).start()
    app.run(port=5000)
