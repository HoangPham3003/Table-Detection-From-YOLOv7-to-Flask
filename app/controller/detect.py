from app import app

import os
import numpy as np

from PIL import Image

import cv2
import torch
from numpy import random

import onnx
import onnxruntime as ort


img_formats = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']
# Get names and colors
names = ['table']
colors = {name:[255, 0, 0] for i, name in enumerate(names)}


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, r, (dw, dh)


def preprocessing(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    image = img.copy()
    image, ratio, dwdh = letterbox(image, auto=False)
    image = image.transpose((2, 0, 1))
    image = np.expand_dims(image, 0)
    image = np.ascontiguousarray(image)

    new_img = image.astype(np.float32)
    new_img /= 255

    return img, new_img, ratio, dwdh


def xyxy2xywh(box, img_h, img_w):
    x_min, y_min, x_max, y_max = box
    dw = 1./img_w
    dh = 1./img_h
    x_center = (x_min + x_max)/2.0
    y_center = (y_min + y_max)/2.0
    w_box = x_max - x_min
    h_box = y_max - y_min
    x_center = x_center * dw
    w_box = w_box * dw
    y_center = y_center * dh
    h_box = h_box * dh
    return (x_center, y_center, w_box, h_box)


def detect(image_path):
    weights = app.config['WEIGHTS']
    save_dir = app.config['SAVE_FOLDER']

    save_label_dir = os.path.join(save_dir, "labels")
    if not os.path.exists(save_label_dir):
        os.mkdir(save_label_dir)

    # Load model
    cuda = torch.cuda.is_available()
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']

    # Check model
    # onnx_model = onnx.load(weights)
    # onnx.checker.check_model(onnx_model)

    # ONNX runtime
    ort_session = ort.InferenceSession(weights, providers=providers)

    # Get image name
    image_name = image_path.split("\\")[-1]

    # Create annot file
    f = open(os.path.join(save_label_dir, image_name.split(".")[0] + ".txt"), 'a')

    img, new_img, ratio, dwdh = preprocessing(image_path)

    outname = [i.name for i in ort_session.get_outputs()]

    inname = [i.name for i in ort_session.get_inputs()]

    inp = {inname[0]:new_img}

    # ONNX inference
    outputs = ort_session.run(outname, inp)[0]

    ori_images = [img.copy()]
        
    for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
        image = ori_images[int(batch_id)]
        img_h, img_w, _ = image.shape
        box = np.array([x0, y0, x1, y1])
        box -= np.array(dwdh * 2)
        box /= ratio
        box = box.round().astype(np.int32).tolist()
        cls_id = int(cls_id)
        score = round(float(score), 3)
        name = names[cls_id]
        color = colors[name]
        name += ' ' + str(score)
        
        x_center, y_center, box_w, box_h = xyxy2xywh(box, img_h, img_w)
        f.write(f"{cls_id} {x_center} {y_center} {box_w} {box_h}\n")

        cv2.rectangle(image, box[:2], box[2:], color, 2)
        cv2.putText(image, name, (box[0], box[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, thickness=2)
    
    img_pil = Image.fromarray(ori_images[0])
    save_path = os.path.join(save_dir, image_name)
    img_pil.save(save_path)
    return image_name