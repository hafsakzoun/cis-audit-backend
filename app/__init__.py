from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # CORS fix - allow Angular on port 4200
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes import cis_controls, extractor, generator, auth, indexer  # ✅ include indexer
    app.register_blueprint(cis_controls.bp)
    app.register_blueprint(generator.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(extractor.extractor)
    app.register_blueprint(indexer.indexer)  # ✅ register it

    return app
