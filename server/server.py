from ultralytics import YOLO
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
import cv2
import time
import math
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") 
CORS(app, resources={r"/socket.io/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
@cross_origin()
def helloWorld():
  return "Hello, cross-origin-world!"
 # Adjust origins for production

@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Analysis started'})

def send_progress(progress):
    socketio.emit('progress', {'message': progress})

def send_results(results):
    socketio.emit('results', {'data': results})

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

stop_processing = False  # Flag to indicate whether processing should stop

@app.route("/stop", methods=['GET'])
def stop_analysis():
    global stop_processing 
    stop_processing = True
    return ({"message": "Processing stopped"}), 400

@app.route("/analyze", methods=['POST', 'GET'])
def analysis():
    global stop_processing 
    if(stop_processing == True):
        stop_processing = False
        
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
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames in the video
    frames_per_second = cap.get(cv2.CAP_PROP_FPS)
    current_frame = 0
    processing_time_sum = 0
    processed_frames = 0
    
    while cap.isOpened() and not stop_processing:
        ret, frame = cap.read()
        if not ret:
            break
        if stop_processing:
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
                        if(delta_time > 3):
                            detections.append({
                                "class": currentClass,
                                "confidence": confidence,
                                "timestamp": current_timestamp
                            })
                            detection_results.append(detections)
                            initial_timestamp = current_timestamp
                            
        end_time = time.time()
        # Processing current frame
        current_frame += 1
        # Calculate percentage progress completed 
        progress = calculate_progress(current_frame, frame_count)
        # Estimate remaining time
        
        processing_time = end_time - start_time
        processing_time_sum += processing_time
        remaining_frames = frame_count - current_frame
        
                # Calculate average processing time per frame
        avg_processing_time = processing_time_sum / current_frame
        
        estimated_remaining_time = calculate_remaining_time(remaining_frames,  avg_processing_time)
        
        # Backend logs
        log_data = {
            'progress': progress,
            'estimated_remaining_time': estimated_remaining_time
            # Add more relevant information here
        }
        socketio.emit('progress_update', log_data)

    cap.release()
    cv2.destroyAllWindows()
    
    return (detection_results)

def calculate_progress(current_frame, total_frames):
    return (current_frame / total_frames) * 100

def calculate_remaining_time(remaining_frames, avg_processing_time):
    if avg_processing_time == 0:
        return "N/A"  # Avoid division by zero

    seconds_remaining = remaining_frames * avg_processing_time
    minutes = int(seconds_remaining // 60)
    seconds = int(seconds_remaining % 60)
    return f"{minutes} min {seconds} sec"

if __name__ == "__main__":
    app.run(debug=True)