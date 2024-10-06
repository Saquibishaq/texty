from flask import Flask, request, jsonify
from flask_cors import CORS
from video_generator import generate_video_from_text
import warnings
import atexit

# Ignore resource tracker warnings
warnings.filterwarnings("ignore", category=UserWarning, module='multiprocessing.resource_tracker')

app = Flask(__name__)
CORS(app)  # Enable CORS if needed

def cleanup():
    print("Cleaning up resources...")  # Add any necessary cleanup code

atexit.register(cleanup)

@app.route('/')
def index():
    return "Welcome to the Video Generation API!"

@app.route('/generate', methods=['POST'])
def generate_video():
    data = request.json
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        video_file = generate_video_from_text(prompt)
        return jsonify({"video_file": video_file}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
