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
    
    image, predictions, ttime = predict(frame)
    print(predictions)
    predicts = []
    for prediction in predictions:
        predicts.append(
            {
                "class": prediction['class'],
                "confidence": prediction['confidence'],
                "box": prediction['box']
            }
        )
    # predicts.append(
    #     {
    #         "time": ttime
    #     }
    # )
    return jsonify(predicts)



[
    {'class': 'person', 'confidence': 0.6562302112579346, 'box': [93, 1, 544, 276]}, 
    {'class': 'person', 'confidence': 0.6224901676177979, 'box': [1, 260, 251, 219]}
    ]

@app.route('/image')
def image():
    return render_template('image.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')