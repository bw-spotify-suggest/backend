from flask import Flask

def create_app():
    app_start = Flask(__name__)
    return app_start

APP = create_app()