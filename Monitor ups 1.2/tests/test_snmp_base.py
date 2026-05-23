import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.snmp.base import _limpiar_valor_snmp, _parsear_salida_snmp, snmpget_multi


class TestParseoSnmp(unittest.TestCase):
    def test_limpia_prefijos_numericos(self):
        self.assertEqual(_limpiar_valor_snmp('INTEGER: 100'), '100')
        self.assertEqual(_limpiar_valor_snmp('Gauge32: 220'), '220')
        self.assertEqual(_limpiar_valor_snmp('STRING: "9E 6000i"'), '9E 6000i')

    def test_detecta_oid_inexistente(self):
        self.assertIsNone(_limpiar_valor_snmp('No Such Object available on this agent at this OID'))

    def test_parsea_salida_multiple_en_orden(self):
        stdout = """\
.1.3.6.1.4.1.534.1.1.2.0 = STRING: "9E 6000i RT2U"
.1.3.6.1.4.1.534.1.2.1.0 = Timeticks: (5400) 0:01:30.00
.1.3.6.1.4.1.534.1.2.4.0 = INTEGER: 100
"""
        oids = [
            '1.3.6.1.4.1.534.1.1.2.0',
            '1.3.6.1.4.1.534.1.2.1.0',
            '1.3.6.1.4.1.534.1.2.4.0',
        ]
        resultado = _parsear_salida_snmp(stdout, oids)
        self.assertEqual(resultado[oids[0]], '9E 6000i RT2U')
        self.assertEqual(resultado[oids[1]], '(5400) 0:01:30.00')
        self.assertEqual(resultado[oids[2]], '100')

    def test_parsea_salida_con_nombres_mib(self):
        stdout = """\
EATON-SHUTDOWNCONTROL-MIB::upsBaseModel.0 = STRING: "9SX 20KP"
EATON-SHUTDOWNCONTROL-MIB::upsAdvBatteryRunTimeRemaining.0 = Timeticks: (1200) 0:00:12.00
"""
        oids = [
            '1.3.6.1.4.1.534.1.1.2.0',
            '1.3.6.1.4.1.534.1.2.1.0',
        ]
        resultado = _parsear_salida_snmp(stdout, oids)
        self.assertEqual(resultado[oids[0]], '9SX 20KP')
        self.assertEqual(resultado[oids[1]], '(1200) 0:00:12.00')

    def test_faltan_lineas_devuelve_none(self):
        stdout = '.1.3.6.1.4.1.534.1.1.2.0 = STRING: "modelo"'
        oids = [
            '1.3.6.1.4.1.534.1.1.2.0',
            '1.3.6.1.4.1.534.1.2.1.0',
        ]
        resultado = _parsear_salida_snmp(stdout, oids)
        self.assertEqual(resultado[oids[0]], 'modelo')
        self.assertIsNone(resultado[oids[1]])


class TestSnmpgetMulti(unittest.TestCase):
    @patch('models.snmp.base.subprocess.run')
    def test_dispositivo_sin_respuesta(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ''
        oids = ['1.3.6.1.4.1.534.1.1.2.0']
        resultado = snmpget_multi('10.0.0.1', 'public', '1', oids)
        self.assertEqual(resultado, {oids[0]: None})

    @patch('models.snmp.base.subprocess.run')
    def test_un_solo_comando_para_varios_oids(self, mock_run):
        oids = [
            '1.3.6.1.4.1.534.1.1.2.0',
            '1.3.6.1.4.1.534.1.2.4.0',
        ]
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = (
            '.1.3.6.1.4.1.534.1.1.2.0 = STRING: "modelo"\n'
            '.1.3.6.1.4.1.534.1.2.4.0 = INTEGER: 95\n'
        )

        resultado = snmpget_multi('10.0.0.1', 'public', '1', oids)

        cmd = mock_run.call_args.args[0]
        self.assertEqual(cmd.count('10.0.0.1'), 1)
        self.assertEqual(cmd[-2:], oids)
        self.assertEqual(resultado[oids[0]], 'modelo')
        self.assertEqual(resultado[oids[1]], '95')


if __name__ == '__main__':
    unittest.main()
