# Flask app detect table using ONNX model exported from YOLOv7

In this repository, I introduce how to convert from trained weight to onnx model and use it for my own custom app without depending on any module of Yolo.

## Yolov7
To start, training in YOLOv7 is the first step. Follow: https://github.com/WongKinYiu/yolov7

## Dataset
ICDAR 2019: https://github.com/cndplab-founder/ICDAR2019_cTDaR

## Demo
![infer_result](plot_git/infer_result.png)

## Requirements
- Python 3
- Opencv-python
- Pillow
- Flask
- ONNX
- ONNX Runtime 

## Export ONNX Model
As mentioned above, the first step is training in YOLOv7. <br>
From YOLOv7 directory, run export.py as below:

``` shell
python export.py --weights best.pt --grid --end2end --simplify --topk-all 100 --iou-thres 0.65 --conf-thres 0.35 --img-size 640 640 --max-wh 640
```

The converted weight (eg. 'best.onnx') then is saved in the directory of Flask app: 'app/controller/weights'. <br/>

## Load and Run detection by ONNX Model

``` shell
# Load and Check
cuda = torch.cuda.is_available()
providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']

onnx_model = onnx.load(weights)
onnx.checker.check_model(onnx_model)
```

``` shell
weights = "best.onnx"
# Start ONNX Runtime session
ort_session = ort.InferenceSession(weights, providers=providers)

outname = [i.name for i in ort_session.get_outputs()]
inname = [i.name for i in ort_session.get_inputs()]

inp = {inname[0]: infer_image}

# ONNX inference
outputs = ort_session.run(outname, inp)[0]
```

## Inference
The inference phase and showing results are shown in code: [detect.py](https://github.com/HoangPham3003/Table-Detection-From-YOLOv7-to-Flask/blob/main/app/controller/detect.py)

## Reference
- A simple guild can be found here: [YOLOv7ONNXandTRT.ipynb](https://colab.research.google.com/github/WongKinYiu/yolov7/blob/main/tools/YOLOv7onnx.ipynb#scrollTo=yfZALjuo-_Md) 



