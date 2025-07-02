import sqlite3
from datetime import datetime

SUBSCRIPTION_COLUMNS = [
    "id", "start_date", "end_date", "name", "lastname",
    "user_id", "dni", "image_url", "data_loaded", "face_loaded"
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
                start_date TEXT,
                end_date TEXT,
                name TEXT,
                lastname TEXT,
                user_id INTEGER,
                dni TEXT,
                image_url TEXT,
                data_loaded BOOLEAN DEFAULT false,
                face_loaded BOOLEAN DEFAULT false
            );
            """,
                """
            CREATE TABLE IF NOT EXISTS pending_subscriptions (
                id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                name TEXT,
                lastname TEXT,
                user_id INTEGER,
                dni TEXT,
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
                        user_id, dni, image_url,
                        data_loaded, face_loaded
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    params['start_date'],
                    params['end_date'],
                    params['name'],
                    params['lastname'],
                    params['user_id'],
                    params['dni'],
                    params.get('image_url', None),
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
                        start_date, end_date, name, lastname,
                        user_id, dni, image_url,
                        data_loaded, face_loaded
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    params['start_date'],
                    params['end_date'],
                    params['name'],
                    params['lastname'],
                    params['user_id'],
                    params['dni'],
                    params.get('image_url', None),
                    params.get('data_loaded', False),
                    params.get('face_loaded', False)
                ))
                conn.commit()
                print("Admin insertado correctamente.")
        except sqlite3.Error as e:
            print("Error al insertar el administrador:", e)
    
    def insert_pending_subscription(self, params):
        """Inserta una nueva suscripción pendiente en pending_subscriptions."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO pending_subscriptions (
                        start_date, end_date, name, lastname,
                        user_id, dni, image_url,
                        data_loaded, face_loaded
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    params['start_date'],
                    params['end_date'],
                    params['name'],
                    params['lastname'],
                    params['user_id'],
                    params['dni'],
                    params.get('image_url', None),
                    params.get('data_loaded', False),
                    params.get('face_loaded', False)
                ))
                conn.commit()
                print("Suscripción pendiente insertada correctamente.")
        except sqlite3.Error as e:
            print("Error al insertar la suscripción pendiente:", e)

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

    def get_admin_by_dni(self, dni):
        """Busca en staff_members la fila que coincida con el admin_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM staff_members WHERE dni = ?
                ''', (dni,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print("Error al buscar el administrador:", e)
            return False

    def update_subscription_dates(self, dni, new_end_date):
        """Actualiza start_date y end_date en la suscripción con el user_id proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE subscriptions 
                    SET  end_date = ? 
                    WHERE dni = ?
                ''', (new_end_date, dni))
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
    def update_admin_dates(self, dni, new_start_date, new_end_date):
        """Actualiza start_date y end_date en la tabla de staff_members con el dni proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE staff_members 
                    SET start_date = ?, end_date = ? 
                    WHERE dni = ?
                ''', (new_start_date, new_end_date, dni))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Administrador con DNI {dni} actualizado correctamente.")
                    return True
                else:
                    print(f"No se encontró el administrador con DNI {dni}.")
                    return False
        except sqlite3.Error as e:
            print("Error al actualizar el administrador:", e)
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
    
    def update_admin_data_load_state(self, dni, data_loaded):
        """Actualiza el estado de data_loaded en la tabla de staff_members con el dni proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE staff_members 
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

    def update_face_load_state_admin(self, dni, face_loaded):
        """Actualiza el estado de face_loaded en la tabla de staff_members con el dni proporcionado."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE staff_members 
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
        
    def update_face_load_state(self, dni, face_loaded):
        """Actualiza el estado de face_loaded en la suscripción con el dni proporcionado."""
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
        """Obtiene todas las suscripciones activas en base al rango de fechas."""
        try:
            today = datetime.now().date()
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                query = f'''
                    SELECT {", ".join(SUBSCRIPTION_COLUMNS)}
                    FROM subscriptions
                    WHERE DATE(?) >= DATE(start_date) AND DATE(?) < DATE(end_date)
                '''
                cursor.execute(query, (today, today))
                rows = cursor.fetchall()
                return [dict(zip(SUBSCRIPTION_COLUMNS, row)) for row in rows] if rows else []
        except sqlite3.Error as e:
            print("Error al obtener las suscripciones:", e)
            return []
    def get_all_staff_members(self):
        """Obtiene todos los administradores"""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                query = f'''
                    SELECT {", ".join(SUBSCRIPTION_COLUMNS)}
                    FROM staff_members
                '''
                cursor.execute(query)  # ✅ Sin parámetros
                rows = cursor.fetchall()
                return [dict(zip(SUBSCRIPTION_COLUMNS, row)) for row in rows] if rows else []
        except sqlite3.Error as e:
            print("Error al obtener los administradores:", e)
            return []

    

    def delete_subscription(self,dni):
        """Elimina una suscripción por su DNI."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM subscriptions WHERE dni = ?', (dni,))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Suscripción con DNI {dni} eliminada correctamente.")
                    return True
                else:
                    print(f"No se encontró la suscripción con DNI {dni}.")
                    return False
        except sqlite3.Error as e:
            print("Error al eliminar la suscripción:", e)
            return False
    
    def delete_pending_subscription(self, dni):
        """Elimina una suscripción pendiente por su DNI."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM pending_subscriptions WHERE dni = ?', (dni,))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Suscripción pendiente con DNI {dni} eliminada correctamente.")
                    return True
                else:
                    print(f"No se encontró la suscripción pendiente con DNI {dni}.")
                    return False
        except sqlite3.Error as e:
            print("Error al eliminar la suscripción pendiente:", e)
            return False
    
    def delete_staff_member(self, dni):
        """Elimina un administrador por su DNI."""
        try:
            with sqlite3.connect('app.db') as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM staff_members WHERE dni = ?', (dni,))
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"Administrador con DNI {dni} eliminado correctamente.")
                    return True
                else:
                    print(f"No se encontró el administrador con DNI {dni}.")
                    return False
        except sqlite3.Error as e:
            print("Error al eliminar el administrador:", e)
            return False