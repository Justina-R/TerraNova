from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import CheckConstraint, event, UniqueConstraint

#Ciudades en las que pueden estar las propiedades
class Ciudad(db.Model):
    __tablename__ = 'ciudad'
    
    id_ciudad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

#Tipo de propiedad: Departamento, Casa, Local, Oficina, Cochera
class Tipo_Propiedad(db.Model):
    __tablename__ = 'tipo_propiedad'
    
    id_tipo = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)

#Estados de las propiedades: Venta o Alquiler
class Estado_Propiedad(db.Model):
    __tablename__ = 'estado_propiedad'
    
    id_estado = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)

#Estado de las Visitas: Confirmada, Pendiente, Realizada, Cancelada
class Estado_Visita(db.Model):
    __tablename__ = 'estado_visita'
    id_estado = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)

#Roles de los Usuarios= 1: Administrador 2:Agente 3:Cliente
class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)

#Almacenamiento de imágenes de distintas propiedades
class Imagen_Propiedad(db.Model):
    __tablename__ = 'imagen_propiedad'
    
    id_imagen = db.Column(db.Integer, primary_key=True)
    id_propiedad = db.Column(db.Integer, db.ForeignKey('propiedad.id_propiedad', ondelete="CASCADE"), nullable=False)
    url_imagen = db.Column(db.String(200), nullable=False)  # URL o ruta de la imagen
    
    # Relación con la propiedad
    propiedad = db.relationship('Propiedad', backref='imagenes')

#Propiedades de la inmobiliaria con todos sus datos
class Propiedad(db.Model):
    __tablename__ = 'propiedad'
    
    id_propiedad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    #Imagen de la miniatura
    image_url = db.Column(db.String(200), nullable=True)
    id_ciudad = db.Column(db.Integer, db.ForeignKey('ciudad.id_ciudad'))
    #Estado_Propiedad
    id_estado = db.Column(db.Integer, db.ForeignKey('estado_propiedad.id_estado'))
    metros_2 = db.Column(db.Integer, nullable=False)
    cant_habitaciones = db.Column(db.Integer, nullable=False)
    cant_banios = db.Column(db.Integer, nullable=False)
    #Dirección exacta de la propiedad
    ubicacion = db.Column(db.String(200), nullable=False)
    
    #Para chequear que ni metros_2 ni cant_habitaciones sea negativo
    __table_args__ = (
        CheckConstraint('metros_2 >= 0', name='check_metros_2_positive'),
        CheckConstraint('cant_habitaciones >= 0', name='check_cant_habitaciones_positive'),
        CheckConstraint('cant_banios >= 0', name='check_cant_banios_positive'),
    )

    def __repr__(self) -> str:
        return f"<Propiedad {self.nombre} {self.precio}>"


#Almacena las propiedades marcadas como favoritas por un usuario específico
#Vista misFavoritos.html
class Favorito_Usuario(db.Model):
    __tablename__ = 'favorito_usuario'
    
    id_favorito_usuario = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario', ondelete="CASCADE"), nullable=False)
    id_propiedad = db.Column(db.Integer, db.ForeignKey('propiedad.id_propiedad', ondelete="CASCADE"), nullable=False)
    
    propiedad = db.relationship('Propiedad', backref='favoritos')

    __table_args__ = (UniqueConstraint('id_usuario', 'id_propiedad', name='uix_usuario_propiedad'),)

#Datos de las visitas pedidas por Clientes y concretadas por Agentes
#Un agente también puede crear una visita en el dashboard si habla con el cliente por otro medio
class Visita(db.Model):
    __tablename__ = 'visita'
    
    id_visita = db.Column(db.Integer, primary_key=True)
    #Usuario que solicita la visita
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_propiedad = db.Column(db.Integer, db.ForeignKey('propiedad.id_propiedad'), nullable=False)
    fecha_visita = db.Column(db.DateTime, nullable=False)
    #Estado de la visita
    id_estado = db.Column(db.Integer, db.ForeignKey('estado_visita.id_estado'))
    #Agente que realizará la visita
    id_agente = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

    """Relationships: relaciones de alto nivel entre las tablas que nos permite hacer consultas
    intertabla sin necesidad de hacer relaciones. Podemos hacer visita.ciudad y ver la ciudad de la propiedad
    en la que se va a hacer la visita"""
    usuario = db.relationship('Usuario', backref='visitas')
    propiedad = db.relationship('Propiedad', backref='visitas')

#Este evento se ejecutará antes de que se inserte una nueva visita en la base de datos.
@event.listens_for(Visita, 'before_insert')
def validate_agente_before_insert(mapper, connection, target):
# Verificamos si el usuario con id_agente tiene el rol 2 (agente)
    agente = Usuario.query.get(target.id_agente)
    if agente and agente.rol != 2:
        raise ValueError('El id_agente debe ser un usuario con rol de Agente.')

#Usuarios que pueden ser Admin, Agentes o Clientes
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    telefono = db.Column(db.String(15), nullable=False)
    direccion = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)
    rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False, default=3)
    
    favoritos = db.relationship('Favorito_Usuario', backref='usuario', cascade="all, delete", passive_deletes=True)
    
    # Se usa
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Se usa
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id_usuario)

    # Se usa
    def is_authenticated(self):
        return self.rol == 1 or self.rol == 2 or super().is_authenticated()

    def is_active(self):
        return True  # Esto controla si el usuario puede iniciar sesión
    
    def is_anonymous(self):
        return False  # Para usuarios no autenticados
    
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) 

"""Como hemos utilizado Flask-Migrate, se puede modificar estos modelos una vez inicializada la app
con la siguiente línea:
flask db migrate -m "Descripción del cambio" """