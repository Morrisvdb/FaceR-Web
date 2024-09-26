from flask import Flask, render_template, Response, jsonify, request, session
from predict import predict
import time

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    route = request.path
    return render_template('404.html', route=route), 404

@app.route('/')
def index():
    return render_template('video.html')

@app.route('/home')
def home():
    return render_template('home.html')

# @app.route('/video')
# def video():
#     return render_template('video.html')

@app.route('/post_frame', methods=['POST', 'GET'])
def post_frame():
    if 'frame' not in request.files:
        return jsonify({"error": "No file part"}), 400

    frame = request.files['frame']
    
    predictions = predict(frame)
    predicts = []
    for prediction in predictions[-1:][0]:
        predicts.append(
            {
                "class": prediction['class'],
                "confidence": prediction['confidence'],
                "box": prediction['box']
            }
        )
    return jsonify(predicts)    

[{'class': 'person', 'confidence': 0.9668554663658142, 'box': [481, 339, 89, 112]}, 
 {'class': 'person', 'confidence': 0.9501999020576477, 'box': [175, 198, 283, 283]}, 
 {'class': 'person', 'confidence': 0.6560819745063782, 'box': [174, 314, 65, 127]}]


@app.route('/image')
def image():
    return render_template('image.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')