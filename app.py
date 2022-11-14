from flask import Flask, make_response, request, jsonify
from db import db
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from blocklist import BLOCKLIST

app = Flask(__name__)
version = "v1"

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Stores REST API"
app.config["API_DESCRIPTION"] = "Rest Api's For Store and Item"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/v1"
app.config[
    "OPENAPI_SWAGGER_UI_URL"
] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sample.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+mariadbconnector://root:root123@10.168.101.84:3306/demo'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db.init_app(app)
api = Api(app)
app.config["JWT_SECRET_KEY"] = "jose"
jwt = JWTManager(app)

migrate = Migrate(app, db)


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "The token is not fresh.",
                "error": "fresh_token_required",
            }
        ),
        401,
    )


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLOCKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


# @app.before_first_request
# def create_tables():
#     db.create_all()


@app.route('/', methods=['GET'])
def home():
    app.logger.debug('Server Check: Status UP')
    return make_response(({'service': 'up', 'success': True, 'swagger_url': f'{request.url}{version}'}), 200)


# Api's Registers into Blueprint
api.register_blueprint(ItemBlueprint)
api.register_blueprint(StoreBlueprint)
api.register_blueprint(TagBlueprint)
api.register_blueprint(UserBlueprint)

if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True, port=8000)
