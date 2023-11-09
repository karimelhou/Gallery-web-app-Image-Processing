from GalleryDB import GalleryDB

def test_Gallery_db():
    print("Starting tests...")

    # Initialize the GalleryDB
    gallery_db = GalleryDB()

    # 1. Test the gallery creation
    user_id = 4  # Example user ID
    gallery_name = "gallery 4"
    success = gallery_db.create_gallery(user_id, gallery_name)
    assert success, f"Failed to create gallery: {gallery_name}"
    print(f"Gallery created: {gallery_name}")

    
    # 2. Test fetching galleries
    galleries = gallery_db.get_galleries(user_id)
    assert galleries, "Failed to fetch galleries"
    #print(f"Fetched galleries: {galleries}")

    # You should validate that the created gallery is in the fetched galleries here

    

    # #  3. Test gallery renaming
    # new_gallery_name = "Renamed tt1"
    # # Assuming gallery_id is the ID of the previously created gallery
    # gallery_id = galleries[-1]['id']  
    # success = gallery_db.rename_gallery(user_id, gallery_id, new_gallery_name)
    # assert success, "Failed to rename gallery"
    # print(f"Gallery renamed to: {new_gallery_name}")

    # # 4. Test gallery deletion

    # success = gallery_db.delete_gallery(user_id, gallery_id)
    # assert success, "Failed to delete gallery"
    # print("Gallery deleted")

    # print("All tests passed successfully!")

if __name__ == "__main__":
    test_Gallery_db()
