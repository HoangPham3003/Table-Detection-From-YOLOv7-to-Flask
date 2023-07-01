from flask import Flask
import os

app = Flask(__name__)

UPLOAD_FOLDER = './app/static/img_Uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['WEIGHTS'] = './app/controller/weights/best.onnx'

SAVE_FOLDER = './app/static/img_Detect'
if not os.path.exists(SAVE_FOLDER):
    os.mkdir(SAVE_FOLDER)
app.config['SAVE_FOLDER'] = SAVE_FOLDER

from app.controller import routes
from app.controller import detect