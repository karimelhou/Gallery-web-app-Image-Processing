import os

class Photos:

    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_gallery_path(self, user_id, gallery_name):
        return os.path.join(self.project_root, 'static', 'Galleries', str(user_id), gallery_name)

    def get_all_gallery_photos(self, user_id, gallery_name):
        """
        Read photo names inside the photo folder
        :param user_id: User's unique identifier
        :param gallery_name: The name of the specific gallery
        :return: A list of photo names
        """
        gallery_path = self.get_gallery_path(user_id, gallery_name)

        if not os.path.exists(gallery_path):
            return []  # No photos if the gallery does not exist

        # List of valid image extensions
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

        # Get all files and filter out those that are not images
        photos = [name for name in os.listdir(gallery_path) if name.lower().endswith(valid_extensions)]
        return photos

    def delete_gallery_photo(self, user_id, gallery_name, photo_name):
        
        gallery_path = self.get_gallery_path(user_id, gallery_name)
        photo_path = os.path.join(gallery_path, photo_name)

        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)  
                return True
            except Exception as e:
                print(f"An error occurred while deleting the photo: {e}")  # Consider logging this error
                return False
        else:
            print("Photo does not exist")  # This can also be logged if needed
            return False


