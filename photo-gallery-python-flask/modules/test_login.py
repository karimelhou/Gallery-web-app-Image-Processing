from LoginDb import LoginDB  
from GalleryDB import GalleryDB

def test_Gallery_db():
    # Replace with test username and password
    test_username = "test_user"
    test_password = "test_password"

    login_db = LoginDB()

    # Test the loginDB method
    result = login_db.loginDB(test_username, test_password)

    if result['result']:
        print(f"Login successful. User type: {result['type']}")
    else:
        print("Login failed.")

if __name__ == "__main__":
    test_Gallery_db()
