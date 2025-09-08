"""
Utilidades generales de la aplicación
"""
from datetime import datetime
import pytz

def get_eastern_time():
    """Obtiene la hora actual en Eastern Time"""
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def format_datetime_for_response(dt):
    """Formatea un datetime para respuesta de API en Eastern Time"""
    if dt is None:
        return None
    
    # Si no tiene timezone, asumir UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    # Convertir a Eastern Time
    eastern = pytz.timezone('US/Eastern')
    eastern_time = dt.astimezone(eastern)
    
    # Formatear para respuesta
    return eastern_time.isoformat()

def get_eastern_timezone():
    """Obtiene el objeto timezone de Eastern Time"""
    return pytz.timezone('US/Eastern')
