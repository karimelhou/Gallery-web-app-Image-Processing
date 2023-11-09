import pymysql

class LoginDB:
    def __init__(self):
        self.config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'database': 'mygallerydb'
        }

    def login(self, username, password):
        try:
            conn = pymysql.connect(**self.config)
            cursor = conn.cursor()
            # Modify the SQL query to also select 'id' (or however your user ID field is named in your DB)
            cursor.execute("SELECT id, type FROM users WHERE username = %s AND password = %s", (username, password))
            user_data = cursor.fetchone()

            if user_data:
                user_id, user_type = user_data  # unpacking the tuple result
                # Include 'user_id' in the return dictionary
                return {'user_id': user_id, 'type': user_type, 'result': True}

            return {'result': False}
        except pymysql.MySQLError as e:
            print(str(e))
            return {'result': False}
        finally:
            cursor.close()
            conn.close()


    def register(self, username, password, user_type='normal'):
        try:
            conn = pymysql.connect(**self.config)
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return {'result': False, 'message': 'Username already exists'}

            # Insert new user
            cursor.execute("INSERT INTO users (username, password, type) VALUES (%s, %s, %s)", (username, password, user_type))
            conn.commit()
            
            return {'result': True, 'message': 'User registered successfully'}
        except pymysql.MySQLError as e:
            print(str(e))
            return {'result': False, 'message': 'Registration failed'}
        finally:
            cursor.close()
            conn.close()