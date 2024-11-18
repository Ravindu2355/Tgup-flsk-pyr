from flask import Flask, jsonify
import os
from flask_cors import CORS

opw = os.getenv('opw')
app = Flask(__name__)

CORS(app)

@app.route('/')
def hello_world():
    return 'Hello from Koyeb'


if __name__ == "__main__":
    app.run(port=8000)
