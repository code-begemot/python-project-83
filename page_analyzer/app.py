from flask import Flask, render_template
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

conn = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

@app.route('/')
def index():
    return render_template('index.html')
