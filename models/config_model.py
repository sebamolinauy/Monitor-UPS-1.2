import json
import os

CONFIG_FILE = 'ups_config.json'

UPS_DEFAULT = [
    {'ip': '10.44.87.95',  'nombre': 'A-G1-UPS1', 'sala': 'A',     'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9E6Ki',          'community': 'public'},
    {'ip': '10.44.87.96',  'nombre': 'A-G1-UPS2', 'sala': 'A',     'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9E6Ki',          'community': 'public'},
    {'ip': '10.44.87.137', 'nombre': 'A-G2-UPS1', 'sala': 'A',     'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9E10Ki',         'community': 'public'},
    {'ip': '10.44.87.138', 'nombre': 'A-G3-UPS1', 'sala': 'A',     'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9E10Ki',         'community': 'public'},
    {'ip': '10.44.87.139', 'nombre': 'A-G3-UPS2', 'sala': 'A',     'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9E10Ki',         'community': 'public'},
    {'ip': '10.44.87.93',  'nombre': 'BC-UPS1',   'sala': 'B y C', 'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9E10Ki',         'community': 'public'},
    {'ip': '10.44.87.94',  'nombre': 'BC-UPS2',   'sala': 'B y C', 'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9E10Ki',         'community': 'public'},
    {'ip': '10.44.87.136', 'nombre': 'D-UPS1',    'sala': 'D',     'ubicacion': 'Terminal PA',        'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.135', 'nombre': 'D-UPS2',    'sala': 'D',     'ubicacion': 'Terminal PA',        'marca': 'eaton', 'modelo': '9PX 1500IRT2U', 'community': 'public'},
    {'ip': '10.44.87.133', 'nombre': 'E-UPS1',    'sala': 'E',     'ubicacion': 'Terminal PA',        'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.123', 'nombre': 'F-UPS1',    'sala': 'F',     'ubicacion': 'Parking',            'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.131', 'nombre': 'G-UPS1',    'sala': 'G',     'ubicacion': 'Sala de Tableros C', 'marca': 'inform','modelo': 'desconocido',    'community': 'public'},
    {'ip': '10.44.87.132', 'nombre': 'H-UPS1',    'sala': 'H',     'ubicacion': 'Sala de Tableros D', 'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.119', 'nombre': 'I-UPS1',    'sala': 'I',     'ubicacion': 'Local 213',          'marca': 'eaton', 'modelo': '9E10Ki',         'community': 'public'},
    {'ip': '10.44.87.120', 'nombre': 'I-UPS2',    'sala': 'I',     'ubicacion': 'Local 213',          'marca': 'eaton', 'modelo': '9E10Ki',         'community': 'public'},
    {'ip': '10.44.87.121', 'nombre': 'KL-UPS1',   'sala': 'K y L', 'ubicacion': 'TAG (TGBT)',         'marca': 'eaton', 'modelo': '9SX 20KP',       'community': 'public'},
    {'ip': '10.44.87.122', 'nombre': 'KL-UPS2',   'sala': 'K y L', 'ubicacion': 'TAG (TGBT)',         'marca': 'eaton', 'modelo': '9SX 20KP',       'community': 'public'},
    {'ip': '10.44.87.130', 'nombre': 'M-UPS1',    'sala': 'M',     'ubicacion': 'PTE',                'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.116', 'nombre': 'O-UPS1',    'sala': 'O',     'ubicacion': 'FEC 08-26',          'marca': 'eaton', 'modelo': '9PX30000IRT2U', 'community': 'public'},
    {'ip': '10.44.87.129', 'nombre': 'P-UPS1',    'sala': 'P',     'ubicacion': 'Dep. residuos',      'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.97',  'nombre': 'Q-UPS1',    'sala': 'Q',     'ubicacion': 'FEC 01-19',          'marca': 'eaton', 'modelo': '9E6Ki',          'community': 'public'},
    {'ip': '10.44.87.98',  'nombre': 'Q-UPS2',    'sala': 'Q',     'ubicacion': 'FEC 01-19',          'marca': 'eaton', 'modelo': '9E6Ki',          'community': 'public'},
    {'ip': '10.44.87.99',  'nombre': 'R-UPS1',    'sala': 'R',     'ubicacion': 'SS TWR',             'marca': 'eaton', 'modelo': '9E6Ki',          'community': 'public'},
    {'ip': '10.44.87.100', 'nombre': 'R-UPS2',    'sala': 'R',     'ubicacion': 'SS TWR',             'marca': 'eaton', 'modelo': '9E6Ki',          'community': 'public'},
    {'ip': '10.44.87.125', 'nombre': 'S-UPS1',    'sala': 'S',     'ubicacion': 'EMA INUMET',         'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.128', 'nombre': 'U-UPS1',    'sala': 'U',     'ubicacion': 'Bomberos',           'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.124', 'nombre': 'V-UPS1',    'sala': 'V',     'ubicacion': 'AWOS IMS',           'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.118', 'nombre': 'W-UPS1',    'sala': 'W',     'ubicacion': 'VOR-DME',            'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
    {'ip': '10.44.87.126', 'nombre': 'X-UPS1',    'sala': 'X',     'ubicacion': 'DF',                 'marca': 'kaise', 'modelo': 'KUKs-RT03',      'community': 'public'},
]

def cargar_config() -> list[dict]:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    guardar_config(UPS_DEFAULT)
    return UPS_DEFAULT

def guardar_config(lista: list[dict]) -> None:
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)