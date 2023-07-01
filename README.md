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
As mentioned above, the first step is training in YOLOv7. The trained weight (eg. 'best.py') then is saved in the directory of Flask app: 'app/controller/weights'. <br/>
From YOLOv7 directory, run export.py as below:

``` shell
python export.py --weights best.pt --grid --end2end --simplify --topk-all 100 --iou-thres 0.65 --conf-thres 0.35 --img-size 640 640 --max-wh 640
```

## Load and Run detection by ONNX Model

``` shell
# Load and Check
cuda = torch.cuda.is_available()
providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']

onnx_model = onnx.load(weights)
onnx.checker.check_model(onnx_model)
```

``` shell
# Detect
ort_session = ort.InferenceSession(weights, providers=providers)

outname = [i.name for i in ort_session.get_outputs()]
inname = [i.name for i in ort_session.get_inputs()]

inp = {inname[0]: ifer_image}

# ONNX inference
outputs = ort_session.run(outname, inp)[0]
```




