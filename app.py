from flask import Flask
import os
path = os.path.join(os.getcwd(), 'json')
os.chdir(path)
app = Flask(__name__)


@app.route('/')
def homepage():
    inform = "Home page of Hetengtech's api, Rainfall api: hetengtech.ngrok.io/rain, Waterlevel api: hetengtech.ngrok.io/waterlevel "

    return inform


@app.route('/rain')
def rain():
    with open('rainfall.json') as f:
        lines = f.read()
    RainJson = lines

    return RainJson


@app.route('/waterlevel')
def waterlevel():
    with open('waterlevel.json') as f:
        lines = f.read()
    WaterlevelJson = lines

    return WaterlevelJson


if __name__ == '__main__':
    from datetime import datetime
    app.run(host='localhost', port=8080)