"use strict";

// Estado en memoria de la página: registro, agente elegido y conversaciones.
const estado = {
  agentes: [],
  seleccionado: null,
  conversaciones: new Map(), // clave -> { contextId, mensajes: [] }
  enviando: new Set(), // claves de agentes con una petición en curso
};

const listaAgentes = document.getElementById("lista-agentes");
const avisoRegistro = document.getElementById("aviso-registro");
const campo = document.getElementById("campo");
const botonEnviar = document.getElementById("enviar");
const contenedorMensajes = document.getElementById("mensajes");

/** Identificador de conversación: el agente lo usa como memoria del hilo. */
function nuevoContexto() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return `ctx-${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`;
}

/** Devuelve (y crea si hace falta) la conversación de un agente. */
function conversacion(clave) {
  if (!estado.conversaciones.has(clave)) {
    estado.conversaciones.set(clave, { contextId: nuevoContexto(), mensajes: [] });
  }
  return estado.conversaciones.get(clave);
}

/** Deja cualquier error en un solo renglón, sin stack trace. */
function mensajeError(error) {
  if (error instanceof TypeError) {
    return "No se pudo conectar con la consola web.";
  }
  const texto = String((error && error.message) || error || "Error desconocido");
  return texto.replace(/\s+/g, " ").trim();
}

/** Saca un texto legible del "detail" que devuelve FastAPI. */
function detalleDeError(datos, respuesta) {
  if (datos && typeof datos.detail === "string") {
    return datos.detail;
  }
  if (datos && Array.isArray(datos.detail) && datos.detail.length > 0) {
    const primero = datos.detail[0];
    if (typeof primero === "string") {
      return primero;
    }
    if (primero && typeof primero.msg === "string") {
      return primero.msg.replace(/^Value error,\s*/i, "");
    }
  }
  return `La consola respondió HTTP ${respuesta.status}.`;
}

/** Etiqueta de estado de cada agente: implementado, en línea o sin conexión. */
function estadoAgente(agente) {
  if (!agente.disponible) {
    return { clase: "etiqueta-pendiente", texto: "Pendiente" };
  }
  if (agente.en_linea) {
    return { clase: "etiqueta-lista", texto: "En línea" };
  }
  return { clase: "etiqueta-fuera", texto: "Sin conexión" };
}

function mostrarAviso(texto) {
  avisoRegistro.textContent = texto;
  avisoRegistro.hidden = false;
}

