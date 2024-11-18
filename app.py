from flask import Flask, jsonify, request
from task_manager import write_task
import os
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/')
def hello_world():
    return 'Hello from Koyeb'
    
@app.route('/upload', methods=['GET'])
def upload_video():
    chat_id = request.args.get('chatid')
    video_url = request.args.get('url')
    write_task(chat_id=chat_id, url=video_url)
    return jsonify({"message": "Video add to task list!"})


if __name__ == "__main__":
    app.run(port=8000)
