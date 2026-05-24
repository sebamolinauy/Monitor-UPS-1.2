import time
import threading
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse

from controllers.ups_controller import get_cache, iniciar_ciclo, probar_conexion
from controllers.config_controller import guardar_lista_completa, listar_ups
from controllers.historial_controller import (
    get_lista_historiales,
    get_datos_historial,
    get_ruta_descarga,
)

app = FastAPI(title="Monitor UPS", version="2.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    def arrancar():
        time.sleep(15)
        iniciar_ciclo()
    threading.Thread(target=arrancar, daemon=True).start()

@app.get("/")
async def dashboard():
    return FileResponse("templates/index.html")

@app.get("/api/datos")
async def api_datos():
    return get_cache()

@app.get("/api/config")
async def api_get_config():
    return listar_ups()

@app.post("/api/config")
async def api_guardar_config(lista: list[dict]):
    return guardar_lista_completa(lista)

@app.get("/api/test_snmp")
async def api_test_snmp(ip: str, community: str = "public"):
    return probar_conexion(ip, community)

@app.get("/api/historial/lista")
async def api_historial_lista():
    return get_lista_historiales()

@app.get("/api/historial/datos")
async def api_historial_datos(archivo: str):
    return get_datos_historial(archivo)

@app.get("/api/historial/descargar")
async def api_historial_descargar(archivo: str):
    ruta = get_ruta_descarga(archivo)
    if not ruta:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(
        path=ruta,
        filename=archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )