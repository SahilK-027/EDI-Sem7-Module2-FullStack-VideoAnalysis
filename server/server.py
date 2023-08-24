from ultralytics import YOLO
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import time
import math
import json


app = Flask(__name__)
CORS(app)

# Define class names
class_names = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
             'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
             'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase',
             'ring', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
             'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
             'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
             'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
             'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
             'teddy bear', 'hair drier', 'toothbrush' ]

@app.route("/analyze", methods=['POST', 'GET'])
def analysis():
    video_file = request.files['video']
    if not video_file:
        return ({'error': 'No video file provided'}), 400

    # Save the video file to a temporary location
    path = 'uploads/video.mp4'
    video_file.save(path)
    
    # Run YOLOv8 Model
    # Load YOLOv5 model
    model = YOLO('yolov8n.pt')
    video_path = "uploads/video.mp4"
    cap = cv2.VideoCapture(video_path)
    detection_results = []
    initial_timestamp = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        start_time = time.time()
        
        # Perform person detection
        results = model(frame)

        # Perform person detection
        detections = []
        
        for i in results:
            boundingBoxes = i.boxes
            for box in boundingBoxes:
                confidence = math.ceil(box.conf[0] * 100) / 100
                classIdx = int(box.cls[0])
                currentClass = class_names[classIdx]
                if currentClass == 'person' and confidence > 0.8:
                    current_timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                    if(initial_timestamp == 0):
                        detections.append({
                            "class": currentClass,
                            "confidence": confidence,
                            "timestamp": current_timestamp
                        })
                        detection_results.append(detections)
                        initial_timestamp = current_timestamp
                    else :    
                        delta_time = current_timestamp - initial_timestamp
                        if(delta_time > 1):
                            detections.append({
                                "class": currentClass,
                                "confidence": confidence,
                                "timestamp": current_timestamp
                            })
                            detection_results.append(detections)
                            initial_timestamp = current_timestamp

    cap.release()
    cv2.destroyAllWindows()
    
    return (detection_results)



if __name__ == "__main__":
    app.run(debug=True)