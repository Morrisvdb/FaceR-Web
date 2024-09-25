import torch, cv2, numpy as np
import torchvision.transforms as transforms
from PIL import Image
import requests
from torchvision.models import (
    resnet18, resnet34, resnet50, resnet101, resnet152,
    ResNet18_Weights, ResNet34_Weights, ResNet50_Weights, ResNet101_Weights, ResNet152_Weights,
)

# Choose the ResNet model
model_name = 'resnet18'  # Change to 'resnet18', 'resnet34', 'resnet101', or 'resnet152' as needed

if model_name == 'resnet18':
    model = resnet18(weights=ResNet18_Weights.DEFAULT)
    preprocess = ResNet18_Weights.DEFAULT.transforms()
elif model_name == 'resnet34':
    model = resnet34(weights=ResNet34_Weights.DEFAULT)
    preprocess = ResNet34_Weights.DEFAULT.transforms()
elif model_name == 'resnet50':
    model = resnet50(weights=ResNet50_Weights.DEFAULT)
    preprocess = ResNet50_Weights.DEFAULT.transforms()
elif model_name == 'resnet101':
    model = resnet101(weights=ResNet101_Weights.DEFAULT)
    preprocess = ResNet101_Weights.DEFAULT.transforms()
elif model_name == 'resnet152':
    model = resnet152(weights=ResNet152_Weights.DEFAULT)
    preprocess = ResNet152_Weights.DEFAULT.transforms()
else:
    raise ValueError(f"Invalid model name: {model_name}")

model.eval()
# Define the image transformations
preprocess = ResNet50_Weights.DEFAULT.transforms()

# Download the ImageNet class labels
LABELS_URL = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
response = requests.get(LABELS_URL)
class_labels = response.json()

def classify_image(image):
    """Classifies the given image using the ResNet model.

    Args:
        image (np.Image): The image to classify

    Returns:
        list: The top 10 predictions
    """
    # Convert the frame to a PIL image
    pil_image = Image.fromarray(image)
    image = preprocess(pil_image)
    image = image.unsqueeze(0)  # Add batch dimension

    # Perform the prediction
    with torch.no_grad():
        output = model(image)

    # The output has unnormalized scores. To get probabilities, you can run a softmax on it.
    probabilities = torch.nn.functional.softmax(output[0], dim=0)

    # Get the top 10 predictions
    top10_prob, top10_catid = torch.topk(probabilities, 10)
    top10_predictions = [(class_labels[catid], prob.item()) for catid, prob in zip(top10_catid, top10_prob)]

    return top10_predictions

def find_objects(image):
    # NOT IN USE
    # Load YOLO
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # Load COCO labels
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # Convert the frame to a blob
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Initialize lists to hold detection data
    class_ids = []
    confidences = []
    boxes = []

    # Process each output
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * image.shape[1])
                center_y = int(detection[1] * image.shape[0])
                w = int(detection[2] * image.shape[1])
                h = int(detection[3] * image.shape[0])

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-max suppression to remove overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Prepare the list of detected objects
    detected_objects = []
    for i in indices:
        i = i[0]
        box = boxes[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        detected_objects.append({
            "class": classes[class_ids[i]],
            "confidence": confidences[i],
            "box": [x, y, w, h]
        })

    return detected_objects