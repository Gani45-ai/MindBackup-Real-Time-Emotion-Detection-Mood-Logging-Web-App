from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os, base64, cv2, numpy as np, time
from pathlib import Path
from db import init_db, add_memory, get_counts_period
from deepface import DeepFace

app = Flask(__name__)
CORS(app)

BASE = Path(__file__).parent
MEM_DIR = BASE / 'memories'
MEM_DIR.mkdir(exist_ok=True)

init_db()

EMOJI_MAP = {
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'surprise': '😮',
    'neutral': '😐',
    'fear': '😨',
    'disgust': '🤢'
}

def decode_image(b64data):
    header, encoded = b64data.split(',', 1) if ',' in b64data else (None, b64data)
    data = base64.b64decode(encoded)
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    payload = request.json
    img_b64 = payload.get('image')
    if not img_b64:
        return jsonify({'error': 'no image'}), 400
    img = decode_image(img_b64)
    try:
        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
        if isinstance(result, list):
            result = result[0]
        emotion = result.get('dominant_emotion') or max(result.get('emotion', {}), key=result.get('emotion', {}).get)
        confidence = 0.0
        if 'emotion' in result and emotion in result['emotion']:
            confidence = float(result['emotion'][emotion])
        else:
            confidence = 0.0
    except Exception as e:
        print('DeepFace error:', e)
        emotion = 'neutral'
        confidence = 0.0

    ts = int(time.time())
    fname = f"{emotion}_{ts}.png"
    fpath = MEM_DIR / fname
    cv2.imwrite(str(fpath), img)
    add_memory(emotion, confidence, fname)
    return jsonify({'emotion': emotion, 'confidence': confidence, 'emoji': EMOJI_MAP.get(emotion, '🙂'), 'filename': fname})

@app.route('/memories/<path:fname>')
def serve_mem(fname):
    return send_from_directory(str(MEM_DIR), fname)

@app.route('/stats')
def stats():
    data = {
        'minute': get_counts_period('minute'),
        'hour': get_counts_period('hour'),
        'day': get_counts_period('day'),
        'week': get_counts_period('week'),
        'month': get_counts_period('month')
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
