import cv2
import numpy as np
import os
import datetime
import uuid
from ultralytics import YOLO, solutions
import time
import torch


def load_yolo_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = YOLO(model_path)
    return model

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# NOTE: YOLOv11 is slightly less accurate but faster than YOLOv8. It's a drop in replacement
modell_path = './Models/YOLOv11/yolo11n.pt'  # Path to your YOLOv8 model
# modell_path = './Models/YOLOv8/yolov8n.pt'  # Path to your YOLOv8 model
modelh_path = './Models/YOLOv8/yolov8x.pt'  # Path to your YOLOv8 model
# modelh_path = './Models/YOLOv11/yolo11x.pt'  # Path to your YOLOv8 model

modell = load_yolo_model(modell_path)
modelh = load_yolo_model(modelh_path)

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
                boxes.append([x1, y1, x2 - x1, y2 - y1])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)

    result = []
    if len(indices) > 0:
        for i in indices.flatten():
            box = boxes[i]
            x, y, w, h = box[0], box[1], box[2], box[3]
            result.append({
                "class": model.names[class_ids[i]],
                "confidence": confidences[i],
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
    
    # Save the image
    image.save(f"./temp/{filename}")
    
    # Read the image
    image = cv2.imread(f"./temp/{filename}")
    image = cv2.flip(image, 1)
    
    # Classify objects
    image, results = classify_objects(image=image, model=model, confidence_threshold=threshold)
    
    # Remove the image
    os.remove(f"./temp/{filename}")
    
    ttime = time.time() - stime
    return image, results, ttime
