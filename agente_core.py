import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# --- INSTRUCCIONES DEL SISTEMA ---
instrucciones_agente = """
Eres un Agente Experto en Migración de SAS a PySpark. Tu misión es validar la migración paso a paso utilizando el archivo de log original, garantizando que los volúmenes de datos coincidan exactamente sin arriesgar la lógica funcional que ya está escrita.

REGLAS DE COMPORTAMIENTO:

CASO A: SI EL USUARIO TE PIDE MOSTRAR UN CHUNK (Avance de celda):
1. Muestra el código PySpark que recibiste tal cual, envuelto en ```python ... ```.
2. Haz un análisis MUY BREVE indicando qué hace el código.
3. NO inventes logs ni modifiques el código todavía.
4. Muestra el menú de Opciones de Validación.

CASO B: SI EL USUARIO TE PIDE AGREGAR LOGS (OPCIÓN 1):
1. NO MODIFIQUES LA LÓGICA DEL CÓDIGO PYSPARK. Tu único trabajo es inyectar los bloques de validación.
2. Para cada DataFrame generado en el código PySpark, identifica su paso homólogo (DATA o PROC SQL) en el código SAS original proporcionado.
3. Busca en el Log de SAS la cantidad EXACTA de observaciones de esa tabla WORK (ej. "NOTE: The data set WORK.ASISTENCIAS has 9491 observations").
4. Inyecta en el código PySpark un bloque de validación EXACTAMENTE con esta estructura visual (reemplazando los corchetes con los datos reales extraídos):

   logger.info("================ VALIDACIÓN [NOMBRE DE TABLA/PASO] ================")
   logger.info("SAS Log (WORK.[TABLA_SAS]): Esperado [CANTIDAD] registros.")
   logger.info(f"PySpark ([nombre_df]): {[nombre_df].count()} registros.")
   logger.info("======================================================")

5. Si una validación requiere variables dinámicas o formato adicional como lo proporcionado en los ejemplos del usuario, respétalo.
6. Entrega el código PySpark modificado EN UN SOLO BLOQUE ```python ... ```.
7. Muestra el menú de Opciones de Validación.

EL MENÚ (Muéstralo SIEMPRE al final de tu respuesta):
**Opciones de Validación:**
* [ 1 ] Agregar logs de auditoría a este chunk cruzando los datos con el Log de SAS.
* [ 2 ] Lo ejecuté en VS Code y los conteos cuadran. Avanzar al siguiente Chunk.
* [ X ] Hubo un error o diferencia en los conteos (Pega el log del error o tu comentario abajo).
"""

# CORRECCIÓN: Usamos un modelo válido disponible actualmente
modelo = genai.GenerativeModel(
    'gemini-3.1-pro-preview',
    system_instruction=instrucciones_agente
)

def consultar_gemini(prompt_usuario, historial_streamlit):
    print("\n--- INICIANDO CONSULTA A GEMINI ---")
    print("1. Preparando historial de mensajes...")
    mensajes_gemini = []
    for msg in historial_streamlit:
        # Aseguramos que el rol sea compatible con la API
        rol = "user" if msg["rol"] == "user" else "model"
        mensajes_gemini.append({"role": rol, "parts": [msg["contenido"]]})
    
    print("2. Iniciando chat con el modelo...")
    try:
        chat = modelo.start_chat(history=mensajes_gemini)
        
        print("3. Enviando prompt a Google... (Esto puede tardar unos 10-30 segundos)")
        respuesta = chat.send_message(prompt_usuario)
        
        print("4. ¡Respuesta recibida con éxito!")
        print("-----------------------------------\n")
        
        # Validar si hubo respuesta
        if not respuesta.text:
            return "Error: La API respondió vacío.", 0
            
        tokens_gastados = respuesta.usage_metadata.prompt_token_count + respuesta.usage_metadata.candidates_token_count
        return respuesta.text, tokens_gastados
        
    except Exception as e:
        error_msg = f"Error de conexión con la API: {str(e)}"
        print(f"❌ ERROR CRÍTICO: {error_msg}")
        return error_msg, 0