/** Clave de agente que viene en la URL, por ejemplo #viajes. */
function claveEnUrl() {
  return decodeURIComponent(window.location.hash.replace(/^#/, "")).trim();
}

/* ---------- Registro de agentes ---------- */

async function cargarAgentes() {
  avisoRegistro.hidden = true;
  try {
    const respuesta = await fetch("/api/agentes", {
      headers: { Accept: "application/json" },
    });
    if (!respuesta.ok) {
      throw new Error(`La consola respondió HTTP ${respuesta.status}.`);
    }
    estado.agentes = await respuesta.json();
    pintarAgentes();

    if (estado.seleccionado) {
      const actual = estado.agentes.find(
        (agente) => agente.clave === estado.seleccionado.clave
      );
      if (actual) {
        seleccionar(actual);
      } else {
        limpiarSeleccion();
      }
    } else {
      const pedido = estado.agentes.find(
        (agente) => agente.clave === claveEnUrl()
      );
      if (pedido) {
        seleccionar(pedido);
      }
    }
  } catch (error) {
    mostrarAviso(`No se pudo cargar el registro: ${mensajeError(error)}`);
  }
}

/** Texto que aparece al pasar el mouse por encima de un agente. */
function tituloAgente(agente) {
  if (!agente.disponible) {
    return `${agente.nombre} todavía no tiene servidor A2A`;
  }
  if (agente.en_linea) {
    return `Conversar con ${agente.nombre}`;
  }
  return `${agente.nombre} está implementado, pero su servidor no responde`;
}

function pintarAgentes() {
  listaAgentes.replaceChildren();
  document.getElementById("contador").textContent = String(estado.agentes.length);

  for (const agente of estado.agentes) {
    const item = document.createElement("li");
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "agente";
    boton.dataset.clave = agente.clave;
    boton.title = tituloAgente(agente);
    if (estado.seleccionado && estado.seleccionado.clave === agente.clave) {
      boton.classList.add("activo");
    }
    boton.addEventListener("click", () => seleccionar(agente));

    const fila = document.createElement("span");
    fila.className = "agente-fila";

    const nombre = document.createElement("span");
    nombre.className = "agente-nombre";
    nombre.textContent = agente.nombre;

    const etiqueta = document.createElement("span");
    const situacion = estadoAgente(agente);
    etiqueta.className = `etiqueta ${situacion.clase}`;
    etiqueta.textContent = situacion.texto;

    fila.append(nombre, etiqueta);

    const descripcion = document.createElement("span");
    descripcion.className = "agente-descripcion";
    descripcion.textContent = agente.descripcion;

    const url = document.createElement("span");
    url.className = "agente-url";
    url.textContent = `${agente.url} · ${agente.metodo}`;

    boton.append(fila, descripcion, url);
    item.append(boton);
    listaAgentes.append(item);
  }
}

/* ---------- Estado en vivo ---------- */

/**
 * Vuelve a preguntar por el registro y actualiza solo las etiquetas de estado.
 * No repinta la lista, no borra el chat y no mueve el foco, así que puede
 * correr cada pocos segundos sin molestar mientras se escribe.
 */
async function refrescarEstado() {
  try {
    const respuesta = await fetch("/api/agentes", {
      headers: { Accept: "application/json" },
    });
    if (!respuesta.ok) {
      return;
    }
    estado.agentes = await respuesta.json();
    if (estado.seleccionado) {
      const actual = estado.agentes.find(
        (agente) => agente.clave === estado.seleccionado.clave
      );
      if (actual) {
        // Si la ficha cambió (el servidor recién arrancó, por ejemplo), repintarla.
        const cambio =
          JSON.stringify(actual.ficha) !==
          JSON.stringify(estado.seleccionado.ficha);
        estado.seleccionado = actual;
        if (cambio) {
          pintarFicha();
        }
      }
    }
    pintarEstado();
  } catch (error) {
    // En silencio a propósito: un fallo de red no debe llenar la página de avisos.
  }
}

/** Repinta la etiqueta y el título de los botones que ya están dibujados. */
function pintarEstado() {
  for (const boton of listaAgentes.querySelectorAll(".agente")) {
    const agente = estado.agentes.find(
      (candidato) => candidato.clave === boton.dataset.clave
    );
    if (!agente) {
      continue;
    }
    const situacion = estadoAgente(agente);
    const etiqueta = boton.querySelector(".etiqueta");
    if (etiqueta) {
      etiqueta.className = `etiqueta ${situacion.clase}`;
      etiqueta.textContent = situacion.texto;
    }
    boton.title = tituloAgente(agente);
  }
}

/* ---------- Selección ---------- */

function seleccionar(agente) {
  estado.seleccionado = agente;
  history.replaceState(null, "", `#${encodeURIComponent(agente.clave)}`);

  for (const boton of listaAgentes.querySelectorAll(".agente")) {
    boton.classList.toggle("activo", boton.dataset.clave === agente.clave);
  }

  document.getElementById("sin-seleccion").hidden = true;
  document.getElementById("chat").hidden = false;
  document.getElementById("chat-nombre").textContent = agente.nombre;
  document.getElementById("chat-destino").textContent =
    `POST ${agente.url} · ${agente.metodo}`;

  actualizarPie();
  actualizarCompositor();
  pintarFicha();
  pintarMensajes();

  if (agente.disponible) {
    campo.focus();
  }
}

function limpiarSeleccion() {
  estado.seleccionado = null;
  history.replaceState(null, "", window.location.pathname);
  document.getElementById("ficha").hidden = true;
  document.getElementById("chat").hidden = true;
  document.getElementById("sin-seleccion").hidden = false;
}

function actualizarPie() {
  const agente = estado.seleccionado;
  if (!agente) {
    return;
  }
  const conv = conversacion(agente.clave);
  document.getElementById("pie-contexto").textContent =
    `context_id: ${conv.contextId}`;
}

/* ---------- Ficha A2A ---------- */

function agregarDato(contenedor, texto, clase = "ficha-dato") {
  const dato = document.createElement("span");
  dato.className = clase;
  dato.textContent = texto;
  contenedor.append(dato);
}

/** Pinta la Agent Card que publica el agente (versión, protocolo y skills). */
function pintarFicha() {
  const contenedor = document.getElementById("ficha");
  const datos = document.getElementById("ficha-datos");
  const habilidades = document.getElementById("ficha-skills");
  const aviso = document.getElementById("ficha-aviso");
  const agente = estado.seleccionado;
  const ficha = agente && agente.ficha;

  datos.replaceChildren();
  habilidades.replaceChildren();
  aviso.hidden = true;
  aviso.textContent = "";

  if (!ficha) {
    // Sin ficha solo se avisa si el servidor está en línea: no publica la card.
    const enLinea = Boolean(agente && agente.en_linea);
    contenedor.hidden = !enLinea;
    if (!enLinea) {
      return;
    }
    habilidades.hidden = true;
    agregarDato(datos, "sin Agent Card publicada", "ficha-dato ficha-dato-alerta");
    aviso.hidden = false;
    aviso.textContent =
      "Este agente está en línea pero no publica " +
      "/.well-known/agent-card.json.";
    return;
  }

  contenedor.hidden = false;

  if (ficha.version) {
    agregarDato(datos, `v${ficha.version}`);
  }
  if (ficha.interfaz && ficha.interfaz.protocolo) {
    agregarDato(
      datos,
      `${ficha.interfaz.protocolo} ${ficha.interfaz.version_protocolo}`.trim()
    );
  }
  agregarDato(datos, ficha.streaming ? "con streaming" : "sin streaming");
  if (ficha.modos_salida.length > 0) {
    agregarDato(datos, `salida: ${ficha.modos_salida.join(", ")}`);
  }

  habilidades.hidden = ficha.habilidades.length === 0;

  for (const habilidad of ficha.habilidades) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = habilidad.nombre || habilidad.id;
    chip.title = habilidad.ejemplos[0]
      ? `${habilidad.descripcion} · Ejemplo: ${habilidad.ejemplos[0]}`
      : habilidad.descripcion;
    chip.addEventListener("click", () => usarEjemplo(habilidad));
    habilidades.append(chip);
  }

  aviso.hidden = !agente.aviso_url;
  aviso.textContent = agente.aviso_url || "";
}

/** Deja el ejemplo de una skill en la caja de texto, listo para mandarlo. */
function usarEjemplo(habilidad) {
  const agente = estado.seleccionado;
  if (!agente || !agente.disponible || estado.enviando.has(agente.clave)) {
    return;
  }
  const ejemplo = habilidad.ejemplos[0];
  if (!ejemplo) {
    return;
  }
  campo.value = ejemplo;
  ajustarAltura();
  campo.focus();
  campo.setSelectionRange(ejemplo.length, ejemplo.length);
}

/* ---------- Mensajes ---------- */

function burbuja(rol, texto, extra = {}) {
  const fila = document.createElement("div");
  fila.className = `mensaje mensaje-${rol}`;

  const cuerpo = document.createElement("div");
  cuerpo.className = "burbuja";
  cuerpo.textContent = texto;
  fila.append(cuerpo);

  if (rol === "agente" && typeof extra.latencia_ms === "number") {
    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = `${(extra.latencia_ms / 1000).toFixed(1)} s`;
    fila.append(meta);
  }

  return fila;
}

function burbujaPensando() {
  const fila = document.createElement("div");
  fila.className = "mensaje mensaje-agente";
  const cuerpo = document.createElement("div");
  cuerpo.className = "burbuja";
  const puntos = document.createElement("span");
  puntos.className = "pensando";
  puntos.setAttribute("aria-label", "El agente está pensando");
  for (let i = 0; i < 3; i += 1) {
    puntos.append(document.createElement("span"));
  }
  cuerpo.append(puntos);
  fila.append(cuerpo);
  return fila;
}

function pintarMensajes() {
  const agente = estado.seleccionado;
  if (!agente) {
    return;
  }

  const conv = conversacion(agente.clave);
  contenedorMensajes.replaceChildren();

  if (!agente.disponible) {
    contenedorMensajes.append(
      burbuja(
        "sistema",
        "Este agente todavía no está implementado. Cuando tenga su servidor A2A, " +
          "podrás conversar con él desde aquí."
      )
    );
  } else if (conv.mensajes.length === 0) {
    contenedorMensajes.append(
      burbuja(
        "sistema",
        `Escríbele a ${agente.nombre}. La conversación se recuerda por context_id.`
      )
    );
  }

  for (const mensaje of conv.mensajes) {
    contenedorMensajes.append(
      burbuja(mensaje.rol, mensaje.texto, mensaje)
    );
  }

  if (estado.enviando.has(agente.clave)) {
    contenedorMensajes.append(burbujaPensando());
  }

  contenedorMensajes.scrollTop = contenedorMensajes.scrollHeight;
}

/* ---------- Envío ---------- */

function actualizarCompositor() {
  const agente = estado.seleccionado;
  const ocupado = Boolean(agente && estado.enviando.has(agente.clave));
  const habilitado = Boolean(agente && agente.disponible && !ocupado);

  campo.disabled = !habilitado;
  botonEnviar.disabled = !habilitado;
  botonEnviar.textContent = ocupado ? "Enviando…" : "Enviar";

  if (!agente) {
    return;
  }
  if (!agente.disponible) {
    campo.placeholder = "Agente pendiente de implementación";
  } else if (ocupado) {
    campo.placeholder = "Esperando la respuesta…";
  } else {
    campo.placeholder = "Escribe tu mensaje…";
  }
}

async function enviar(evento) {
  evento.preventDefault();

  const agente = estado.seleccionado;
  if (!agente || !agente.disponible || estado.enviando.has(agente.clave)) {
    return;
  }

  const texto = campo.value.trim();
  if (!texto) {
    return;
  }

  const conv = conversacion(agente.clave);
  conv.mensajes.push({ rol: "usuario", texto });
  campo.value = "";
  ajustarAltura();

  estado.enviando.add(agente.clave);
  actualizarCompositor();
  pintarMensajes();

  try {
    const respuesta = await fetch("/api/mensajes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agente: agente.clave,
        texto,
        context_id: conv.contextId,
      }),
    });

    const datos = await respuesta.json().catch(() => ({}));
    if (!respuesta.ok) {
      throw new Error(detalleDeError(datos, respuesta));
    }

    if (datos.context_id) {
      conv.contextId = datos.context_id;
    }
    conv.mensajes.push({
      rol: "agente",
      texto: datos.respuesta,
      latencia_ms: datos.latencia_ms,
    });
  } catch (error) {
    conv.mensajes.push({ rol: "error", texto: mensajeError(error) });
  } finally {
    estado.enviando.delete(agente.clave);
    if (estado.seleccionado && estado.seleccionado.clave === agente.clave) {
      actualizarCompositor();
      actualizarPie();
      pintarMensajes();
    }
  }
}

