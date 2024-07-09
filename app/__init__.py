from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig, TestingConfig
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)


    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"message": "Welcome to backend stage two task for the HNG Internship"})        

    from app.routes import auth_bp, user_bp, org_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(org_bp)

    return app

app = create_app(DevelopmentConfig)
