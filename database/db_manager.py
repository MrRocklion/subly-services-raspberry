import sqlite3

SUBSCRIPTION_COLUMNS = [
    "id", "start_date", "end_date", "name", "lastname", "duration",
    "entries", "user_id", "dni", "image_url", "data_loaded", "face_loaded"
]

class SqliteManager:
    def __init__(self):
        self.create_tables()

    def create_tables(self):
        sql_statements = [
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                name TEXT,
                lastname TEXT,
                duration INTEGER,
                entries INTEGER,
                user_id INTEGER,
                dni TEXT,
                image_url TEXT,
                data_loaded BOOLEAN DEFAULT false,
                face_loaded BOOLEAN DEFAULT false
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS staff_members (
                id INTEGER PRIMARY KEY,
                admin_id INTEGER,
                dni TEXT,
                name TEXT,
                lastname TEXT,
                email TEXT,
                account_type TEXT,
                image_url TEXT,
                data_loaded BOOLEAN DEFAULT false,
                face_loaded BOOLEAN DEFAULT false
            );
            """
        ]
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                for statement in sql_statements:
                    cursor.execute(statement)
                conn.commit()
                print("Tablas creadas correctamente.")
        except sqlite3.Error as e:
            print("Error al crear las tablas:", e)

    def insert_subscription(self, params):
        """Inserta una nueva suscripción en la tabla."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO subscriptions (
                        start_date, end_date, name, lastname,
                        duration, entries, user_id, dni, image_url,
                        data_loaded, face_loaded
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    params['start_date'],
                    params['end_date'],
                    params['name'],
                    params['lastname'],
                    params['duration'],
                    int(params['entries']),
                    params['user_id'],
                    params['dni'],
                    params['image_url'],
                    params.get('data_loaded', False),
                    params.get('face_loaded', False)
                ))
                conn.commit()
                print("Suscripción insertada correctamente.")
        except sqlite3.Error as e:
            print("Error al insertar la suscripción:", e)

    def insert_admin(self, params):
        """Inserta un nuevo administrador en staff_members."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO staff_members (
                        admin_id, dni, name, lastname, email,
                        account_type, image_url, data_loaded, face_loaded
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    params['admin_id'],
                    params['dni'],
                    params['name'],
                    params['lastname'],
                    params['email'],
                    params['account_type'],
                    params.get('image_url', None),
                    params.get('data_loaded', False),
                    params.get('face_loaded', False)
                ))
                conn.commit()
                print("Admin insertado correctamente.")
        except sqlite3.Error as e:
            print("Error al insertar el administrador:", e)

    def get_subscription_by_user_id(self, user_id):
        """Busca en subscriptions la fila que coincida con el user_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT {", ".join(SUBSCRIPTION_COLUMNS)}
                    FROM subscriptions WHERE user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()
                return dict(zip(SUBSCRIPTION_COLUMNS, row)) if row else None
        except sqlite3.Error as e:
            print("Error al buscar la suscripción:", e)
            return False

    def get_subscription_by_dni(self, dni):
        """Busca en subscriptions la fila que coincida con el dni proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT {", ".join(SUBSCRIPTION_COLUMNS)}
                    FROM subscriptions WHERE dni = ?
                ''', (dni,))
                row = cursor.fetchone()
                return dict(zip(SUBSCRIPTION_COLUMNS, row)) if row else None
        except sqlite3.Error as e:
            print("Error al buscar la suscripción:", e)
            return False

    def get_admin_by_id(self, admin_id):
        """Busca en staff_members la fila que coincida con el admin_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM staff_members WHERE admin_id = ?
                ''', (admin_id,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print("Error al buscar el administrador:", e)
            return False

    def update_subscription_dates(self, dni, new_start_date, new_end_date):
        """Actualiza start_date y end_date en la suscripción con el user_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscriptions 
                    SET start_date = ?, end_date = ? 
                    WHERE dni = ?
                ''', (new_start_date, new_end_date, dni))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Suscripción de usuario {dni} actualizada correctamente.")
                    return True
                else:
                    print(f"No se encontró la suscripción con dni {dni}.")
                    return False
        except sqlite3.Error as e:
            print("Error al actualizar la suscripción:", e)
            return False

    def update_data_load_state(self, dni, data_loaded):
        """Actualiza el estado de data_loaded en la suscripción con el user_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscriptions 
                    SET data_loaded = ? 
                    WHERE dni = ?
                ''', (data_loaded, dni))
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    return False
        except sqlite3.Error as e:
            return False

    def update_face_load_state(self, dni, face_loaded):
        """Actualiza el estado de face_loaded en la suscripción con el user_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscriptions 
                    SET face_loaded = ? 
                    WHERE dni = ?
                ''', (face_loaded, dni))
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                else:
                    return False
        except sqlite3.Error as e:
            return False

    def get_all_subscriptions(self):
        """Obtiene todas las suscripciones de la base de datos."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute(f'SELECT {", ".join(SUBSCRIPTION_COLUMNS)} FROM subscriptions')
                rows = cursor.fetchall()
                return [dict(zip(SUBSCRIPTION_COLUMNS, row)) for row in rows] if rows else []
        except sqlite3.Error as e:
            print("Error al obtener las suscripciones:", e)
            return []
