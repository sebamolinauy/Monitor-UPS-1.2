const UMBRAL_VOLTAJE_MIN = 200;
const UMBRAL_BATERIA_MIN = 30;
const UMBRAL_CARGA_MAX   = 40;

// ── VISTAS ────────────────────────────────────────────────
function mostrarVista(v, btn) {
  document.querySelectorAll('.view').forEach(e => e.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(e => e.classList.remove('active'));
  document.getElementById('view-' + v).classList.add('active');
  btn.classList.add('active');
  if (v === 'historial') cargarListaHistorial();
  if (v === 'admin')     cargarTablaAdmin();
}

// ── SONIDO ────────────────────────────────────────────────
function sonarAlarma(nivel) {
  try {
    const ctx   = new (window.AudioContext || window.webkitAudioContext)();
    const notas = nivel === 'falla' ? [880, 660, 880, 660] : [660, 880];
    let t = ctx.currentTime;
    notas.forEach(freq => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.connect(g); g.connect(ctx.destination);
      o.frequency.value = freq;
      o.type = nivel === 'falla' ? 'sawtooth' : 'sine';
      g.gain.setValueAtTime(0.3, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
      o.start(t); o.stop(t + 0.3); t += 0.35;
    });
  } catch(e) {}
}

// ── ALERTAS ───────────────────────────────────────────────
let alertasActuales = [];
const popupsActivos = new Set();

function actualizarPestanaAlertas(alertas) {
  const tabAlertas = document.getElementById('tab-alertas');
  const contenido  = document.getElementById('alertas-contenido');

  // Detectar alertas nuevas para sonar
  const keysAnteriores = new Set(alertasActuales.map(a => a.ups + '|' + a.estado));
  const nuevas = alertas.filter(a => !keysAnteriores.has(a.ups + '|' + a.estado));
  if (nuevas.length > 0) {
    sonarAlarma(nuevas.some(a => a.nivel === 'falla') ? 'falla' : 'advertencia');
  }
  alertasActuales = alertas;

  // Pestaña: rojo pulsante si hay alertas
  if (alertas.length > 0) {
    tabAlertas.classList.add('alerta-activa');
    tabAlertas.textContent = '⚠ Alertas (' + alertas.length + ')';
  } else {
    tabAlertas.classList.remove('alerta-activa');
    tabAlertas.textContent = '⚠ Alertas';
  }

  // Lista en la vista alertas
  if (alertas.length === 0) {
    contenido.innerHTML = '<p class="alerta-vacia">&#10003; Sin alertas activas. Todos los UPS funcionan correctamente.</p>';
    actualizarPopups([]);
    return;
  }

  let html = '';
  alertas.forEach(a => {
    const esFalla = a.nivel === 'falla';
    html += `<div class="alerta-fila ${esFalla ? '' : 'advertencia'}">
      <span class="alerta-icono">${esFalla ? '&#128308;' : '&#128992;'}</span>
      <div class="alerta-info">
        <strong>${a.ups} &mdash; Sala ${a.sala}</strong>
        <span>${a.estado}</span>
      </div>
      <span class="alerta-nivel ${esFalla ? 'nivel-falla' : 'nivel-advertencia'}">
        ${esFalla ? 'ALARMA' : 'ADVERTENCIA'}
      </span>
      <span class="alerta-hora-txt">${a.hora}</span>
    </div>`;
  });
  contenido.innerHTML = html;
  actualizarPopups(alertas);
}

function actualizarPopups(alertas) {
  const overlay = document.getElementById('alerta-overlay');
  const keys    = new Set(alertas.map(a => a.ups + '|' + a.estado));

  // Eliminar popups cuya alerta ya no existe
  popupsActivos.forEach(key => {
    if (!keys.has(key)) {
      const el = overlay.querySelector(`[data-key="${CSS.escape(key)}"]`);
      if (el) el.remove();
      popupsActivos.delete(key);
    }
  });

  // Agregar popups nuevos
  alertas.forEach(a => {
    const key = a.ups + '|' + a.estado;
    if (popupsActivos.has(key)) return;
    popupsActivos.add(key);
    const div = document.createElement('div');
    div.className = 'alerta-popup' + (a.nivel === 'falla' ? ' falla' : '');
    div.setAttribute('data-key', key);
    div.innerHTML = `
      <div class="alerta-ph">
        <span class="alerta-titulo">&#9888; ${a.nivel === 'falla' ? 'ALARMA' : 'ADVERTENCIA'}</span>
        <button class="alerta-cerrar" onclick="cerrarPopup(this,'${key}')">&#215;</button>
      </div>
      <div class="alerta-pbody"><strong>${a.ups}</strong> &mdash; Sala ${a.sala}<br>${a.estado}</div>
      <div class="alerta-phora">${a.hora}</div>`;
    overlay.appendChild(div);
  });
}

function cerrarPopup(btn, key) {
  btn.closest('.alerta-popup').remove();
  popupsActivos.delete(key);
}

// ── DASHBOARD ─────────────────────────────────────────────
function nivelCard(u) {
  if (u.estado === 'Sin soporte')   return 'nsoporte';
  if (u.estado === 'Sin respuesta') return 'rojo';
  if (['En bateria','Falla','Bypass','Apagando'].includes(u.estado)) return 'rojo';
  if (u.voltaje_entrada !== null && u.voltaje_entrada < UMBRAL_VOLTAJE_MIN) return 'rojo';
  if (u.bateria_pct     !== null && u.bateria_pct     < UMBRAL_BATERIA_MIN) return 'rojo';
  if (u.carga_pct       !== null && u.carga_pct       > UMBRAL_CARGA_MAX)   return 'naranja';
  return 'ok';
}

function badgeInfo(nivel, u) {
  if (nivel === 'nsoporte') return { cls: 'badge-sin', txt: 'N/A' };
  if (nivel === 'rojo') {
    if (u.estado === 'Sin respuesta')            return { cls: 'badge-rojo', txt: 'DESCONECTADA' };
    if (u.estado === 'En bateria')               return { cls: 'badge-rojo', txt: 'EN BATERIA' };
    if (['Falla','Bypass'].includes(u.estado))   return { cls: 'badge-rojo', txt: u.estado.toUpperCase() };
    if (u.voltaje_entrada !== null && u.voltaje_entrada < UMBRAL_VOLTAJE_MIN)
      return { cls: 'badge-rojo', txt: 'V.ENTRADA BAJO' };
    if (u.bateria_pct !== null && u.bateria_pct < UMBRAL_BATERIA_MIN)
      return { cls: 'badge-rojo', txt: 'BAT. CRITICA' };
    return { cls: 'badge-rojo', txt: 'ALARMA' };
  }
  if (nivel === 'naranja') return { cls: 'badge-naranja', txt: 'CARGA ALTA' };
  return { cls: 'badge-ok', txt: 'EN LINEA' };
}

function colorBat(v) {
  return v === null ? '#555' : v < UMBRAL_BATERIA_MIN ? '#f44336' : v < 50 ? '#ff9800' : '#4caf50';
}

function metrica(label, valor, unidad, nivel) {
  const txt = valor !== null && valor !== undefined ? valor + (unidad || '') : '---';
  const cls = nivel === 'rojo' ? 'rojo' : nivel === 'naranja' ? 'naranja' : '';
  return `<div class="metrica">
    <div class="metrica-label">${label}</div>
    <div class="metrica-valor ${cls}">${txt}</div>
  </div>`;
}

function renderCard(u) {
  const nivel = nivelCard(u);
  const { cls: badgeCls, txt: badgeTxt } = badgeInfo(nivel, u);
  const batPct  = u.bateria_pct !== null ? u.bateria_pct : 0;
  const nvVin   = (u.voltaje_entrada !== null && u.voltaje_entrada < UMBRAL_VOLTAJE_MIN) ? 'rojo' : '';
  const nvBat   = (u.bateria_pct !== null && u.bateria_pct < UMBRAL_BATERIA_MIN) ? 'rojo' : '';
  const nvCarga = (u.carga_pct !== null && u.carga_pct > UMBRAL_CARGA_MAX) ? 'naranja' : '';
  const autoTxt = u.autonomia_min !== null ? u.autonomia_min + ' min' : '---';

  const badgeEl = (nivel === 'ok' || nivel === 'naranja')
    ? `<a class="card-badge ${badgeCls}" href="http://${u.ip}" target="_blank"
          title="Abrir interfaz web">${badgeTxt} &#8599;</a>`
    : `<div class="card-badge ${badgeCls}">${badgeTxt}</div>`;

  return `<div class="card ${nivel}">
    <div class="card-header">
      <div class="card-nombre">${u.nombre}</div>${badgeEl}
    </div>
    <div class="card-sub">${u.marca.toUpperCase()} ${u.modelo} &mdash; ${u.ip}</div>
    <div class="metricas">
      ${metrica('V.Entrada', u.voltaje_entrada, 'V',   nvVin)}
      ${metrica('V.Salida',  u.voltaje_salida,  'V',   '')}
      ${metrica('Bateria',   u.bateria_pct,     '%',   nvBat)}
      ${metrica('Carga',     u.carga_pct,       '%',   nvCarga)}
      ${metrica('Temp',      u.temperatura,     '°C',  '')}
      <div class="metrica">
        <div class="metrica-label">Autonomia</div>
        <div class="metrica-valor">${autoTxt}</div>
      </div>
    </div>
    <div class="barra-bat">
      <div class="barra-fill"
           style="width:${batPct}%;background:${colorBat(u.bateria_pct)}">
      </div>
    </div>
    <div class="ip-tag">${u.ubicacion}</div>
  </div>`;
}

async function actualizar() {
  try {
    const r = await fetch('/api/datos');
    const d = await r.json();
    document.getElementById('tiempo').textContent = 'Act: ' + (d.ultima_actualizacion || '...');
    const ups = d.datos || [];

    document.getElementById('cnt-total').textContent  = ' ' + ups.length;
    document.getElementById('cnt-ok').textContent     = ' ' + ups.filter(u => nivelCard(u) === 'ok').length;
    document.getElementById('cnt-alerta').textContent = ' ' + ups.filter(u => nivelCard(u) === 'naranja').length;
    document.getElementById('cnt-falla').textContent  = ' ' + ups.filter(u => nivelCard(u) === 'rojo').length;
    document.getElementById('cnt-sin').textContent    = ' ' + ups.filter(u => u.estado === 'Sin respuesta').length;

    const salas = {};
    ups.forEach(u => {
      if (!salas[u.sala]) salas[u.sala] = [];
      salas[u.sala].push(u);
    });

    let html = '';
    for (const sala of Object.keys(salas)) {
      html += `<div class="sala-titulo">Sala ${sala} &mdash; ${salas[sala][0].ubicacion}</div>
               <div class="grid">`;
      salas[sala].forEach(u => html += renderCard(u));
      html += '</div>';
    }
    document.getElementById('contenido').innerHTML = html;
    actualizarPestanaAlertas(d.alertas_activas || []);
  } catch(e) {
    document.getElementById('tiempo').textContent = 'Error de conexion';
  }
}

actualizar();
setInterval(actualizar, 10000);

// ── HISTORIAL ─────────────────────────────────────────────
async function cargarListaHistorial() {
  const sel = document.getElementById('hist-select');
  if (sel.options.length > 1) return;
  const archivos = await (await fetch('/api/historial/lista')).json();
  archivos.forEach(f => {
    const o = document.createElement('option');
    o.value = f;
    o.textContent = f.replace('historial_', '').replace('.xlsx', '');
    sel.appendChild(o);
  });
}

async function cargarHistorial() {
  const archivo = document.getElementById('hist-select').value;
  const wrap    = document.getElementById('hist-tabla-wrap');
  const btnDl   = document.getElementById('btn-descargar');
  if (!archivo) {
    wrap.innerHTML = '<p class="hist-vacio">Selecciona una semana.</p>';
    btnDl.classList.add('hidden');
    return;
  }
  wrap.innerHTML = '<p class="hist-vacio">Cargando...</p>';
  const d = await (await fetch('/api/historial/datos?archivo=' + encodeURIComponent(archivo))).json();
  if (!d.filas || !d.filas.length) {
    wrap.innerHTML = '<p class="hist-vacio">Sin datos para esta semana.</p>';
    return;
  }
  let html = '<table id="hist-tabla"><thead><tr>';
  d.cabeceras.forEach(c => html += `<th>${c}</th>`);
  html += '</tr></thead><tbody>';
  d.filas.forEach(f => {
    const e   = f[6] || '';
    const cls = ['Falla','Bypass','En bateria','Sin respuesta'].includes(e) ? 'tr-rojo' : '';
    html += `<tr class="${cls}">`;
    f.forEach(v => html += `<td>${v != null ? v : ''}</td>`);
    html += '</tr>';
  });
  html += '</tbody></table>';
  wrap.innerHTML = html;
  btnDl.href = '/api/historial/descargar?archivo=' + encodeURIComponent(archivo);
  btnDl.classList.remove('hidden');
}

// ── ADMIN ─────────────────────────────────────────────────
let upsData = [];

async function cargarTablaAdmin() {
  upsData = await (await fetch('/api/config')).json();
  renderTablaAdmin();
}

function renderTablaAdmin() {
  const buscar = document.getElementById('admin-buscar').value.toLowerCase();
  const tbody  = document.getElementById('admin-tbody');
  tbody.innerHTML = '';
  let n = 0;
  upsData.forEach((u, i) => {
    if (buscar && !(u.nombre+u.ip+u.sala+u.ubicacion+u.marca+u.modelo).toLowerCase().includes(buscar)) return;
    n++;
    const mc = u.marca === 'eaton' ? 'marca-eaton' : u.marca === 'kaise' ? 'marca-kaise' : 'marca-otro';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="color:#444;font-size:11px">${i+1}</td>
      <td><strong style="color:#ddd">${u.nombre}</strong></td>
      <td>${u.sala}</td>
      <td style="color:#888">${u.ubicacion}</td>
      <td style="font-family:monospace;font-size:11px;color:#6abf69">${u.ip}</td>
      <td><span class="marca-pill ${mc}">${u.marca.toUpperCase()}</span></td>
      <td style="color:#aaa">${u.modelo}</td>
      <td style="font-size:11px;color:#555">${u.community}</td>
      <td><button class="btn-icon" title="Editar" onclick="abrirModal(${i})">&#9998;</button></td>`;
    tbody.appendChild(tr);
  });
  document.getElementById('admin-total').textContent = `${n} de ${upsData.length} UPS`;
}

function abrirModal(idx) {
  const esEdicion = idx !== undefined;
  document.getElementById('edit-index').value = esEdicion ? idx : -1;
  document.getElementById('modal-titulo').textContent = esEdicion ? 'Editar UPS' : 'Agregar UPS';
  document.getElementById('btn-eliminar').classList.toggle('hidden', !esEdicion);
  document.getElementById('test-resultado').style.display = 'none';
  if (esEdicion) {
    const u = upsData[idx];
    document.getElementById('f-nombre').value    = u.nombre;
    document.getElementById('f-ip').value        = u.ip;
    document.getElementById('f-sala').value      = u.sala;
    document.getElementById('f-ubicacion').value = u.ubicacion;
    document.getElementById('f-marca').value     = u.marca;
    document.getElementById('f-modelo').value    = u.modelo;
    document.getElementById('f-community').value = u.community;
  } else {
    ['f-nombre','f-ip','f-sala','f-ubicacion','f-modelo'].forEach(
      id => document.getElementById(id).value = ''
    );
    document.getElementById('f-marca').value     = 'eaton';
    document.getElementById('f-community').value = 'public';
  }
  document.getElementById('modal-bg').classList.remove('hidden');
}

function cerrarModal() {
  document.getElementById('modal-bg').classList.add('hidden');
}

async function probarConexion() {
  const ip  = document.getElementById('f-ip').value.trim();
  const com = document.getElementById('f-community').value.trim() || 'public';
  if (!ip) { alert('Ingresa una IP primero'); return; }
  const res  = document.getElementById('test-resultado');
  const spin = document.getElementById('test-spin');
  res.style.display = 'none';
  spin.classList.remove('hidden');
  try {
    const d = await (await fetch(`/api/test_snmp?ip=${encodeURIComponent(ip)}&community=${encodeURIComponent(com)}`)).json();
    res.className   = d.ok ? 'ok' : 'err';
    res.textContent = d.ok
      ? `Conexion OK: ${d.descripcion} (SNMPv${d.version})`
      : `Sin respuesta: ${d.descripcion}`;
    res.style.display = 'block';
  } catch(e) {
    res.className = 'err';
    res.textContent = 'Error de red';
    res.style.display = 'block';
  }
  spin.classList.add('hidden');
}

async function guardarUPS() {
  const idx = parseInt(document.getElementById('edit-index').value);
  const u = {
    nombre   : document.getElementById('f-nombre').value.trim(),
    ip       : document.getElementById('f-ip').value.trim(),
    sala     : document.getElementById('f-sala').value.trim(),
    ubicacion: document.getElementById('f-ubicacion').value.trim(),
    marca    : document.getElementById('f-marca').value,
    modelo   : document.getElementById('f-modelo').value.trim() || document.getElementById('f-marca').value,
    community: document.getElementById('f-community').value.trim() || 'public',
  };
  if (!u.nombre || !u.ip || !u.sala || !u.ubicacion) {
    alert('Completar los campos obligatorios (*)');
    return;
  }
  if (idx >= 0) upsData[idx] = u; else upsData.push(u);
  await fetch('/api/config', {
    method : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body   : JSON.stringify(upsData),
  });
  cerrarModal();
  cargarTablaAdmin();
}

async function eliminarUPS() {
  const idx = parseInt(document.getElementById('edit-index').value);
  if (idx < 0) return;
  if (!confirm(`Eliminar "${upsData[idx].nombre}" (${upsData[idx].ip})?`)) return;
  upsData.splice(idx, 1);
  await fetch('/api/config', {
    method : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body   : JSON.stringify(upsData),
  });
  cerrarModal();
  cargarTablaAdmin();
}