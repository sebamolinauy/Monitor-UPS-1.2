from models.snmp.base import snmpget

def consultar_kaise(ups: dict) -> dict:
    """Consulta UPS Kaise. Autonomia viene en minutos directamente."""
    ip, c = ups['ip'], ups['community']
    raw = {
        'autonomia_min'  : snmpget(ip, c, '1', '1.3.6.1.4.1.935.1.1.1.2.2.3.0'),
        'bateria_pct'    : snmpget(ip, c, '1', '1.3.6.1.4.1.935.1.1.1.2.2.1.0'),
        'temperatura'    : snmpget(ip, c, '1', '1.3.6.1.4.1.935.1.1.1.2.2.2.0'),
        'estado_raw'     : snmpget(ip, c, '1', '1.3.6.1.4.1.935.1.1.1.3.1.1.0'),
        'voltaje_entrada': snmpget(ip, c, '1', '1.3.6.1.4.1.935.1.1.1.3.2.1.0'),
        'voltaje_salida' : snmpget(ip, c, '1', '1.3.6.1.4.1.935.1.1.1.4.2.1.0'),
        'carga_pct'      : snmpget(ip, c, '1', '1.3.6.1.4.1.935.1.1.1.4.2.3.0'),
    }
    estados = {'1':'En linea','2':'En bateria','3':'Bypass','4':'Falla'}
    return {
        'modelo'         : ups['modelo'],
        'autonomia_min'  : int(raw['autonomia_min'])                          if raw['autonomia_min']   else None,
        'bateria_pct'    : int(raw['bateria_pct'])                            if raw['bateria_pct']     else None,
        'voltaje_entrada': round(int(raw['voltaje_entrada']) / 10, 1)         if raw['voltaje_entrada'] else None,
        'voltaje_salida' : round(int(raw['voltaje_salida'])  / 10, 1)         if raw['voltaje_salida']  else None,
        'carga_w'        : None,
        'carga_pct'      : int(raw['carga_pct'])                              if raw['carga_pct']       else None,
        'temperatura'    : int(raw['temperatura'])                            if raw['temperatura']     else None,
        'estado'         : estados.get(raw['estado_raw'], 'Sin respuesta')    if raw['estado_raw']      else 'Sin respuesta',
    }