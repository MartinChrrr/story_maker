import os
import base64
from flask import Flask, flash, request, redirect, url_for,render_template
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import hashlib
from werkzeug.utils import secure_filename
import llm as l
import json

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
    description = db.Column(db.TEXT, unique=True, nullable=True)
    one_line = db.Column(db.TEXT, unique=True, nullable=True)
    title = db.Column(db.TEXT, unique=True, nullable=True)
    



def get_md5_from_file(file):  
    file.seek(0)
    file_content = file.read()
    file.seek(0)
    return hashlib.md5(file_content).hexdigest(), file_content


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_hash(img_path):
    with open(img_path, "rb") as f:
        img_hash = hashlib.md5()
        while chunk := f.read(8192): #random number
           img_hash.update(chunk)
    return img_hash.hexdigest()

def get_json_from_response(r):
    clean_r = r.strip().strip('`')
    if clean_r.startswith("json"):
        clean_r = clean_r[4:]  # remove json
    clean_r = clean_r.strip("`\n ")

    # Find just json
    start = clean_r.find('{')
    end = clean_r.rfind('}') + 1
    json_part = clean_r[start:end]

    # Parse proprement
    data = json.loads(json_part)

    return data

#routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gallery")
def gallery():
    images = Image.query.all()
    img_list = []
    descriptions = []
    for img in images:
        dir = "uploaded_images/"
        string = dir + img.filename
        img.filename = string
    return render_template("gallery.html", images=images)

@app.route("/new_character", methods=['GET', 'POST'])
def new_character():
    if request.method == 'POST':
        if 'user_image' not in request.files:
            app.logger.info(request.files["user_image"])
            return 'No file part'
        file = request.files['user_image']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Get hash
            img_hash, file_content = get_md5_from_file(file)
            
            # Check if hash match in database
            if Image.query.filter_by(hash=img_hash).first():
                return "Cette image existe déjà dans la base."
            
            
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            #Loading part
            return redirect(url_for('loading', filename=filename))
            #redirect(url_for("loading", filename=filename))

            #llm part
            # response_llm = l.get_image_description(path)
            # response = get_json_from_response(response_llm)
            # title = response["title"]
            # desc = response["text"]
            # one_line = response["one_line"]
            # # Save in database part
            # new_img = Image(filename=filename, data=file_content, hash=img_hash, description=desc, title = title, one_line = one_line)
            # db.session.add(new_img)
            # db.session.commit()
            # #redirection to story
            # redirect(url_for('/story', image_id=new_img.id))

    return render_template("new_character.html")
            
@app.route("/loading")
def loading():
    #loading template html during request
    filename = request.args.get('filename')
    return render_template("loading.html", filename=filename)

@app.route("/process_image/<filename>")
def process_image(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #llm part
    app.logger.info("[process_image] llm")
    response_llm = l.get_image_description(path)
    app.logger.info("[process_image] response llm")
    response = get_json_from_response(response_llm)
    app.logger.info("[process_image] response json")
    title = response["title"]
    desc = response["text"]
    one_line = response["one_line"]
    # Save in database part
    # Get hash
    with open(path, "rb") as f:
        file_content = f.read()
    img_hash, _ = get_md5_from_file(open(path, "rb"))
    new_img = Image(filename=filename, data=file_content, hash=img_hash, description=desc, title = title, one_line = one_line)
    db.session.add(new_img)
    db.session.commit()
    #redirection to story
    return redirect(url_for('story', id=new_img.id))



@app.route("/test")
def test():
    try:
        result = db.engine.execute('SELECT 1')
        return "Connexion à la base de données réussie!"
    except Exception as e:
        return f"Erreur de connexion à la base : {str(e)}"
    
@app.route('/story', methods=['GET'])
def story():
    image_id = request.args.get('id')
    
    if image_id is None:
        return None
    image = Image.query.get(image_id)
    if image is None:
        return None
    DIR = "uploaded_images/"
    path = DIR + image.filename
    image.filename = path
    return render_template("story.html", image = image)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")


