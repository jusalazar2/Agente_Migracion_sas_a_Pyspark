import os
import shutil
from agente_core import consultar_gemini
from herramientas import leer_chunk_notebook, actualizar_chunk_notebook, extraer_codigo_python, leer_log_sas, leer_codigo_sas, contar_total_chunks
import streamlit as st

st.set_page_config(page_title="Agente Migración PySpark", page_icon="🤖", layout="wide")

# 1. Inicializamos los nombres por defecto en el estado para que 'contar_total_chunks' no falle al arrancar
if "archivo_pyspark" not in st.session_state: st.session_state.archivo_pyspark = "nbk_cispc157.ipynb"
if "archivo_sas" not in st.session_state: st.session_state.archivo_sas = "cispc157.sas"
if "archivo_log" not in st.session_state: st.session_state.archivo_log = "cispc157.log"

# --- VARIABLES DE ESTADO ---
if "mensajes" not in st.session_state: st.session_state.mensajes = []
if "chunk_actual" not in st.session_state: st.session_state.chunk_actual = 0
if "tokens_usados" not in st.session_state: st.session_state.tokens_usados = 0
if "codigo_pendiente" not in st.session_state: st.session_state.codigo_pendiente = None 

PRESUPUESTO_TOKENS = 5000000

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📊 Archivos de Origen")
        
    st.session_state.archivo_pyspark = st.text_input("🐍 Notebook PySpark:", value=st.session_state.archivo_pyspark)
    st.session_state.archivo_sas = st.text_input("⚙️ Código SAS Original:", value=st.session_state.archivo_sas)
    st.session_state.archivo_log = st.text_input("📄 Log SAS Referencia:", value=st.session_state.archivo_log)
    
    # 2. CONTEO DINÁMICO: Se recalcula cada vez que cambia el texto de la caja
    st.session_state.total_chunks = contar_total_chunks(st.session_state.archivo_pyspark)
    
    archivo_destino = st.session_state.archivo_pyspark.replace(".ipynb", "_validado.ipynb")
    st.caption(f"💾 Archivo de Salida: {archivo_destino}")
    st.divider()    
    
    if st.session_state.total_chunks > 0:
        # 3. BLINDAJE: Usamos min() para asegurar que el valor enviado a st.progress jamás supere 1.0
        progreso_seguro = min(1.0, st.session_state.chunk_actual / st.session_state.total_chunks)
        st.progress(progreso_seguro)
        
    st.write(f"**Chunk Actual:** {st.session_state.chunk_actual} / {st.session_state.total_chunks}")
    st.metric(label="Tokens Usados", value=f"{st.session_state.tokens_usados:,}")
    st.success("✅ Entorno PySpark Local: Conectado")

# --- ÁREA PRINCIPAL ---
st.title("🤖 Asistente Autónomo: Migración SAS a PySpark")

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

arranque_automatico = False
prompt = None

if len(st.session_state.mensajes) == 0:
    st.info("Asegúrate de que los 3 archivos estén configurados en la barra lateral.")
    if st.button("🚀 Iniciar Traducción y Auditoría del Chunk 1", use_container_width=True):
        if os.path.exists(st.session_state.archivo_pyspark):
            shutil.copy(st.session_state.archivo_pyspark, archivo_destino)
        prompt = "Inicia la validación del Chunk 1"
        arranque_automatico = True
else:
    prompt = st.chat_input("Ej: 1 (Agregar Logs), 2 (Aprobar y Avanzar), o texto para corregir...")

if prompt or arranque_automatico:
    with st.chat_message("user"): st.markdown(prompt)
    
    prompt_enriquecido = prompt
    texto_minusculas = prompt.lower().strip()
    accion = "chat_libre"

    if "inicia" in texto_minusculas and st.session_state.chunk_actual == 0:
        st.session_state.chunk_actual = 1
        accion = "mostrar_chunk"
    elif "siguiente" in texto_minusculas or "listo" in texto_minusculas or texto_minusculas == "2":
        if st.session_state.chunk_actual > 0:
            codigo_a_guardar = st.session_state.codigo_pendiente if st.session_state.codigo_pendiente else leer_chunk_notebook(st.session_state.archivo_pyspark, st.session_state.chunk_actual)
            res = actualizar_chunk_notebook(codigo_a_guardar, st.session_state.chunk_actual, st.session_state.archivo_pyspark, archivo_destino)
            st.toast(f"✅ {res}")
        st.session_state.codigo_pendiente = None
        st.session_state.chunk_actual += 1
        accion = "mostrar_chunk"
    elif texto_minusculas == "1":
        accion = "generar_logs"

    mkd = "```"

    if accion == "mostrar_chunk" and st.session_state.chunk_actual > 0:
        codigo_pyspark = leer_chunk_notebook(st.session_state.archivo_pyspark, st.session_state.chunk_actual)
        prompt_enriquecido = (f"El usuario avanzó al Chunk {st.session_state.chunk_actual}.\n"
                              f"Muestra este código, descríbelo brevemente y pregúntale qué hacer:\n\n{mkd}python\n{codigo_pyspark}\n{mkd}")

    elif accion == "generar_logs" and st.session_state.chunk_actual > 0:
        codigo_pyspark = leer_chunk_notebook(st.session_state.archivo_pyspark, st.session_state.chunk_actual)
        codigo_sas = leer_codigo_sas(st.session_state.archivo_sas)
        contenido_log = leer_log_sas(st.session_state.archivo_log)
        
        prompt_enriquecido = (f"El usuario seleccionó la opción [ 1 ]. Procesa el Chunk {st.session_state.chunk_actual}.\n\n"
                              f"1. PySpark base:\n{mkd}python\n{codigo_pyspark}\n{mkd}\n\n"
                              f"2. SAS Original:\n{mkd}sas\n{codigo_sas}\n{mkd}\n\n"
                              f"3. Log SAS:\n<log_sas>\n{contenido_log}\n</log_sas>\n\n"
                              f"Reescribe el código PySpark inyectando los logs de validación.")

    st.session_state.mensajes.append({"rol": "user", "contenido": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Procesando instrucción..."):
            texto_respuesta, tokens_gastados = consultar_gemini(prompt_enriquecido, st.session_state.mensajes)
            st.markdown(texto_respuesta)
            st.session_state.tokens_usados += tokens_gastados
            
            codigo_limpio = extraer_codigo_python(texto_respuesta)
            if codigo_limpio:
                st.session_state.codigo_pendiente = codigo_limpio
                st.caption("📝 *Código modificado en memoria temporal. Escribe '2' o 'listo' para aprobarlo y guardarlo definitivamente.*")
                
    st.session_state.mensajes.append({"rol": "assistant", "contenido": texto_respuesta})
    st.rerun()