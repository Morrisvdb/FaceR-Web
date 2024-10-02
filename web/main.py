from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for
from predict import predict, get_class_names
from datetime import timedelta
import random, cv2, base64

app = Flask(__name__)
app.secret_key = 'kk321i2h9dbu292du2jb3riqudijnasjdkch'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

PASSWORD = 'cals1900'
ADMIN_PASSWORD = '2008'

@app.errorhandler(404)
def page_not_found(e):
    route = request.path
    return render_template('404.html', route=route), 404

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    with open('web/splashtexts.txt', 'r') as file:
        lines = file.readlines()
        splash_text = random.choice(lines).strip()
    return render_template('home.html', splash_text=splash_text)

@app.route('/login/<next_url>', methods=['GET', 'POST'])
def login(next_url):
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            session['authenticated'] = True
            session.permanent = True
            if next_url:
                return redirect(url_for(next_url))
            else:
                return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('home'))

@app.route('/logout_all', methods=['GET', 'POST'])
def logout_all():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session.clear()
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/post_frame/<type>/<threshold>', methods=['POST', 'GET'])
def post_frame(type, threshold):
    if type not in ['l', 'h']:
        return jsonify({"error": "Invalid model type"}), 400
    if 'frame' not in request.files:
        return jsonify({"error": "No file part"}), 400
    try:
        threshold = float(threshold)
        if threshold < 0 or threshold > 1:
            return jsonify({"error": "Invalid threshold"}), 400
    except ValueError:
        return jsonify({"error": "Invalid threshold"}), 400

    frame = request.files['frame']
    image, predictions, ttime = predict(frame, type, threshold)
    
    predicts = []
    for prediction in predictions:
        predicts.append(
            {
                "class": prediction['class'],
                "confidence": prediction['confidence'],
                "box": prediction['box'],
            }
        )        
    return jsonify(predicts)

@app.route('/image')
def image():
    if not session.get('authenticated'):
        return redirect(url_for('login', next_url=url_for('image').split('/')[-1]))
    return render_template('image.html')  

@app.route('/video')
def video():
    if not session.get('authenticated'):
        return redirect(url_for('login', next_url=url_for('video').split('/')[-1]))
    class_names = get_class_names('l')
    class_names = class_names.values()
    return render_template('video.html', class_names=class_names)  

@app.route('/upload')
def upload():
    if not session.get('authenticated'):
        return redirect(url_for('login', next_url=url_for('image').split('/')[-1]))
    return render_template('upload.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')
    # app.run(debug=True, host='0.0.0.0', ssl_context=('web/ssl/cert.pem', 'web/ssl/key.pem'), port=5000)