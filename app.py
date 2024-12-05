from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import time
import uuid
import threading

# Initialize Flask
app = Flask(__name__)

# Load classification model
model = tf.keras.models.load_model('static/model/model_bs64_lr1e-05.h5')

# Classification labels
labels = ['Healthy', 'Rotten']

# Create 'uploads' folder if it doesn't exist
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Preprocess image function
def preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB')  # Convert image to RGB
    img = img.resize((299, 299))  # Resize according to model input
    img_array = np.array(img) / 255.0  # Normalize pixels to 0-1
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array


# Function to delete the uploaded image after a delay (600 seconds = 10 minutes)
def delete_file_after_delay(filepath, delay=600):  # 600 seconds = 10 minutes
    time.sleep(delay)  # Wait for the specified delay (in seconds)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"File {filepath} has been deleted after {delay} seconds.")


# API route to handle image upload and prediction
@app.route("/api/predict", methods=["POST"])
def predict():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Generate a unique filename
    original_filename = secure_filename(file.filename)
    file_ext = os.path.splitext(original_filename)[1]  # Get file extension
    unique_filename = f"{int(time.time())}{uuid.uuid4().hex[:8]}{file_ext}"  # Add timestamp + UUID

    # Save the uploaded image
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)

    try:
        # Preprocess image and make prediction
        img_array = preprocess_image(filepath)
        predictions = model.predict(img_array)
        predicted_class_idx = np.argmax(predictions)

        # Convert confidence to percentage and ensure it's a standard float
        confidence = float(predictions[0][predicted_class_idx]) * 100
        predicted_class = labels[predicted_class_idx]

        # Prepare JSON response
        response = {
            "prediction": predicted_class,
            "confidence": confidence,
            "image_url": f"/api/uploads/{unique_filename}"  # Optional if needed
        }

        # Start a new thread to delete the file after 600 seconds (10 minutes)
        threading.Thread(target=delete_file_after_delay, args=(filepath, 600)).start()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Return prediction result
    return jsonify(response)


# Route to serve uploaded images
@app.route("/api/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# Route to render the main template
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# Run the server
if __name__ == '__main__':
    app.run(debug=True)
