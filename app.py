from flask import Flask, jsonify, request
from task_manager import write_task
import os
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/')
def hello_world():
    return 'Hello from Koyeb'
    

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000)
