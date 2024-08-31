from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_session import Session
import mysql.connector
import hashlib
from PIL import Image
import io
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import base64

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '7252'
MYSQL_DB = 'login'

##Load the model
model=tf.keras.models.load_model('trained.keras')
class_names=['Aloevera','Amla','Amruthaballi','Arali','Astma_weed','Badipala','Balloon_Vine','Bamboo','Beans','Betel','Bhrami','Bringaraja','Caricature','Castor','Catharanthus','Chakte','Chilly','Citron lime (herelikai)','Coffee','Common rue(naagdalli)','Coriender','Curry','Doddpathre','Drumstick','Ekka','Eucalyptus','Ganigale','Ganike','Gasagase','Ginger','Globe Amarnath','Guava','Henna','Hibiscus','Honge','Insulin','Jackfruit','Jasmine','Kambajala','Kasambruga','Kohlrabi','Lantana','Lemon','Lemongrass','Malabar_Nut','Malabar_Spinach','Mango','Marigold','Mint','Neem','Nelavembu','Nerale','Nooni','Onion','Padri','Palak(Spinach)','Papaya','Parijatha','Pea','Pepper','Pomoegranate','Pumpkin','Raddish','Rose','Sampige','Sapota','Seethaashoka','Seethapala','Spinach1','Tamarind','Taro','Tecoma','Thumbe','Tomato','Tulsi','Turmeric','ashoka','camphor','kamakasturi','kepala']
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    message = session.pop('message', None)
    return render_template("login.html", message=message)


@app.route("/home")
def home():
    return render_template('home.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM details WHERE username=%s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('register.html', message='Username already exists. Please choose a different one.')
        else:
            cursor.execute('INSERT INTO details (username, password) VALUES (%s, %s)', (username, hashed_password))
            db.commit()
            return render_template('register.html', message="Registration successful!")
        
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT password FROM details WHERE username=%s', (username,))
    result = cursor.fetchone()

    if result and result[0] == hashed_password:
        return redirect(url_for('success'))
    else:
        session['message'] = 'Invalid username or password'
        return redirect(url_for('index'))

@app.route('/success')
def success():
    return redirect(url_for('home'))

@app.route('/predict',methods=['GET','POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            img = Image.open(io.BytesIO(file.read()))
            result = process_image(img)
            img_str = img_to_base64(img)
            return render_template('result.html', result=result, image=img_str)
    return render_template('predict.html')



def process_image(img):
    img_array=tf.keras.preprocessing.image.img_to_array(img)
    img_array=tf.image.resize(img_array,[128,128])
    input_arr=np.expand_dims(img_array,axis=0)
    prediction=model.predict(input_arr)
    result_index=np.argmax(prediction)
    model_prediction=class_names[result_index]
    return model_prediction

def allowed_file(filename):
    allow={'png','jpg','jpeg','gif','avif'}
    return '.' in filename and filename.rsplit('.',1)[1].lower() in allow

def img_to_base64(img):
    imgio=io.BytesIO()
    img.save(imgio,'JPEG')
    img_str="data:image/jpeg;base64," + base64.b64encode(imgio.getvalue()).decode()
    return img_str


if __name__ == '__main__':
    app.run(debug=True)
