import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from models.config_model import cargar_config
from models.snmp.eaton import consultar_eaton
from models.snmp.kaise import consultar_kaise
from models.snmp.base import test_snmp
from models.historial_model import guardar_historial, limpiar_historial_viejo
from controllers.alerta_controller import evaluar_alertas

# ── Cache compartida ──────────────────────────────────────
_cache: dict = {
    'datos'               : [],
    'ultima_actualizacion': None,
    'alertas_activas'     : [],
}
_cache_lock = threading.Lock()

# ── Consulta individual ───────────────────────────────────
def consultar_uno(ups: dict) -> dict:
    """Consulta un UPS segun su marca y devuelve el resultado enriquecido."""
    marca = ups['marca'].lower()
    if marca == 'eaton':
        datos = consultar_eaton(ups)
    elif marca == 'kaise':
        datos = consultar_kaise(ups)
    else:
        datos = {
            'modelo'        : ups['modelo'],
            'estado'        : 'Sin soporte',
            'autonomia_min' : None,
            'bateria_pct'   : None,
            'voltaje_entrada': None,
            'voltaje_salida' : None,
            'carga_w'       : None,
            'carga_pct'     : None,
            'temperatura'   : None,
        }
    return {
        'nombre'   : ups['nombre'],
        'sala'     : ups['sala'],
        'ubicacion': ups['ubicacion'],
        'marca'    : ups['marca'],
        'ip'       : ups['ip'],
        **datos,
    }

# ── Ciclo de actualización en segundo plano ───────────────
def ciclo_actualizacion() -> None:
    """Consulta todos los UPS en paralelo cada 10 segundos."""
    while True:
        ups_list = cargar_config()
        resultados_map: dict = {}

        with ThreadPoolExecutor(max_workers=15) as executor:
            futuros = {executor.submit(consultar_uno, ups): ups for ups in ups_list}
            for futuro in as_completed(futuros):
                try:
                    resultado = futuro.result()
                    resultados_map[resultado['nombre']] = resultado
                except Exception:
                    pass

        # Mantener el orden original de la lista
        resultados = [
            resultados_map[u['nombre']]
            for u in ups_list
            if u['nombre'] in resultados_map
        ]

        alertas = []
        for u in resultados:
            alertas.extend(evaluar_alertas(u))

        with _cache_lock:
            _cache['datos']                = resultados
            _cache['ultima_actualizacion'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            _cache['alertas_activas']      = alertas

        guardar_historial(resultados)
        limpiar_historial_viejo()
        time.sleep(10)

# ── API pública del controller ────────────────────────────
def get_cache() -> dict:
    """Devuelve una copia segura de la cache actual."""
    with _cache_lock:
        return dict(_cache)

def iniciar_ciclo() -> None:
    """Arranca el hilo de actualización. Llamar solo una vez al iniciar la app."""
    hilo = threading.Thread(target=ciclo_actualizacion, daemon=True)
    hilo.start()

def probar_conexion(ip: str, community: str) -> dict:
    """Prueba la conexion SNMP con un dispositivo."""
    return test_snmp(ip, community)