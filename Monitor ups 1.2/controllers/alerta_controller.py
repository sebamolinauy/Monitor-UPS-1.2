UMBRAL_VOLTAJE_MIN = 200   # ROJO si voltaje entrada < 200V
UMBRAL_BATERIA_MIN = 30    # ROJO si bateria < 30%
UMBRAL_CARGA_MAX   = 40    # NARANJA si carga > 40% potencia nominal

def evaluar_alertas(u: dict) -> list[dict]:
    """
    Evalua un UPS y devuelve lista de alertas activas.
    Rojo  : desconexion, en bateria, falla, bypass,
            voltaje entrada < 200V, bateria < 30%
    Naranja: carga > 40% de la potencia nominal
    """
    alertas = []
    from datetime import datetime
    hora = datetime.now().strftime('%H:%M:%S')

    def alerta(estado: str, nivel: str) -> dict:
        return {
            'ups'   : u['nombre'],
            'sala'  : u['sala'],
            'estado': estado,
            'nivel' : nivel,
            'hora'  : hora,
        }

    # ROJO: sin respuesta
    if u['estado'] == 'Sin respuesta':
        alertas.append(alerta('UPS desconectada o sin respuesta', 'falla'))

    # ROJO: estado critico
    if u['estado'] in ('En bateria', 'Falla', 'Bypass', 'Apagando'):
        alertas.append(alerta(u['estado'], 'falla'))

    # ROJO: voltaje bajo
    if u.get('voltaje_entrada') is not None and u['voltaje_entrada'] < UMBRAL_VOLTAJE_MIN:
        alertas.append(alerta(f"Voltaje entrada bajo: {u['voltaje_entrada']}V", 'falla'))

    # ROJO: bateria critica
    if u.get('bateria_pct') is not None and u['bateria_pct'] < UMBRAL_BATERIA_MIN:
        alertas.append(alerta(f"Bateria critica: {u['bateria_pct']}%", 'falla'))

    # NARANJA: carga elevada
    if u.get('carga_pct') is not None and u['carga_pct'] > UMBRAL_CARGA_MAX and u['estado'] == 'En linea':
        alertas.append(alerta(f"Carga elevada: {u['carga_pct']}%", 'advertencia'))

    return alertas