from flask import Flask
from app.config import LocalDevelopmentConfig
from app.database import db 

app = None

def create_app():    
    app = Flask(__name__, template_folder = 'templates')
    app.config.from_object(LocalDevelopmentConfig)
    with app.app_context():
        db.init_app(app)
    return app

app = create_app()
app.app_context().push()
from app.controllers import *

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080
    )