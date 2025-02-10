from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session
import mysql.connector
from rembg import remove
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Configuration
DB_HOST = "mysql_db"
DB_USER = "root"
DB_PASSWORD = "password"
DB_NAME = "image_app"

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('upload_file'))
        else:
            flash('Invalid credentials, please try again!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request', 'danger')
            return redirect(request.url)

        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)

        try:
            input_image = Image.open(file.stream)
            output_image = remove(input_image, post_process_mask=True)
            img_io = BytesIO()
            output_image.save(img_io, 'PNG')
            img_io.seek(0)

            # Save Image to Database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO images (username, image) VALUES (%s, %s)", (session['username'], img_io.getvalue()))
            conn.commit()
            cursor.close()
            conn.close()

            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='image_rmbg.png')

        except UnidentifiedImageError:
            flash('Invalid image file. Please upload a valid image.', 'danger')
            return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
