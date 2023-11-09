from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import werkzeug
import os
import cv2
from image_processing import get_color_histogram, get_dominant_colors, get_color_moments

app = Flask(__name__)
api = Api(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ImageProcessing(Resource):
    def post(self):
        if 'image' not in request.files:
            return {'error': 'No image provided'}, 400

        file = request.files['image']
        
        if file.filename == '':
            return {'error': 'No image provided'}, 400
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            
            # Read the image only once
            image = cv2.imread(file_path)
            
            histogram = get_color_histogram(image)
            dominant_colors = get_dominant_colors(image)
            color_moments = get_color_moments(image)
            
            os.remove(file_path)
            
            return {
                'histogram': histogram, 
                'dominant_colors': dominant_colors,
                'color_moments': color_moments
            }, 200

        return {'error': 'Invalid file format'}, 400

api.add_resource(ImageProcessing, '/process_image')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
