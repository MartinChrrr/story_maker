import os
import base64
from flask import Flask, flash, request, redirect, url_for,render_template
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import hashlib
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "./static/uploaded_images/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
IMAGE_FOLDER = "./static/uploaded_images/"


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

database_url = "postgresql://martin:test@db:5432/mydatabase"
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(80), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    hash = db.Column(db.String(32), unique=True, nullable=False)  



def get_md5_from_file(file):
    # file doit être un objet de type FileStorage de Flask
    file.seek(0)
    file_content = file.read()
    file.seek(0)
    return hashlib.md5(file_content).hexdigest(), file_content


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_hash(img_path):
    # This function will return the `md5` checksum for any input image.
    with open(img_path, "rb") as f:
        img_hash = hashlib.md5()
        while chunk := f.read(8192):
           img_hash.update(chunk)
    return img_hash.hexdigest()

#routes
@app.route("/")
def index():
    return render_template("index.html")

#local
# @app.route("/gallery")
# def gallery():
    # IMG_LIST = os.listdir("static/uploaded_images")
    # IMG_LIST = ["uploaded_images/" + i for i in IMG_LIST]
    # imagelist=IMG_LIST
    # return render_template("gallery.html", imagelist=IMG_LIST)

@app.route("/gallery")
def gallery():
    images = Image.query.all()
    img_list = []
    for img in images:
        dir = "uploaded_images/"
        string = dir + img.filename
        img_list.append(string)
    return render_template("gallery.html", imagelist=img_list)

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
            # Hash et obtention du contenu binaire
            img_hash, file_content = get_md5_from_file(file)
            
            # Vérification existence dans la base
            if Image.query.filter_by(hash=img_hash).first():
                return "Cette image existe déjà dans la base."
            
            # Enregistrement dans la base
            new_img = Image(filename=filename, data=file_content, hash=img_hash)
            db.session.add(new_img)
            db.session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template("new_character.html")
            
 
@app.route("/test")
def test():
    try:
        result = db.engine.execute('SELECT 1')
        return "Connexion à la base de données réussie!"
    except Exception as e:
        return f"Erreur de connexion à la base : {str(e)}"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")


