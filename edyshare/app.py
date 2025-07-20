from flask import Flask, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
import os
import sqlite3

# ──────────────── SETUP ────────────────
app = Flask(__name__)
app.secret_key = 'supersecret'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ──────────────── DATABASE ────────────────
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    uploader TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ──────────────── ROUTES ────────────────

@app.route('/')
def index():
    return jsonify({"message": "Welcome to EduShare Backend!"})

# Register User
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"message": "Registration successful"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409
    finally:
        conn.close()

# Login User
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()

    if user:
        session['user'] = username
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify({"message": "Logged out"})

# Upload Resource
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    title = request.form['title']
    subject = request.form['subject']
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conn = get_db()
        conn.execute("INSERT INTO resources (title, subject, filename, uploader) VALUES (?, ?, ?, ?)",
                     (title, subject, filename, session['user']))
        conn.commit()
        conn.close()
        return jsonify({"message": "File uploaded successfully"})
    else:
        return jsonify({"error": "No file provided"}), 400

# List All Resources
@app.route('/resources', methods=['GET'])
def resources():
    conn = get_db()
    res = conn.execute("SELECT * FROM resources").fetchall()
    conn.close()
    return jsonify([dict(row) for row in res])

# Download Resource
@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ──────────────── MAIN ────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
