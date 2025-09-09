from flask import Flask
import os
import openai
import dotenv
from time import sleep
from helpers import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'alura'

dotenv.load_dotenv()

from views import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)