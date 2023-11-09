import pymysql
import os
import shutil


class GalleryDB:
    def __init__(self):
        self.config = {
            'user': 'root',
            'password': '',  
            'host': 'localhost',
            'database': 'mygallerydb',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        

    def connect(self):
        return pymysql.connect(**self.config)

    def create_gallery(self, user_id, gallery_name):
        """Create a new gallery for a user."""
        connection = self.connect()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO galleries (user_id, gallery_name) VALUES (%s, %s)"
                cursor.execute(sql, (user_id, gallery_name))
            connection.commit()

            # Create a directory for this gallery if necessary
            # Assuming galleries are stored in directories named after the gallery
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This navigates up to your project root from the current script location
            gallery_path = os.path.join(project_root, 'static', 'Galleries', str(user_id), gallery_name)            
            os.makedirs(gallery_path, exist_ok=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            connection.close()
        return True

    def get_galleries(self, user_id):
        connection = self.connect()
        galleries = []
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id, gallery_name FROM galleries WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchall()
                print(f"Database returned: {result}")  # Log the raw result from the database

                for row in result:
                    galleries.append({'id': row['id'], 'gallery_name': row['gallery_name']})  # Adjusted to match the dictionary key with the column names
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()
        return galleries


    def delete_gallery(self, user_id, gallery_id):
        connection = self.connect()
        try:
            with connection.cursor() as cursor:
                # Fetch the gallery name before deletion
                sql = "SELECT gallery_name FROM galleries WHERE user_id = %s AND id = %s"
                cursor.execute(sql, (user_id, gallery_id))
                result = cursor.fetchone()
                
                if not result:
                    return False  # Gallery not found or not owned by the user

                gallery_name = result['gallery_name']

                # Delete the gallery from the database
                sql = "DELETE FROM galleries WHERE id = %s"
                cursor.execute(sql, (gallery_id,))
                connection.commit()

                # Delete the directory associated with this gallery
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This navigates up to your project root from the current script location
                gallery_path = os.path.join(project_root, 'static', 'Galleries', str(user_id), gallery_name)
                if os.path.exists(gallery_path):
                    shutil.rmtree(gallery_path)
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            connection.close()
        return True


    def rename_gallery(self, user_id, gallery_id, new_gallery_name):
        connection = self.connect()
        try:
            with connection.cursor() as cursor:
                # Fetch the current gallery name
                sql = "SELECT gallery_name FROM galleries WHERE user_id = %s AND id = %s"
                cursor.execute(sql, (user_id, gallery_id))
                result = cursor.fetchone()

                if not result:
                    return False  # Gallery not found or not owned by the user

                old_gallery_name = result['gallery_name']

                # Update the gallery name in the database
                sql = "UPDATE galleries SET gallery_name = %s WHERE id = %s AND user_id = %s"
                cursor.execute(sql, (new_gallery_name, gallery_id, user_id))
                connection.commit()

                # Rename the directory associated with this gallery
                base_dir = os.path.dirname(os.path.dirname(__file__))  # This should get the project's root directory based on the current script location.
                old_gallery_path = os.path.join(base_dir, 'static', 'Galleries', str(user_id), old_gallery_name)
                new_gallery_path = os.path.join(base_dir, 'static', 'Galleries', str(user_id), new_gallery_name)

                if os.path.exists(old_gallery_path):
                    os.rename(old_gallery_path, new_gallery_path)
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            connection.close()
        return True

