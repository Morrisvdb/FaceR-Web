from flask import Flask, render_template, Response, jsonify, request, session

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

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/post_frame', methods=['POST', 'GET'])
def post_frame():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    print(type(file))
    
    predictions = []
    for i in range(10):
        predictions.append(['label' + str(i), 1.0 - i/10])
    return jsonify(predictions)
    

@app.route('/image')
def image():
    return render_template('image.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')