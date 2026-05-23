import subprocess

SNMP_TIMEOUT_SEC = 8
SNMP_ATTEMPT_TIMEOUT_SEC = 2
SNMP_RETRIES = 2

_PREFIJOS_VALOR = ('INTEGER:', 'STRING:', 'Gauge32:', 'Counter32:', 'Timeticks:')


def _limpiar_valor_snmp(valor: str) -> str | None:
    val = valor.strip()
    if not val or 'no such' in val.lower():
        return None
    for prefijo in _PREFIJOS_VALOR:
        val = val.replace(prefijo, '')
    val = val.strip().strip('"')
    return val or None


def _parsear_linea_snmp(linea: str) -> str | None:
    if '=' not in linea:
        return None
    _, valor = linea.split('=', 1)
    return _limpiar_valor_snmp(valor)


def _parsear_salida_snmp(stdout: str, oids: list[str]) -> dict[str, str | None]:
    """Asocia cada OID con su valor usando el orden de las lineas de snmpget."""
    lineas = [
        ln.strip()
        for ln in stdout.strip().splitlines()
        if ln.strip() and '=' in ln
    ]
    return {
        oid: _parsear_linea_snmp(lineas[i]) if i < len(lineas) else None
        for i, oid in enumerate(oids)
    }


def _comando_snmpget(ip: str, community: str, version: str, oids: list[str]) -> list[str]:
    return [
        'snmpget',
        '-v', version,
        '-c', community,
        '-t', str(SNMP_ATTEMPT_TIMEOUT_SEC),
        '-r', str(SNMP_RETRIES),
        ip,
        *oids,
    ]


def snmpget(ip: str, community: str, version: str, oid: str) -> str | None:
    """Consulta un OID SNMP y devuelve el valor como string o None si falla."""
    return snmpget_multi(ip, community, version, [oid]).get(oid)


def snmpget_multi(ip: str, community: str, version: str, oids: list[str]) -> dict[str, str | None]:
    """Consulta varios OIDs en un solo round-trip SNMP."""
    if not oids:
        return {}

    vacio = {oid: None for oid in oids}
    try:
        cmd = _comando_snmpget(ip, community, version, oids)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=SNMP_TIMEOUT_SEC)
        if r.returncode != 0 or not r.stdout.strip():
            return vacio
        return _parsear_salida_snmp(r.stdout, oids)
    except Exception:
        return vacio


def test_snmp(ip: str, community: str) -> dict:
    """Prueba la conexion SNMP con un dispositivo. Devuelve ok, descripcion y version."""
    for ver in ['1', '2c']:
        for oid, desc in [
            ('1.3.6.1.2.1.1.1.0',             'Dispositivo'),
            ('1.3.6.1.4.1.534.1.1.2.0',       'Eaton'),
            ('1.3.6.1.4.1.935.1.1.1.2.2.1.0', 'Kaise'),
        ]:
            val = snmpget(ip, community, ver, oid)
            if val:
                return {'ok': True, 'descripcion': f'{desc}: {val}', 'version': ver}
    return {'ok': False, 'descripcion': 'Sin respuesta SNMP en v1 y v2c', 'version': None}
