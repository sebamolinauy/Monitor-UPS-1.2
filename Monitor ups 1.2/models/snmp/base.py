import subprocess

def snmpget(ip: str, community: str, version: str, oid: str) -> str | None:
    """Consulta un OID SNMP y devuelve el valor como string o None si falla."""
    try:
        cmd = ['snmpget', '-v', version, '-c', community, '-t', '2', '-r', '2', ip, oid]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if r.returncode == 0:
            val = r.stdout.strip().split('=')[-1].strip()
            for prefijo in ['INTEGER:', 'STRING:', 'Gauge32:', 'Counter32:', 'Timeticks:']:
                val = val.replace(prefijo, '')
            return val.strip().strip('"')
    except Exception:
        pass
    return None


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