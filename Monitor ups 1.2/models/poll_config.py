"""Configuracion del ciclo de polling SNMP."""

# Segundos entre actualizaciones. El ciclo compensa su duracion para mantener este intervalo.
POLL_INTERVAL_SEC = 10

# Hilos simultaneos para consultar UPS. 0 = un hilo por UPS en la config.
SNMP_MAX_CONCURRENT = 20
