import cv2
import numpy as np
import os
import datetime
import uuid

def load_yolo_model(weights_path, config_path, names_path):
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Weight file not found: {weights_path}")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    if not os.path.exists(names_path):
        raise FileNotFoundError(f"Names file not found: {names_path}")

    net = cv2.dnn.readNet(weights_path, config_path)
    with open(names_path, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    unconnected_out_layers = net.getUnconnectedOutLayers()

    # Ensure unconnected_out_layers is a list of indices
    if isinstance(unconnected_out_layers, np.ndarray):
        unconnected_out_layers = unconnected_out_layers.flatten()
    output_layers = [layer_names[i - 1] for i in unconnected_out_layers]
    return net, classes, output_layers

def classify_objects(image, net, classes, output_layers, confidence_threshold=0.5, nms_threshold=0.4):
    # if not os.path.exists(image_path):
    #     raise FileNotFoundError(f"Image file not found: {image_path}")

    # image = cv2.imread(image_path)
    height, width, channels = image.shape

    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confidence_threshold:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)

    result = []
    if len(indices) > 0:
        for i in indices.flatten():
            box = boxes[i]
            x, y, w, h = box[0], box[1], box[2], box[3]
            result.append({
                "class": classes[class_ids[i]],
                "confidence": confidences[i],
                "box": [x, y, w, h]
            })

            # Draw bounding box
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"{classes[class_ids[i]]}: {confidences[i]:.2f}"
            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return image, result

def create_unique_filename(extension=".jpg"):
    now = datetime.datetime.now()
    unique_id = uuid.uuid4()
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{unique_id}{extension}"
    return filename

def predict(image):
    base_path = './Models/YOLO3/'
    weights_path = base_path + 'yolov3.weights'
    config_path = base_path + 'yolov3.cfg'
    names_path = base_path + 'coco.names'
    filename = "./temp/" + create_unique_filename()
    if not os.path.exists("./temp"):
        os.makedirs("./temp")
    image.save(filename)
    image = cv2.imread(filename)
    os.remove(filename)

    net, classes, output_layers = load_yolo_model(weights_path, config_path, names_path)
    
    image, results = classify_objects(image, net, classes, output_layers)
    
    return image, results

def cleanup():
    if len(os.listdir("./temp")) > 5:
        for file in os.listdir("./temp"):
            os.remove(f"./temp/{file}")



# Demo:

# image = cv2.imread('webcam_frame.jpg')
# image, results = predict(image)
# cv2.imshow('Image with Bounding Boxes', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