/* ---------- Detalles de la caja de texto ---------- */

function ajustarAltura() {
  campo.style.height = "auto";
  campo.style.height = `${Math.min(campo.scrollHeight, 160)}px`;
}

campo.addEventListener("input", ajustarAltura);

campo.addEventListener("keydown", (evento) => {
  if (evento.key === "Enter" && !evento.shiftKey) {
    evento.preventDefault();
    document.getElementById("formulario").requestSubmit();
  }
});

document.getElementById("formulario").addEventListener("submit", enviar);

document.getElementById("nueva-conversacion").addEventListener("click", () => {
  const agente = estado.seleccionado;
  if (!agente || estado.enviando.has(agente.clave)) {
    return;
  }
  const conv = conversacion(agente.clave);
  conv.contextId = nuevoContexto();
  conv.mensajes = [];
  actualizarPie();
  pintarMensajes();
  if (agente.disponible) {
    campo.focus();
  }
});

document.getElementById("recargar").addEventListener("click", cargarAgentes);

/* Revisa el estado cada 10 s, y otra vez al volver a la pestaña, para que una
   etiqueta "Sin conexión" no se quede pegada cuando el servidor ya arrancó. */
const REFRESCO_MS = 10000;
setInterval(refrescarEstado, REFRESCO_MS);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    refrescarEstado();
  }
});

cargarAgentes();
