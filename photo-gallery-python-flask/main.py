from flask import Flask
from flask import sessions
from flask import request
from flask import render_template, render_template_string
from flask import redirect, url_for
from werkzeug.utils import secure_filename
import json
import os
from modules.Login import Login
from modules.Gallery import Gallery
from modules.Photos import Photos
from definition import *
from modules.LoginDb import LoginDB  
from flask import Flask, request, session, json
from modules.GalleryDB import GalleryDB
import jsonify
import requests
from flask import redirect
from flask import jsonify
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import mpld3






app = Flask(__name__)
app.secret_key = 'testkey'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg','png'])
session = {}

'''
for int routes
@app.route('/<int:id>')
def func(id):
    print(id)
'''
photos_obj = Photos()


@app.route('/')
@app.route('/index')
def index():
    if 'type' in session:
        return redirect(url_for('galleries'))

    return render_template("index.html")


@app.route('/login', methods=['POST'])
def do_login():
    if request.method == "POST":
        user_name = request.form['username']
        password = request.form['password']

        login_db = LoginDB()
        result = login_db.login(user_name, password)

        if result['result']:
            session['type'] = result['type']
            session['user_id'] = result['user_id']
            response = {'success': True, 'type': result['type']}
        else:
            response = {'success': False}
        
        return json.dumps(response)


@app.route('/logout')
def do_logout():
    session.pop('type', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def do_register():
    if request.method == "POST":
        user_name = request.form['username']
        password = request.form['password']
        user_type = request.form.get('type', 'normal')  # default to 'normal' if not provided

        login_db = LoginDB()
        result = login_db.register(user_name, password, user_type)

        return json.dumps(result)
    
# -------------- Gallery Routes ----------------
@app.route('/galleries')
def galleries():
    if 'user_id' in session:  # check if the user is logged in
        user_id = session['user_id']
        gallery_db = GalleryDB()
        galleries = gallery_db.get_galleries(user_id)  # get galleries for the logged-in user
        return render_template("gallery.html", galleries=galleries, session=session)
    else:
        return redirect(url_for("index"))


@app.route('/galleries/add', methods=['POST'])
def add_galleries():
    if 'user_id' in session and request.method == "POST":
        user_id = session['user_id']
        gallery_name = request.form['galleryName']

        gallery_db = GalleryDB()
        result = gallery_db.create_gallery(user_id, gallery_name)

        response = {'success': result}
        return json.dumps(response)
    else:
        response = {'success': False}
        return json.dumps(response)


@app.route('/galleries/edit', methods=['POST'])
def edit_galleries():
    # Check if the user is authenticated and the request method is POST
    if 'user_id' in session and request.method == "POST":
        user_id = session['user_id']
        gallery_id = request.form['galleryId']  # Assuming the form data contains 'galleryId'
        new_gallery_name = request.form['newName']

        # Initialize the GalleryDB class
        gallery_db = GalleryDB()

        # Attempt to rename the gallery and capture the result
        success = gallery_db.rename_gallery(user_id, gallery_id, new_gallery_name)

        if success:
            response = {'success': True, 'message': 'Gallery renamed successfully.'}
        else:
            response = {'success': False, 'message': 'Failed to rename gallery. Please check the data and try again.'}
    else:
        # Handling for unauthorized access or bad request
        response = {'success': False, 'message': 'Not authorized or bad request.'}

    # Sending a JSON response
    return json.dumps(response)



@app.route('/galleries/delete', methods=['POST'])
def delete_galleries():
    if 'user_id' in session and request.method == "POST":
        user_id = session['user_id']
        gallery_id = request.form['galleryId']  # this should be the unique identifier for the gallery

        gallery_db = GalleryDB()
        result = gallery_db.delete_gallery(user_id, gallery_id)

        response = {'success': result}
        return json.dumps(response)
    else:
        response = {'success': False}
        return json.dumps(response)

# -------------- Gallery Routes ----------------


# -------------- Gallery Photos Routes ----------------
@app.route('/galleries/album/<gallery_name>', methods=['GET'])
def gallery(gallery_name):
    if 'type' in session:
        user_id = session['user_id']
        photos_obj = Photos()
        photos = photos_obj.get_all_gallery_photos(user_id, gallery_name)
        full_image_path = f"/static/Galleries/{user_id}/{gallery_name}/"
        
        # Check if result files exist for each photo
        photo_data = []
        for photo in photos:
            photo_path = os.path.join(photos_obj.get_gallery_path(user_id, gallery_name), photo)
            result_path = f"{photo_path}_results.json"
            photo_data.append({
                'name': photo,
                'calculated': os.path.isfile(result_path)  # Check if the results file exists
            })
        
        return render_template("photos.html", photos=photo_data, full_image_path=full_image_path, gallery_name=gallery_name, session=session)
    else:
        return redirect(url_for("index"))



@app.route('/galleries/album/photos/delete', methods=['POST'])
def delete_gallery_photo():
    try:
        gallery_name = request.form['galleryName']
        photo_name = request.form['photoName']
        user_id = session['user_id']  # or however you're getting the user_id

        photos_obj = Photos()
        result = photos_obj.delete_gallery_photo(user_id, gallery_name, photo_name)

        # Also delete the corresponding JSON file
        json_file_path = os.path.join(photos_obj.get_gallery_path(user_id, gallery_name), f"{photo_name}_results.json")
        if os.path.isfile(json_file_path):
            os.remove(json_file_path)

        response = {'success': result}
        return json.dumps(response)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify(success=False, error=str(e)), 500




@app.route('/galleries/album/<gallery_name>/upload', methods=['GET','POST'])
def upload_gallery_photo(gallery_name):
    if 'user_id' in session:  # Ensure the user is logged in
        user_id = session['user_id']  # Retrieve user_id from the session

        photos_obj = Photos()
        gallery_path = photos_obj.get_gallery_path(user_id, gallery_name)  # Get the correct path
        app.config['UPLOAD_FOLDER'] = gallery_path

        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(url_for('gallery', gallery_name=gallery_name))
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                msg = 'No selected file'
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                # Verify if the upload directory exists, if not create it
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('gallery', gallery_name=gallery_name))
            



