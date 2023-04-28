from flask import Flask, render_template, request, url_for, redirect
from dotenv import load_dotenv
load_dotenv()
import os
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='hotell',
                            user=os.getenv('DB_USERNAME'),
                            password=os.getenv('DB_PASSWORD'))
    return conn
def get_db_connection1(username,password):
    conn = psycopg2.connect(host='localhost',
                            database='hotell',
                            user=username,
                            password=password)
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    # cur.execute('SELECT * FROM books;')
    # books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html')
# ...

@app.route('/receptionist/', methods=('GET', 'POST'))
def receptionist():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection1(username,password)
            # render_template('recepage.html');
            print("hellllo")
            return redirect(url_for('recepage'))
        except:
            return render_template('receptionist.html')

    return render_template('receptionist.html')

@app.route('/recepage/')
def recepage():
    print("hello")
    return render_template('recepage.html')