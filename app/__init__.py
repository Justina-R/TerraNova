from app.config import Config
from flask import Flask
from app.extensions import db, init_login_manager, mail, migrate
#IMPORTAR BLUEPRINTS
from app.blueprints.admin_bp import admin_bp
from app.blueprints.mail_bp import mail_bp
from app.blueprints.public_bp import public_bp
from app.blueprints.user_bp import user_bp
from app.blueprints.errors_bp import errors_bp
from dotenv import load_dotenv
import os

load_dotenv()

def crear_admin(app):
    """Crea un usuario administrador si no existe."""
    with app.app_context():
        from app.models import Usuario  # ✅ Importación diferida

        if not Usuario.query.filter_by(email=os.getenv("ADMIN_MAIL")).first():
            admin = Usuario(
                nombre='admin',
                apellido='1',
                email= os.getenv("ADMIN_MAIL"),
                rol= 1,
                telefono= os.getenv("ADMIN_PHONE"),
                direccion= os.getenv("ADMIN_ADDRESS")
            )
            admin.set_password(os.getenv("ADMIN_PASSWORD"))  # Hashea la contraseña
            db.session.add(admin)
            db.session.commit()


# Crea y configura una instancia de la aplicación Flask
def crear_app():
    app = Flask(__name__, template_folder="templates")
    #  Carga la configuración de la aplicación desde una clase llamada Config sacada de config.py
    app.config.from_object(Config)

    # Inicializa la extensión de la base de datos y la vincula con Flask (init_app)
    db.init_app(app)
    init_login_manager(app)
    mail.init_app(app)
    migrate.init_app(app, db) # conecta Flask-Migrate con la app y la base de datos

    #Registrar blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(mail_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(errors_bp)

    with app.app_context():
        db.create_all() # Crea las tablas si no existen
        crear_admin(app)  # Llamamos a la función para crear el admin

    return app