@app.route('/galleries/album/<gallery_name>/calculate/<photo_name>', methods=['POST'])
def calculate_image_properties(gallery_name, photo_name):
    user_id = session['user_id'] 
    photos_obj = Photos()
    gallery_path = photos_obj.get_gallery_path(user_id, gallery_name)
    
    # File path to the image
    image_path = os.path.join(gallery_path, photo_name)
    print("Photo name received for calculation:", photo_name)

    # Endpoint to your Image Processing API
    API_URL = "http://127.0.0.1:5001/process_image"
    
    # Check if the result file already exists
    result_path = os.path.join(gallery_path, f"{photo_name}_results.json")
    if not os.path.exists(result_path):
        with open(image_path, 'rb') as f:
            response = requests.post(API_URL, files={'image': f})
        if response.status_code == 200:
            data = response.json()
            with open(result_path, 'w') as result_file:
                json.dump(data, result_file)
        else:
            return jsonify(success=False, message="Error in calculation")
    
    return jsonify(success=True, message="Calculation complete or already exists")


@app.route('/galleries/album/<gallery_name>/view_calculation/<photo_name>', methods=['GET'])
def view_image_properties(gallery_name, photo_name):
    user_id = session['user_id'] 
    photos_obj = Photos()
    gallery_path = photos_obj.get_gallery_path(user_id, gallery_name)
    
    result_path = os.path.join(gallery_path, f"{photo_name}_results.json")
    if os.path.exists(result_path):
        with open(result_path, 'r') as result_file:
            data = json.load(result_file)
        # Color Moments Plot
        labels = list(data['color_moments'].keys())
        mean_values = [data['color_moments'][ch]['mean'] for ch in labels]
        skewness_values = [data['color_moments'][ch]['skewness'] for ch in labels]
        std_dev_values = [data['color_moments'][ch]['std_dev'] for ch in labels]

        fig, ax = plt.subplots()
        ax.bar(labels, mean_values, label='Mean')
        ax.bar(labels, skewness_values, label='Skewness', bottom=mean_values)
        ax.bar(labels, std_dev_values, label='Std Dev', bottom=skewness_values)

        ax.set_ylabel('Scores')
        ax.set_title('Color Moments')
        ax.legend()

        color_moments_plot = mpld3.fig_to_html(fig)
        plt.close(fig)
        

        # Combined Histograms Plot
        histograms = data['histogram']
        fig_combined_histogram, ax = plt.subplots(figsize=(5, 5))
        colors = ['red', 'green', 'blue']
        for color in colors:
            ax.bar(range(256), histograms[color], color=color, alpha=0.5, label=f'{color.capitalize()} Channel')
        ax.set_title('Combined Histogram')
        ax.set_xlim([0, 256])
        ax.legend()
        plt.tight_layout()
        combined_histograms_plot = mpld3.fig_to_html(fig_combined_histogram)
        plt.close(fig_combined_histogram)


        # Dominant Colors
        dominant_colors = data['dominant_colors']

        return jsonify(
            success=True,
            content={
                # Assuming you have created the plots and saved them as HTML strings
                "color_moments_plot": color_moments_plot,
                "histograms_plot": combined_histograms_plot,
                "dominant_colors": dominant_colors,
            }
        )
    else:
        return jsonify(success=False, message="No calculation results found")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# -------------- Gallery Photos Routes ----------------


if __name__  == "__main__":
    app.run(debug=True)




