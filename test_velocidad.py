import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Lista completa de IPs a probar
UPS_LIST = [
    {'nombre': 'A-G1-UPS1',  'ip': '10.44.87.95'},
    {'nombre': 'A-G1-UPS2',  'ip': '10.44.87.96'},
    {'nombre': 'A-G2-UPS1',  'ip': '10.44.87.137'},
    {'nombre': 'A-G3-UPS1',  'ip': '10.44.87.138'},
    {'nombre': 'A-G3-UPS2',  'ip': '10.44.87.139'},
    {'nombre': 'BC-UPS1',    'ip': '10.44.87.93'},
    {'nombre': 'BC-UPS2',    'ip': '10.44.87.94'},
    {'nombre': 'D-UPS1',     'ip': '10.44.87.136'},
    {'nombre': 'D-UPS2',     'ip': '10.44.87.135'},
    {'nombre': 'E-UPS1',     'ip': '10.44.87.133'},
    {'nombre': 'F-UPS1',     'ip': '10.44.87.123'},
    {'nombre': 'G-UPS1',     'ip': '10.44.87.131'},
    {'nombre': 'H-UPS1',     'ip': '10.44.87.132'},
    {'nombre': 'I-UPS1',     'ip': '10.44.87.119'},
    {'nombre': 'I-UPS2',     'ip': '10.44.87.120'},
    {'nombre': 'KL-UPS1',    'ip': '10.44.87.121'},
    {'nombre': 'KL-UPS2',    'ip': '10.44.87.122'},
    {'nombre': 'M-UPS1',     'ip': '10.44.87.130'},
    {'nombre': 'O-UPS1',     'ip': '10.44.87.116'},
    {'nombre': 'P-UPS1',     'ip': '10.44.87.129'},
    {'nombre': 'Q-UPS1',     'ip': '10.44.87.97'},
    {'nombre': 'Q-UPS2',     'ip': '10.44.87.98'},
    {'nombre': 'R-UPS1',     'ip': '10.44.87.99'},
    {'nombre': 'R-UPS2',     'ip': '10.44.87.100'},
    {'nombre': 'S-UPS1',     'ip': '10.44.87.125'},
    {'nombre': 'U-UPS1',     'ip': '10.44.87.128'},
    {'nombre': 'V-UPS1',     'ip': '10.44.87.124'},
    {'nombre': 'W-UPS1',     'ip': '10.44.87.118'},
    {'nombre': 'X-UPS1',     'ip': '10.44.87.126'},
]

# OID simple que responde cualquier dispositivo Eaton o Kaise
OID_PRUEBA_EATON = '1.3.6.1.4.1.534.1.8.1.0'
OID_PRUEBA_KAISE = '1.3.6.1.4.1.935.1.1.1.3.1.1.0'
OID_GENERICO     = '1.3.6.1.2.1.1.3.0'  # uptime estandar

def consulta_rapida(ups):
    """Prueba un solo OID y mide el tiempo de respuesta."""
    inicio = time.time()
    for oid in [OID_PRUEBA_EATON, OID_PRUEBA_KAISE, OID_GENERICO]:
        try:
            cmd = ['snmpget', '-v', '1', '-c', 'public',
                   '-t', '1', '-r', '1', ups['ip'], oid]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                duracion = time.time() - inicio
                return {
                    'nombre'  : ups['nombre'],
                    'ip'      : ups['ip'],
                    'estado'  : 'OK',
                    'duracion': round(duracion, 2),
                }
        except Exception:
            pass
    duracion = time.time() - inicio
    return {
        'nombre'  : ups['nombre'],
        'ip'      : ups['ip'],
        'estado'  : 'SIN RESPUESTA',
        'duracion': round(duracion, 2),
    }

def medir(workers, label):
    print(f"\n{'='*55}")
    print(f"  TEST: {label}")
    print(f"  Hilos simultaneos: {workers}")
    print(f"  UPS a consultar: {len(UPS_LIST)}")
    print(f"  Inicio: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    print(f"{'='*55}")

    inicio_total = time.time()
    resultados = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futuros = {executor.submit(consulta_rapida, ups): ups for ups in UPS_LIST}
        for futuro in as_completed(futuros):
            resultado = futuro.result()
            resultados.append(resultado)
            estado = resultado['estado']
            print(f"  {resultado['nombre']:<14} {resultado['ip']:<16} "
                  f"{estado:<15} {resultado['duracion']}s")

    total = round(time.time() - inicio_total, 2)
    ok      = [r for r in resultados if r['estado'] == 'OK']
    sin_r   = [r for r in resultados if r['estado'] == 'SIN RESPUESTA']
    mas_lento = max(resultados, key=lambda r: r['duracion'])

    print(f"\n  RESULTADO:")
    print(f"  Tiempo total      : {total}s")
    print(f"  Respondieron      : {len(ok)}/{len(UPS_LIST)}")
    print(f"  Sin respuesta     : {len(sin_r)}")
    print(f"  Mas lento         : {mas_lento['nombre']} ({mas_lento['duracion']}s)")
    print(f"  Promedio          : {round(sum(r['duracion'] for r in resultados)/len(resultados),2)}s")
    return total

# ── EJECUTAR PRUEBAS ──────────────────────────────────────
print("\n  PRUEBA DE VELOCIDAD SNMP")
print("  Mide el tiempo de consultar 1 OID por UPS con distintos")
print("  niveles de paralelismo.\n")

t10 = medir(10, "10 hilos (configuracion actual)")
time.sleep(3)
t15 = medir(15, "15 hilos")
time.sleep(3)
t29 = medir(29, "29 hilos (1 por UPS - maximo paralelismo)")

print(f"\n{'='*55}")
print(f"  COMPARATIVA FINAL")
print(f"{'='*55}")
print(f"  10 hilos : {t10}s")
print(f"  15 hilos : {t15}s")
print(f"  29 hilos : {t29}s")
print(f"  Ganancia 10->29 hilos: {round(t10-t29,2)}s menos")
print(f"{'='*55}\n")