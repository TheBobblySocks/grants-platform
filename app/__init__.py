from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from config import config
from programme_config import PROGRAMME

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    try:
        app.jinja_loader = ChoiceLoader([
            PackageLoader("app"),
            PrefixLoader({
                "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
            }),
        ])
        from govuk_frontend_wtf.main import WTFormsHelpers
        WTFormsHelpers(app)
    except Exception:
        pass

    @app.context_processor
    def inject_programme():
        return {"programme": PROGRAMME}

    from app.blueprints.auth import auth as auth_bp
    from app.blueprints.public import public as public_bp
    from app.blueprints.applicant import applicant as applicant_bp
    from app.blueprints.assessor import assessor as assessor_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(applicant_bp)
    app.register_blueprint(assessor_bp)

    return app


@login_manager.user_loader
def load_user(user_id: str):
    from app.models import User
    return User.query.get(int(user_id))
