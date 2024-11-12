from flask import Flask, render_template, Response, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from predict import predict, get_class_names
from datetime import timedelta
import random, cv2, base64
from __init__ import app, db, cache
from models import Contestant, FoundObjects
import segno
import os
from dotenv import load_dotenv

load_dotenv()
PASSWORD = os.getenv('PASSWORD')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

@app.errorhandler(404)
def page_not_found(e):
    route = request.path
    return render_template('404.html', route=route), 404

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
@cache.cached(timeout=60)
def home():
    with open('./splashtexts.txt', 'r') as file:
        lines = file.readlines()
        splash_text = random.choice(lines).strip()
    return render_template('home.html', splash_text=splash_text)

@app.route('/process')
def process():
    return render_template('process.html')

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
    
    if session.get('is_competing'):
        contestant = Contestant.query.filter_by(username=session['username']).first()
        if contestant is None:
            session['is_competing'] = False
            return redirect(url_for('home'))
        threshold = 0.5

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
        
    
    if session.get('is_competing'):
        contestant = Contestant.query.filter_by(username=session['username']).first()
        if contestant is None:
            session['is_competing'] = False
            return redirect(url_for('home'))
        
        if len(predicts) <= 0:
            pass
        else:
            already_found = FoundObjects.query.filter_by(contestant_id=contestant.id, class_name=predicts[0]['class']).all()
            if already_found:
                pass
            else:
                new_found_object = FoundObjects(class_name=predicts[0]['class'], confidence=predicts[0]['confidence'], contestant_id=contestant.id)
                db.session.add(new_found_object)
                db.session.commit()
        
    return jsonify(predicts)

@app.route('/image')
def image():
    if not session.get('authenticated'):
        return redirect(url_for('login', next_url=url_for('image').split('/')[-1]))
    return render_template('image.html')  

@app.route('/video')
@cache.cached(timeout=60)
def video():
    if not session.get('authenticated'):
        return redirect(url_for('login', next_url=url_for('video').split('/')[-1]))
    class_names = get_class_names('l')
    class_names = class_names.values()
    return render_template('video.html', class_names=class_names)  

@app.route('/qr')
def qr():
    if os.path.exists('./static/qr.png'):
        return render_template('qr.html', qr='static/qr.png')
    return redirect(url_for('qr_setup'))        

@app.route('/qr/setup', methods=['GET', 'POST'])
def qr_setup():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            url = request.form['url']
            qr = segno.make(url)
            qr.save(
                './static/qr.png',
                scale=15,
                border=1,
                )

            return redirect(url_for('qr'))
        else:
            return render_template('qr_setup.html', error='Invalid password')
    return render_template('qr_setup.html')

@app.route('/competition/join', methods=['GET', 'POST'])
def competition_join():
    if session.get('is_competing'):
        return redirect(url_for('competition'))
    if request.method == 'POST':
        username = request.form['username']
        if not username:
            return render_template('join_competition.html', error='Username is required')
        is_in_use = Contestant.query.filter_by(username=username).first()
        if is_in_use:
            return render_template('join_competition.html', error='Username is already in use')
        new_contestant = Contestant(username=username)
        db.session.add(new_contestant)
        db.session.commit()
        session['username'] = username
        session['is_competing'] = True
        return redirect(url_for('competition'))
    
    return render_template('join_competition.html')

@app.route('/competition/leave')
def competition_leave():
    if not session.get('is_competing'):
        return redirect(url_for('join'))
    session['is_competing'] = False
    username = session.pop('username', None)
    user = Contestant.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('home'))
    
@app.route('/competition/leaderboard')
def competition_leaderboard():
    return render_template('leaderboard.html')

@app.route('/competition/reset', methods=['GET', 'POST'])
def reset_competition():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            contestants = Contestant.query.all()
            for contestant in contestants:
                db.session.delete(contestant)
            found_objects = FoundObjects.query.all()
            for found_object in found_objects:
                db.session.delete(found_object)
            db.session.commit()
            
            return redirect(url_for('competition_leaderboard'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/leaderboard')
def leaderboard():
    contestants = Contestant.query.all()
    leaderboard = []
    for contestant in contestants:
        found_objects = FoundObjects.query.filter_by(contestant_id=contestant.id).all()
        victory = 'false'
        if len(found_objects) >= 5:
            victory = 'true'
        leaderboard.append(
            {
                "username": contestant.username,
                "found_objects": len(found_objects),
                "victory": victory
            }
        )
    leaderboard = sorted(leaderboard, key=lambda x: x['found_objects'], reverse=True)
    return jsonify(leaderboard)

@app.route('/competition')
def competition():
    if not session.get('is_competing'):
        return redirect(url_for('competition_join'))
    return render_template('competition.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001, ssl_context='adhoc')
    # app.run(debug=True, host='0.0.0.0', ssl_context=('web/ssl/cert.pem', 'web/ssl/key.pem'), port=5000)