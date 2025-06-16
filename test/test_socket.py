import socketio

# Crear una instancia del cliente
sio = socketio.Client()

# Evento al conectarse
@sio.event
def connect():
    print('✅ Conectado al servidor Socket.IO')

# Evento al recibir una nueva suscripción
@sio.on('new-subscription')
def handle_new_subscription(data):
    print('📦 Nueva suscripción recibida:', data)

# Evento al desconectarse
@sio.event
def disconnect():
    print('❌ Desconectado del servidor')

# Conectar al servidor
sio.connect('http://localhost:3000')  # cambia el host si es necesario

# Mantener el cliente en ejecución
sio.wait()
