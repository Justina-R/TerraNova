from dotenv import load_dotenv
import os

load_dotenv()

class Config():
    #  clave secreta que Flask utiliza para firmar cookies y otros datos sensibles, como las sesiones de usuario
    # lo ideal sería usar una clave secreta aleatoria y más segura
    SECRET_KEY= os.getenv("SECRET_KEY")
    # Indica que la base de datos es local (con SQLite)
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    # desactiva el seguimiento de modificaciones en los objetos de la base de datos para mejorar el rendimiento de la BBDD
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mensaje que aparece cuando queres entrar a una página que tiene el decorador @login_required y no está autenticado
    LOGIN_MESSAGE = None
    # Redireccionar a la página de login si no está autenticado
    LOGIN_VIEW = "public_bp.login"  # public es el blueprint en el que se encuentra el html "login"

    # Configuración de correos (SMTP Gmail)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")