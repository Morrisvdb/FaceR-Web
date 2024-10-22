import cv2
import numpy as np
import os
import datetime
import uuid
from ultralytics import YOLO, solutions
import time
import torch
import torchvision
import requests


def load_yolo_model(model_path, model_url=None):
    if not os.path.exists(model_path):
        print(FileNotFoundError(f"Model file not found: {model_path}; Downloading from {model_url}"))
        model = requests.get(model_url)
    model = YOLO(model_path)
    return model

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# device = torch.device('cpu')

print(f"Using device: {device}")

# NOTE: YOLOv11 is slightly less accurate but faster than YOLOv8. It's a drop in replacement
modell_path = './Models/YOLOv11/yolo11n.pt'  # Path to your YOLOv8 model
modell_url = 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt'
modelh_path = './Models/YOLOv8/yolov8x.pt'  # Path to your YOLOv8 model
modelh_url = 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x.pt'

modell = load_yolo_model(modell_path, modell_url)
modelh = load_yolo_model(modelh_path, modelh_url)

modelh.to(device)
modell.to(device)

def classify_objects(image, model, confidence_threshold=0.5, nms_threshold=0.4):
    height, width, channels = image.shape

    # Run inference
    results = model(image)

    class_ids = []
    confidences = []
    boxes = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  # Convert tensor to list and then map to int
            confidence = box.conf.item()  # Convert tensor to scalar
            class_id = box.cls.item()  # Convert tensor to scalar
            if confidence > confidence_threshold:
                boxes.append([x1, y1, x2, y2])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Convert to tensors and move to CPU
    if len(boxes) > 0:
        boxes = torch.tensor(boxes, dtype=torch.float32).cpu()
        confidences = torch.tensor(confidences, dtype=torch.float32).cpu()
    else:
        boxes = torch.empty((0, 4), dtype=torch.float32).cpu()
        confidences = torch.empty((0,), dtype=torch.float32).cpu()

    # Perform NMS on CPU
    indices = torchvision.ops.nms(boxes, confidences, nms_threshold)

    result = []
    if len(indices) > 0:
        for i in indices:
            box = boxes[i].tolist()
            x, y, x2, y2 = map(int, box)  # Ensure coordinates are integers
            w, h = x2 - x, y2 - y
            result.append({
                "class": model.names[class_ids[i]],
                "confidence": confidences[i].item(),
                "box": [x, y, w, h]
            })

            # Draw bounding box
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"{model.names[class_ids[i]]}: {confidences[i]:.2f}"
            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return image, result

def create_unique_filename(extension=".jpg"):
    now = datetime.datetime.now()
    unique_id = uuid.uuid4()
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{unique_id}{extension}"
    return filename

def get_class_names(type='h'):
    if type == 'l':
        model = modell
    elif type == 'h':
        model = modelh
    else:
        return None

    return model.names

def predict(image, type='h', threshold=0.5):
    stime = time.time()
    
    if type == 'l':
        model = modell
    elif type == 'h':
        model = modelh
    else:
        raise ValueError(f"Invalid model type: {type}")

    filename = create_unique_filename()
    
    if os.path.exists("./temp") == False:
        os.mkdir("./temp")
    
    # Save the image
    image.save(f"./temp/{filename}")
    
    # Read the image
    image = cv2.imread(f"./temp/{filename}")
    # image = cv2.flip(image, 1)
    
    # Classify objects
    image, results = classify_objects(image=image, model=model, confidence_threshold=threshold)
    
    # Remove the image
    os.remove(f"./temp/{filename}")
    
    ttime = time.time() - stime
    return image, results, ttime