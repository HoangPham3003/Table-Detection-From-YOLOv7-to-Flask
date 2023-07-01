from app import app

import os
import time
import cv2
import json
import numpy as np

from werkzeug.utils import secure_filename
from flask import request, render_template, url_for, jsonify, redirect, session

from datetime import datetime

from PIL import Image

from app.controller.detect import detect


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/favicon.ico")
def favicon():
    return "", 200


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            fileName = secure_filename(file.filename)
            file_name, file_extension = fileName.split('.')

            now = datetime.now()
            dt_string = now.strftime("__%d_%m_%Y_%H_%M_%S")
            
            fileName = file_name + dt_string + '.' + file_extension

            upload_image_path = os.path.join(app.config['UPLOAD_FOLDER'], fileName)

            file.save(upload_image_path)

            image_name = detect(upload_image_path)

            data = {}
            data['image_name'] = image_name

            return jsonify(data=data)


    return render_template('home.html')