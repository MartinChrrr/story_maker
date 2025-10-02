import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import render_template

UPLOAD_FOLDER = "./static/uploaded_images/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
IMAGE_FOLDER = "./static/uploaded_images/"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    IMG_LIST = os.listdir("static/uploaded_images")
    IMG_LIST = ["uploaded_images/" + i for i in IMG_LIST]
    imagelist=IMG_LIST
    return render_template("gallery.html", imagelist=IMG_LIST)

@app.route("/new_character", methods=['GET', 'POST'])
def new_character():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'Image uploaded successfully!'
    return render_template("new_character.html")



