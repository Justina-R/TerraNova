from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Instancia de la base de datos
db = SQLAlchemy()

# Instancia de Flask-Mail
mail = Mail()

# Instancia de Flask-Migrate
migrate = Migrate()