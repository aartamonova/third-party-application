from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bootstrap import Bootstrap

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

bootstrap = Bootstrap(app)

from third_party_app.routes import index_routes, errors_routes
