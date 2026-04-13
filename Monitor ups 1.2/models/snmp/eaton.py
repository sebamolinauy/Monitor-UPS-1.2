from models.snmp.base import snmpget

POTENCIAS_EATON = {
    '9e6ki'         : 4800,
    '9e10ki'        : 8000,
    '9px 1500irt2u' : 1500,
    '9sx 20kp'      : 20000,
    '9px30000irt2u' : 30000,
}

def consultar_eaton_9e(ups: dict) -> dict:
    """Consulta UPS Eaton monofasico (9E, 9PX)."""
    ip, c = ups['ip'], ups['community']
    raw = {
        'modelo'         : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.1.2.0'),
        'autonomia_seg'  : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.2.1.0'),
        'bateria_pct'    : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.2.4.0'),
        'voltaje_entrada': snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.3.4.1.2.1'),
        'voltaje_salida' : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.4.4.1.2.1'),
        'carga_w'        : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.4.4.1.4.1'),
        'temperatura'    : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.6.1.0'),
        'estado_raw'     : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.8.1.0'),
    }
    estados = {'1':'En linea','2':'En bateria','3':'Bypass','4':'Falla','5':'Apagando'}
    carga_w    = int(raw['carga_w']) if raw['carga_w'] else None
    modelo_key = ups['modelo'].lower().strip()
    potencia   = POTENCIAS_EATON.get(modelo_key)
    carga_pct  = round((carga_w / potencia) * 100, 1) if (carga_w and potencia) else None
    return {
        'modelo'         : raw['modelo'] or ups['modelo'],
        'autonomia_min'  : int(int(raw['autonomia_seg']) / 60) if raw['autonomia_seg'] else None,
        'bateria_pct'    : int(raw['bateria_pct'])      if raw['bateria_pct']     else None,
        'voltaje_entrada': int(raw['voltaje_entrada'])   if raw['voltaje_entrada'] else None,
        'voltaje_salida' : int(raw['voltaje_salida'])    if raw['voltaje_salida']  else None,
        'carga_w'        : carga_w,
        'carga_pct'      : carga_pct,
        'temperatura'    : int(raw['temperatura'])       if raw['temperatura']     else None,
        'estado'         : estados.get(raw['estado_raw'], 'Sin respuesta') if raw['estado_raw'] else 'Sin respuesta',
    }

def consultar_eaton_9sx(ups: dict) -> dict:
    """Consulta UPS Eaton trifasico (9SX). Estados y OIDs diferentes al 9E."""
    ip, c = ups['ip'], ups['community']
    raw = {
        'modelo'         : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.1.2.0'),
        'autonomia_seg'  : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.2.1.0'),
        'bateria_pct'    : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.2.4.0'),
        'voltaje_entrada': snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.3.8.1.0'),
        'voltaje_salida' : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.4.9.1.0'),
        'carga_w'        : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.4.9.3.0'),
        'carga_pct'      : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.4.1.0'),
        'temperatura'    : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.6.1.0'),
        'estado_raw'     : snmpget(ip, c, '1', '1.3.6.1.4.1.534.1.8.1.0'),
    }
    estados = {
        '1':'Sin soporte', '2':'En linea',  '3':'Bypass',
        '4':'En bateria',  '5':'En linea',  '6':'En linea',
        '10':'En linea',   '11':'Bypass',
    }
    return {
        'modelo'         : raw['modelo'] or ups['modelo'],
        'autonomia_min'  : int(int(raw['autonomia_seg']) / 60) if raw['autonomia_seg'] else None,
        'bateria_pct'    : int(raw['bateria_pct'])      if raw['bateria_pct']     else None,
        'voltaje_entrada': int(raw['voltaje_entrada'])   if raw['voltaje_entrada'] else None,
        'voltaje_salida' : int(raw['voltaje_salida'])    if raw['voltaje_salida']  else None,
        'carga_w'        : int(raw['carga_w'])           if raw['carga_w']         else None,
        'carga_pct'      : int(raw['carga_pct'])         if raw['carga_pct']       else None,
        'temperatura'    : int(raw['temperatura'])       if raw['temperatura']     else None,
        'estado'         : estados.get(raw['estado_raw'], 'Sin respuesta') if raw['estado_raw'] else 'Sin respuesta',
    }

def consultar_eaton(ups: dict) -> dict:
    """Detecta el modelo y llama a la funcion correcta."""
    if '9sx' in ups['modelo'].lower():
        return consultar_eaton_9sx(ups)
    return consultar_eaton_9e(ups)