from flask import Flask

app = Flask(__name__)

@app.route('/')
def default():
    return 'Check out Werkzeug debug console at /console'
