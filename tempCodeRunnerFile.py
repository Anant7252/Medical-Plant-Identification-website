from flask import Flask, render_template, request,redirect,url_for ,g
import mysql.connector
import hashlib
import io
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import base64

app=Flask(__name__)


MYSQL_HOST='127.0.0.1'
MYSQL_USER='root'
MYSQL_PASSWORD='72520000'
MYSQL_DB='login'

def get_db():
    db=getattr(g,'_database',None)
    if db is None:
        db = g._database = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
    return db

model =tf.keras.models.load_model("trained_model.keras")
class_names=['Aloevera','Amla','Amruthaballi','Arali','Astma_weed','Badipala','Balloon_Vine','Bamboo','Beans','Betel','Bhrami','Bringaraja','Caricature','Castor','Catharanthus','Chakte','Chilly','Citron lime (herelikai)','Coffee','Common rue(naagdalli)','Coriender','Curry','Doddpathre','Drumstick','Ekka','Eucalyptus','Ganigale','Ganike','Gasagase','Ginger','Globe Amarnath','Guava','Henna','Hibiscus','Honge','Insulin','Jackfruit','Jasmine','Kambajala','Kasambruga','Kohlrabi','Lantana','Lemon','Lemongrass','Malabar_Nut','Malabar_Spinach','Mango','Marigold','Mint','Neem','Nelavembu','Nerale','Nooni','Onion','Padri','Palak(Spinach)','Papaya','Parijatha','Pea','Pepper','Pomoegranate','Pumpkin','Raddish','Rose','Sampige','Sapota','Seethaashoka','Seethapala','Spinach1','Tamarind','Taro','Tecoma','Thumbe','Tomato','Tulsi','Turmeric','ashoka','camphor','kamakasturi','kepala']


@app.teardown_appcontext
def close_connection(exception):
    db=getattr(g,'_database',None)
    if db is not None :
        db.close()

@app.route("/")
def index():
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        cursor = db.cursor()

        # Check if username already exists or not
        cursor.execute('SELECT * FROM details WHERE username=%s', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('register.html', message='Username already exists. Please choose a different one.')
        else:
            # If the username doesn't exist, insert the new user into the database
            cursor.execute('INSERT INTO details (username, password) VALUES (%s, %s)', (username, hashed_password))
            db.commit()
            return render_template('register.html', message="Registration successful!")
        
    return render_template('register.html')


@app.route('/login',methods=['POST'])
def login():
    username=request.form['username']
    password=request.form['password']
    hashed_password=hashlib.sha256(password.encode()).hexdigest()

    db=get_db()
    cursor=db.cursor()
    cursor.execute('SELECT password From details WHERE username=%s',(username,))
    result=cursor.fetchone()

    if result and result[0]==hashed_password:
        return redirect(url_for('success'))
    else:
        return redirect(url_for('fail'))
    
@app.route('/success')
def success():
    return 'Login Successful'

@app.route('/fail')
def fail():
    return render_template('login.html' ,message='Invalid User name or password')

if __name__ =='__main__':
    app.run(debug=True)