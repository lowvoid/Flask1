from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_mail import Mail
from VAG.config import Config
from flask_admin import Admin
from flask_wtf import CSRFProtect

# Extensions
FontAwesome()
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
ckeditor = CKEditor()
mail = Mail()
admin = Admin()
csrf = CSRFProtect()
# Login manager
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    FontAwesome(app)
    app.config.from_object(Config)

    from VAG.adminbp.routes import MyAdminIndexView

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexView())
    csrf.init_app(app)

    # Blueprints
    from VAG.main.routes import main
    from VAG.users.routes import users
    from VAG.features.routes import features_bp
    from VAG.services.routes import services_bp
    from VAG.errors.handlers import errors
    from VAG.adminbp.routes import adminbp

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(features_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(errors)
    app.register_blueprint(adminbp)

    return app
