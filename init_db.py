from flask import Flask
from models import db, Usuario, Jugador
import pandas as pd
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_numeric_columns(df):
    """Convierte columnas numéricas de formato europeo (comas) a formato con puntos"""
    numeric_columns = [
        'age', 'player_height', 'pts', 'reb', 'ast', 'net_rating',
        'oreb_pct', 'dreb_pct', 'usg_pct', 'ts_pct', 'ast_pct'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)
    
    if 'gp' in df.columns:
        df['gp'] = df['gp'].astype(int)
    
    return df

def get_best_season_by_player(df):
    """
    Selecciona la temporada con mejor PPP para cada jugador.
    Retorna un DataFrame con solo los mejores registros.
    """
    # Ordenar por jugador y PPP de manera descendente
    df_sorted = df.sort_values(['player_name', 'pts'], ascending=[True, False])
    
    # Tomar el primer registro (mejor PPP) para cada jugador
    best_seasons = df_sorted.groupby('player_name').first().reset_index()
    
    logger.info(f"Registros originales: {len(df)}, Registros únicos: {len(best_seasons)}")
    return best_seasons

def init_database():
    # Crear la aplicación Flask
    app = Flask(__name__)
    
    # Configuración
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    instance_path = os.path.join(BASE_DIR, 'instance')
    database_path = os.path.join(instance_path, 'database.db')
    
    os.makedirs(instance_path, exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info(f"Usando base de datos en: {database_path}")
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("Tablas creadas exitosamente")
            
            # Verificar si ya existen datos
            if not Jugador.query.first():
                
                csv_path = os.path.join(BASE_DIR, 'database', 'jugadores.csv')
                
                if not os.path.exists(csv_path):
                    logger.error(f"No se encuentra el archivo CSV en: {csv_path}")
                    return
                
                logger.info(f"Leyendo datos desde: {csv_path}")
                
                df = pd.read_csv(csv_path, delimiter=',')
                
                columnas_necesarias = [
                    'player_name', 'team_abbreviation', 'age', 'player_height',
                    'college', 'country', 'gp', 'pts', 'reb', 'ast', 'net_rating',
                    'oreb_pct', 'dreb_pct', 'usg_pct', 'ts_pct', 'ast_pct', 'season'
                ]
                df = df[columnas_necesarias]
                df = convert_numeric_columns(df)
                df = get_best_season_by_player(df)
                
                # Asignar posiciones
                def assign_position(height):
                    if height <= 180.0: return 'Base'
                    elif height <= 190.0: return 'Escolta'
                    elif height <= 200.9: return 'Alero'
                    elif height <= 210.0: return 'Ala-pívot'
                    else: return 'Pívot'
                
                df['position'] = df['player_height'].apply(assign_position)
                
                # Renombrar columnas
                column_names = {
                    'player_name': 'nombre',
                    'team_abbreviation': 'equipo',
                    'age': 'edad',
                    'player_height': 'altura',
                    'college': 'universidad',
                    'country': 'pais',
                    'gp': 'partidos_jugados',
                    'pts': 'puntos_por_partido',
                    'reb': 'rebotes_por_partido',
                    'ast': 'asistencias_por_partido',
                    'net_rating': 'rating_neto',
                    'oreb_pct': 'porcentaje_rebotes_ofensivos',
                    'dreb_pct': 'porcentaje_rebotes_defensivos',
                    'usg_pct': 'porcentaje_uso',
                    'ts_pct': 'porcentaje_tiro_efectivo',
                    'ast_pct': 'porcentaje_asistencias',
                    'season': 'temporada',
                    'position': 'posicion'
                }
                
                df = df.rename(columns=column_names)
                
                # Insertar datos
                for _, row in df.iterrows():
                    try:
                        jugador = Jugador(**row.to_dict())
                        db.session.add(jugador)
                    except Exception as e:
                        logger.error(f"Error al insertar jugador {row['nombre']}: {str(e)}")
                        db.session.rollback()
                        continue
                
                logger.info("Datos de jugadores insertados")
                
                # Crear usuario admin si no existe
                if not Usuario.query.filter_by(username='admin').first():
                    usuario = Usuario(username='admin')
                    usuario.set_password('admin123')
                    db.session.add(usuario)
                    logger.info("Usuario admin creado")
                
                db.session.commit()
                logger.info("Base de datos inicializada exitosamente")
                
        except Exception as e:
            logger.error(f"Error al inicializar la base de datos: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    try:
        init_database()
        logger.info("Proceso de inicialización completado")
    except Exception as e:
        logger.error(f"Error en la inicialización: {str(e)}")