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
from classes.gpiosManager import GpiosManager
from werkzeug.utils import secure_filename

import logging
from classes.Filters import ExcludePathsFilter

DATASET_FOLDER = 'dataset'

app = Flask(__name__)
app.config['DATASET_FOLDER'] = DATASET_FOLDER

sio = socketio.Client()
load_dotenv(dotenv_path=".env", override=True)
api_url = os.getenv("API_URL")
tenant = os.getenv("TENANT_ID")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
bussines = os.getenv("NAME",'Subly')
# Datos de ISAPI
isapi_url = os.getenv("ISAPI_URL")
isapi_username = os.getenv("ISAPI_USERNAME")
isapi_password = os.getenv("ISAPI_PASSWORD")


subly = SublyBackend(tenant, api_url, username, password)
isapi = HikVision(isapi_url, isapi_username, isapi_password)
db = SqliteManager()

EXCLUDED_PATHS = ["/progress","/search-users"]

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(ExcludePathsFilter(EXCLUDED_PATHS))
manager = GpiosManager()


def update_db_now():
    global progress_value
    try:
        progress_value=10
        users_subly = subly.get_users()
        users = []
        for user in users_subly:
            dni = user.get('dni', '')
            if not dni or not dni.strip():
                logger.warning(f"Usuario {user.get('user_id')} no tiene DNI, se omitirá.")
                continue
            user['dni'] = user['dni'].strip()
            users.append(user)
        admins_subly = subly.get_admins()
        admins = []
        progress_value=40
        for admin in admins_subly:
            dni = admin.get('dni', '')
            if not dni or not dni.strip():
                logger.warning(f"Administrador {admin['user_id']} no tiene DNI, se omitirá.")
                continue
            admin['dni'] = admin['dni'].strip()
            admin['start_date'] = "2025-07-19T00:00:00.000Z"
            admin['end_date'] = "2035-07-19T00:00:00.000Z"
            admins.append(admin)
        progress_value=50
        counter = 0
        for user in users:
            total = len(users)
            counter += 1
            progress_value_aux = int((counter / total) *20 )
            progress_value = 60 + progress_value_aux
            try:
                user_db = db.get_subscription_by_dni(user['dni'])

                if user_db:
                    db.update_subscription_dates(
                            user['dni'].strip(),
                            user['end_date'],
                            user['name'],
                            user['lastname']
                        )
                    user_updated = db.get_subscription_by_dni(user['dni'].strip())
                    if isapi.veirfy_user(user['dni'].strip()):
                        isapi.update_days(user_updated)
                    else:
                        isapi.enroll_user(user_updated)
                else:
                    db.insert_subscription(user)
                    if isapi.enroll_user(user):
                        logger.info(f"Usuario {user['dni']} inscrito correctamente en HikVision.")
                        db.update_data_load_state(user['dni'], True)
                    else:
                        logger.error(f"Error al inscribir usuario {user['dni']} en HikVision.")
                        db.update_data_load_state(user['dni'], False)
                    
            except Exception as e:
                logger.error(f"Error al procesar usuario {user['dni']}: {e}")
                continue
        counter = 0
        for admin in admins:
            total = len(admins)
            counter += 1
            progress_value_aux = int((counter / total) *20 )
            progress_value = 80 + progress_value_aux
            try:
                if db.get_admin_by_dni(admin['dni']):
                    db.update_admin_dates(
                        admin['dni'],
                        admin['start_date'],
                        admin['end_date']
                    )
                    isapi.update_days(admin)
                else:
                    db.insert_admin(admin)
                    if isapi.enroll_user(admin):
                        logger.info(f"Administrador {admin['dni']} inscrito correctamente en HikVision.")
                        db.update_data_load_state(admin['dni'], True)
                    else:
                        logger.error(f"Error al inscribir administrador {admin['dni']} en HikVision.")
                        db.update_data_load_state(admin['dni'], False)
            except Exception as e:
                logger.error(f"Error al procesar administrador {admin['dni']}: {e}")
                continue

        logger.info(f"Total de usuarios obtenidos de Subly: {len(users)}")
    except Exception as e:
        logger.error(f"Error al iniciar la actualización de la base de datos: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    logger.info("Se finalizo de actualizar o agregar usuarios")
    return redirect(url_for('index'))

def update_local_database():
    '''Este hilo se encarga de actualizar la db con los usuarios activos de Subly todos los días a las 9PM'''
    while True:
        now = datetime.now()
        next_run = now.replace(hour=4, minute=30, second=30, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
        seconds_until_run = (next_run - now).total_seconds()
        time.sleep(seconds_until_run)
        update_db_now()
        



@sio.event
def connect():
    logger.info('Conectado al servidor Socket.IO')
    print('Conectado al servidor Socket.IO')

@sio.on('new-subscription')
def handle_new_subscription(data):
    logger.info('Nueva suscripción recibida: %s', data)
    try:
        if data['tenant'] == tenant:
            if db.get_subscription_by_dni(data['dni'].strip()):
                db.update_subscription_dates(
                    data['dni'].strip(),
                    data['end_date'],
                    data['name'],
                    data['lastname']
                )
                #primero lo actualizamos en la base de datos y luego lo traemos con las fechas modificadas para
                #actualizar los dias de acceso en HikVision
                user_updated = db.get_subscription_by_dni(data['dni'].strip())
                if isapi.veirfy_user(user_updated['dni']):
                    isapi.update_days(user_updated)
                else:
                    isapi.enroll_user(user_updated)
            else:
                db.insert_subscription(data)
                if isapi.enroll_user(data):
                    logger.info(f"Usuario {data['dni']} inscrito correctamente en HikVision.")
                    db.update_data_load_state(data['dni'], True)
                else:
                    logger.error(f"Error al inscribir usuario {data['dni']} en HikVision.")
                    db.update_data_load_state(data['dni'], False)
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
    error = None
    error_image_url = None

    if request.method == 'POST':
        image = request.files.get('image')
        dni = request.form.get('user')

        if image and dni:
            logger.info(f"id detectado: {dni}")
            new_filename = f"{secure_filename(dni)}.jpg"
            filepath = os.path.join(app.config['DATASET_FOLDER'], new_filename)
            from PIL import Image
            try:
                img = Image.open(image)
                rgb_img = img.convert('RGB')
                rgb_img.save(filepath, format='JPEG')
                image_url = url_for('get_image', filename=new_filename)

                result = isapi.enroll_face(dni)
                if result is False:
                    error = "Error al inscribir la cara del usuario. Por favor, inténtelo de nuevo."
                    error_image_url = url_for('static', filename='upload_failed.jpg')
                else:
                    db.update_face_load_state(dni, True)
            except Exception as e:
                error = f"Ocurrió un error procesando la imagen: {str(e)}"
                error_image_url = url_for('static', filename='upload_failed.jpg')

        else:
            error = "Debe seleccionar una imagen y un usuario válido."
            error_image_url = url_for('static', filename='upload_failed.jpg')

    return render_template('upload.html', image_url=image_url, error=error, error_image_url=error_image_url)

@app.route('/dataset/<filename>')
def get_image(filename):
    return send_from_directory(app.config['DATASET_FOLDER'], filename)


@app.route('/normal', methods=['POST'])
def normal_pass():
    resultado = "Pase normal generado exitosamente "
    logger.info(resultado)
    manager.turnstileOpen()
    return jsonify({'mensaje': resultado})


@app.route('/special', methods=['POST'])
def special_pass():
    resultado = "Pase especial generado exitosamente "
    logger.info(resultado)
    manager.armDown()
    return jsonify({'mensaje': resultado})

@app.route('/search-users')
def search_users():
    query = request.args.get('q', '').lower()
    users = db.get_all_subscriptions()
    admins = db.get_all_staff_members()
    users.extend(admins)
    filtered = [
        u for u in users
        if query in u['name'].lower() or query in u['lastname'].lower()
    ]
    return jsonify(filtered)

@app.route('/users')
def mostrar_usuarios():
    users = db.get_all_subscriptions()
    print(f"Usuarios obtenidos de la base de datos: {len(users)}")
    return render_template('users.html', usuarios=users)

@app.route('/admins')
def admins_view():
    admins = db.get_all_staff_members()
    print(f"Usuarios obtenidos de la base de datos: {len(admins)}")
    return render_template('admins.html', usuarios=admins)


@app.route('/update')
def update():
    global progress_value
    progress_value = 0
    return render_template('progress.html')

@app.route('/start-update')
def start_update():
    global progress_value
    update_db_now()
    return jsonify({"status": "complete"})

@app.route('/progress')
def get_progress():
    global progress_value
    return jsonify({"progress": progress_value})

# @app.route("/api/operations", methods=["POST"])
# def operations():
#     data = request.get_json(silent=True) or {}
#     dni = (data.get("dni") or "").strip()
#     if not dni:
#         return jsonify(error="dni requerido"), 400
#     db.delete_subscription(dni=dni)
#     return jsonify(status="deleted", dni=dni), 200


@app.route("/api/operations", methods=["POST"])
def operations():
    params = request.get_json()
    if not params:
        return jsonify({"status":"error","msg": "No se recibió JSON","name":bussines}), 400
    if params['tenant'] != tenant:
        return jsonify({"status":"error","msg":"no coincide el tenant","name":bussines})
    if params.get('dni') == None:
        return jsonify({"status":"error","msg":"no enviaste la cedula","name":bussines})
    if params.get('operation') ==None:
        return jsonify({"status":"error","msg":"no enviaste la accion","name":bussines})
    else:
        if params['operation'] == 'delete':
            if db.get_subscription_by_dni(params['dni']):
                db.delete_subscription(params['dni'])
                return jsonify({"status":"success","msg":"usuario eliminado con exito","name":bussines})
            else:
                return jsonify({"status":"error","msg":"no existe ese usuario en el registro local","name":bussines})
        if params['operation'] == 'register':
            subly.get_user_info(params['dni'])
        else:
            return jsonify({"status":"error","msg":"no existe esa operacion","name":bussines})


if __name__ == '__main__':
    threading.Thread(target=run_socket_client).start()
    app.run(host='0.0.0.0', port=8000)
