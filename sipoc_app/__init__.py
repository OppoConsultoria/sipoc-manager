import os
from flask import Flask, redirect, url_for

from sipoc_app.config import Config
from sipoc_app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para continuar."
    login_manager.login_message_category = "warning"
    csrf.init_app(app)

    from sipoc_app import models  # noqa: F401

    from sipoc_app.auth import auth_bp
    from sipoc_app.dashboard import dashboard_bp
    from sipoc_app.empresas import empresas_bp
    from sipoc_app.areas import areas_bp
    from sipoc_app.sipoc import sipoc_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(empresas_bp)
    app.register_blueprint(areas_bp)
    app.register_blueprint(sipoc_bp)

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.home"))

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"now": datetime.utcnow()}

    return app
