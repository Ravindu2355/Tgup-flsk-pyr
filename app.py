from flask import Flask, jsonify, request
from task_manager import write_task
import os
from bot import app as tg
from bot import upload_from_url
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
    if not chat_id or not video_url:
        return jsonify({"s":0,"message": "No parameter found!"})
    try:
        async def run_upload():
          async with tg:
            await upload_from_url(tg, chat_id=chat_id, url=video_url)

    # Run the async function in the event loop
    asyncio.run(run_upload())
    
    return jsonify({"s":1,"message": "Video add to task list!"})


if __name__ == "__main__":
    app.run(port=8000)
