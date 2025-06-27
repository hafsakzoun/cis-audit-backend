from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    from app.routes import cis_controls, extractor, generator, indexer, audit_route, register, login
    app.register_blueprint(cis_controls.bp)
    app.register_blueprint(generator.bp)
    app.register_blueprint(register.register)
    app.register_blueprint(extractor.extractor)
    app.register_blueprint(indexer.indexer)
    app.register_blueprint(audit_route.audit_route)
    app.register_blueprint(login.login)   # << This is important!

    return app
