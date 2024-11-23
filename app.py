from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Jugador, Equipo, JugadorEquipo
import os
import logging

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración de la aplicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
instance_path = os.path.join(BASE_DIR, 'instance')
database_path = os.path.join(instance_path, 'database.db')

app.config.update(
    SECRET_KEY='tu_clave_secreta_aqui',
    SQLALCHEMY_DATABASE_URI=f'sqlite:///{database_path}',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    TEMPLATES_AUTO_RELOAD=True  # Útil durante el desarrollo
)

# Asegurar que existe el directorio de la base de datos
os.makedirs(instance_path, exist_ok=True)

# Inicialización de extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        logger.info(f"Intento de registro para usuario: {username}")
        
        if not username or not password or not password_confirm:
            flash('Por favor completa todos los campos', 'danger')
            return redirect(url_for('login'))
            
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('login'))
        
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso', 'danger')
            return redirect(url_for('login'))
        
        nuevo_usuario = Usuario(username=username)
        nuevo_usuario.set_password(password)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        logger.info(f"Usuario {username} creado exitosamente")
        
        login_user(nuevo_usuario)
        flash('¡Registro exitoso! Bienvenido.', 'success')
        return redirect(url_for('index'))
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en el registro: {str(e)}")
        flash('Error en el registro. Por favor intenta nuevamente.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

# Rutas principales
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/armar_equipo')
@login_required
def armar_equipo():
    return render_template('armar_equipo.html')

@app.route('/mis_equipos')
@login_required
def mis_equipos():
    equipos = Equipo.query.filter_by(usuario_id=current_user.id).order_by(Equipo.fecha_creacion.desc()).all()
    return render_template('mis_equipos.html', equipos=equipos)

# Rutas de la API
@app.route('/api/jugadores')
@login_required
def get_jugadores():
    try:
        jugadores = Jugador.query.all()
        return jsonify([{
            'id': j.id,
            'nombre': j.nombre,
            'equipo': j.equipo,
            'posicion': j.posicion,
            'edad': j.edad,
            'altura': j.altura,
            'puntos_por_partido': j.puntos_por_partido
        } for j in jugadores])
    except Exception as e:
        logger.error(f"Error al obtener jugadores: {str(e)}")
        return jsonify({'error': 'Error al obtener los jugadores'}), 500

@app.route('/api/jugadores/<int:id>')
@login_required
def get_jugador(id):
    try:
        jugador = Jugador.query.get_or_404(id)
        return jsonify({
            'id': jugador.id,
            'nombre': jugador.nombre,
            'equipo': jugador.equipo,
            'posicion': jugador.posicion,
            'edad': jugador.edad,
            'altura': jugador.altura,
            'universidad': jugador.universidad,
            'pais': jugador.pais,
            'partidos_jugados': jugador.partidos_jugados,
            'puntos_por_partido': jugador.puntos_por_partido,
            'rebotes_por_partido': jugador.rebotes_por_partido,
            'asistencias_por_partido': jugador.asistencias_por_partido
        })
    except Exception as e:
        logger.error(f"Error al obtener jugador {id}: {str(e)}")
        return jsonify({'error': 'Error al obtener los detalles del jugador'}), 500

@app.route('/api/jugadores_por_posicion/<posicion>')
@login_required
def get_jugadores_por_posicion(posicion):
    try:
        jugadores = Jugador.query.filter_by(posicion=posicion).all()
        return jsonify([
            {
                'id': j.id,
                'nombre': j.nombre,
                'equipo': j.equipo,
                'posicion': j.posicion,
                'puntos_por_partido': j.puntos_por_partido,
                'rebotes_por_partido': j.rebotes_por_partido,  # Agregar rebotes
                'asistencias_por_partido': j.asistencias_por_partido  # Agregar asistencias
            }
            for j in jugadores
        ])
    except Exception as e:
        logger.error(f"Error al obtener jugadores por posición {posicion}: {str(e)}")
        return jsonify({'error': 'Error al obtener los jugadores'}), 500

@app.route('/api/crear_equipo', methods=['POST'])
@login_required
def crear_equipo():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        tipo_equipo = data.get('tipo')
        jugadores_ids = data.get('jugadores')
        
        if not nombre or not tipo_equipo or not jugadores_ids:
            return jsonify({'error': 'Datos incompletos'}), 400
            
        # Verificar si ya existe un equipo con ese nombre para el usuario actual
        equipo_existente = Equipo.query.filter_by(
            usuario_id=current_user.id,
            nombre=nombre
        ).first()
        
        if equipo_existente:
            return jsonify({'error': 'Ya tienes un equipo con ese nombre'}), 400
            
        # Crear nuevo equipo
        nuevo_equipo = Equipo(
            nombre=nombre,
            usuario_id=current_user.id,
            tipo=tipo_equipo
        )
        
        db.session.add(nuevo_equipo)
        db.session.flush()
        
        # Agregar jugadores al equipo
        for jugador_id in jugadores_ids:
            jugador = Jugador.query.get(jugador_id)
            if jugador:
                nuevo_equipo.jugadores.append(jugador)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipo creado exitosamente',
            'equipo_id': nuevo_equipo.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear equipo: {str(e)}")
        return jsonify({'error': f'Error al crear el equipo: {str(e)}'}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
        logger.info("Base de datos inicializada")
        
    app.run(debug=True)