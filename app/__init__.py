from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # ✅ Allow Angular dev server (you can make this stricter in production)
    CORS(app)  # allowing all origins (fine for dev)

    from app.routes import cis_controls, extractor, generator, auth, indexer, audit_route
    app.register_blueprint(cis_controls.bp)
    app.register_blueprint(generator.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(extractor.extractor)
    app.register_blueprint(indexer.indexer)
    app.register_blueprint(audit_route.audit_route)

    return app
