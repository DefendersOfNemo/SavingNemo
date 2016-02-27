# imports
#import os
from flask import Flask

#basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')

app = Flask(__name__, template_folder="../../client/templates", static_folder="../../client/static")
app.config.from_object('app.config')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# avoiding circular reference error, placing import below.
from app import views