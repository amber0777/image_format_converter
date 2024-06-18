# from flask import Flask, request,render_template, redirect,session
# from flask_sqlalchemy import SQLAlchemy
# import bcrypt

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db = SQLAlchemy(app)
# app.secret_key = 'secret_key'

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))

#     def __init__(self,email,password,name):
#         self.name = name
#         self.email = email
#         self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
#     def check_password(self,password):
#         return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

# with app.app_context():
#     db.create_all()


# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/register',methods=['GET','POST'])
# def register():
#     if request.method == 'POST':
#         # handle request
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']

#         new_user = User(name=name,email=email,password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect('/login')



#     return render_template('register.html')

# @app.route('/login',methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = User.query.filter_by(email=email).first()
        
#         if user and user.check_password(password):
#             session['email'] = user.email
#             return redirect('/dashboard')
#         else:
#             return render_template('login.html',error='Invalid user')

#     return render_template('login.html')


# @app.route('/dashboard')
# def dashboard():
#     if session['email']:
#         user = User.query.filter_by(email=session['email']).first()
#         return render_template('dashboard.html',user=user)
    
#     return redirect('/login')

# @app.route('/logout')
# def logout():
#     session.pop('email',None)
#     return redirect('/login')

# if __name__ == '__main__':
#     app.run(debug=True)




from flask import Flask, request, render_template, redirect, session,flash,url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import cv2 
from werkzeug.utils import secure_filename
import os
import bcrypt

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL configurations
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3306 
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'image_recog_app'

mysql = MySQL(app)

# Initialize database (create 'users' table if not exists)
with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100) NOT NULL
        )
    """)
    mysql.connection.commit()
    cur.close()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"{app.config['UPLOAD_FOLDER']}/{filename}")
    match operation:
        case "cgray":
            imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            cv2.imwrite(newFilename, imgProcessed)
            return newFilename
        case "cwebp": 
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpg": 
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng": 
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename

@app.route('/')
def index():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/contact')
def contact():
    contact_info = {
        'phone': '123-456-7890',
        'email': 'contact@example.com'
    }
    return render_template('contact.html', contact_info=contact_info)

@app.route('/documentation')
def documentation():
    contact_info = {
        'phone': '123-456-7890',
        'email': 'contact@example.com'
    }
    return render_template('documentation.html', contact_info=contact_info)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['email'] = user[2]  # store email in session
            return redirect('/index')
        else:
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/index')
def index_page():
    if 'email' in session:
        return render_template('index.html')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST": 
        operation = request.form.get("operation")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return render_template("error.html")
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            # Render index.html again with updated context
            return render_template("index.html")

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)

