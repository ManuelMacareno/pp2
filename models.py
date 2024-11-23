from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    equipos = db.relationship('Equipo', backref='usuario', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Equipo(db.Model):
    __tablename__ = 'equipos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)  # Nuevo campo
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # 'ofensivo', 'defensivo', 'equilibrado'
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())  # Nuevo campo
    jugadores = db.relationship('Jugador', secondary='jugador_equipo', lazy='subquery',
        backref=db.backref('equipos', lazy=True))

class JugadorEquipo(db.Model):
    __tablename__ = 'jugador_equipo'
    
    id = db.Column(db.Integer, primary_key=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'), nullable=False)
    
class Jugador(db.Model):
    __tablename__ = 'jugadores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.Text)
    equipo = db.Column(db.Text)
    edad = db.Column(db.Float)
    altura = db.Column(db.Float)
    universidad = db.Column(db.Text)
    pais = db.Column(db.Text)
    partidos_jugados = db.Column(db.Integer)
    puntos_por_partido = db.Column(db.Float)
    rebotes_por_partido = db.Column(db.Float)
    asistencias_por_partido = db.Column(db.Float)
    rating_neto = db.Column(db.Float)
    porcentaje_rebotes_ofensivos = db.Column(db.Float)
    porcentaje_rebotes_defensivos = db.Column(db.Float)
    porcentaje_uso = db.Column(db.Float)
    porcentaje_tiro_efectivo = db.Column(db.Float)
    porcentaje_asistencias = db.Column(db.Float)
    temporada = db.Column(db.Text)
    posicion = db.Column(db.Text)