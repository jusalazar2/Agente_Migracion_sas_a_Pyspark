import re
import json
import os

# Definimos la carpeta intocable por defecto
CARPETA_DATA = "data"

def asegurar_ruta_data(ruta):
    """
    Toma cualquier ruta, extrae solo el nombre del archivo 
    y lo obliga a estar dentro de la carpeta 'data/'.
    """
    nombre_archivo = os.path.basename(ruta)
    return os.path.join(CARPETA_DATA, nombre_archivo)

def leer_chunk_notebook(ruta="nbk_cispc157.ipynb", numero_chunk=1):
    """
    Abre un Jupyter Notebook, filtra solo las celdas de código 
    y extrae el contenido exacto del chunk solicitado.
    """
    ruta_segura = asegurar_ruta_data(ruta)
    print(f"🔍 [Herramienta] Leyendo notebook: {ruta_segura}, Chunk número: {numero_chunk}")
    
    try:
        if not os.path.exists(ruta_segura):
            print(f"❌ ERROR: El archivo '{ruta_segura}' no existe.")
            return f"No se encontró el archivo: {ruta_segura}"

        with open(ruta_segura, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        celdas_codigo = [celda for celda in notebook['cells'] if celda['cell_type'] == 'code']
        indice = numero_chunk - 1
        
        if 0 <= indice < len(celdas_codigo):
            print(f"✅ [Herramienta] Chunk {numero_chunk} cargado exitosamente.")
            return "".join(celdas_codigo[indice]['source'])
        else:
            return f"Error: El chunk {numero_chunk} no existe en este notebook."
            
    except Exception as e:
        print(f"❌ [Herramienta] Error leyendo chunk: {e}")
        return f"Error al leer la libreta: {str(e)}"

def actualizar_chunk_notebook(nuevo_codigo, numero_chunk=1, ruta_origen="nbk_cispc157.ipynb", ruta_destino="nbk_cispc157_validado.ipynb"):
    """
    Lee el notebook original, reemplaza el código del chunk específico y guarda el nuevo notebook.
    """
    ruta_origen_segura = asegurar_ruta_data(ruta_origen)
    ruta_destino_segura = asegurar_ruta_data(ruta_destino)
    
    # Si ya hemos avanzado chunks y existe el validado, trabajamos sobre ese
    ruta_base = ruta_destino_segura if os.path.exists(ruta_destino_segura) else ruta_origen_segura
    
    try:
        # Aseguramos que la carpeta data exista antes de escribir
        if not os.path.exists(CARPETA_DATA):
            os.makedirs(CARPETA_DATA)

        with open(ruta_base, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        contador_codigo = 0
        for celda in notebook['cells']:
            if celda['cell_type'] == 'code':
                if contador_codigo == (numero_chunk - 1):
                    lineas_codigo = [linea + "\n" for linea in nuevo_codigo.split("\n")]
                    if lineas_codigo and lineas_codigo[-1].endswith("\n\n"):
                        lineas_codigo[-1] = lineas_codigo[-1][:-1]
                        
                    celda['source'] = lineas_codigo
                    break
                contador_codigo += 1
                
        # Escribimos siempre en la ruta destino dentro de data/
        with open(ruta_destino_segura, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
            
        return f"Chunk {numero_chunk} actualizado exitosamente en {ruta_destino_segura}"
        
    except Exception as e:
        return f"Error al modificar el notebook: {str(e)}"
    
def extraer_codigo_python(texto_respuesta):
    """Busca bloques de código Python dentro de la respuesta del LLM."""
    patron = r"```python\n(.*?)\n```"
    coincidencias = re.findall(patron, texto_respuesta, re.DOTALL)
    
    if coincidencias:
        return coincidencias[-1]
    return None

def leer_codigo_sas(ruta):
    """Lee el archivo original de SAS forzando la lectura en la carpeta data/"""
    ruta_segura = asegurar_ruta_data(ruta)
    try:
        if not os.path.exists(ruta_segura):
            print(f"❌ ERROR: El archivo SAS '{ruta_segura}' no existe.")
            return "No se encontró el archivo SAS."
        
        with open(ruta_segura, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
        
        print(f"DEBUG: Leyendo SAS en {ruta_segura}. Tamaño: {len(contenido)} caracteres.")
        return contenido
    except Exception as e:
        print(f"❌ ERROR crítico leyendo el archivo SAS: {str(e)}")
        return f"Error al leer el archivo SAS: {str(e)}"

def leer_log_sas(ruta):
    """Lee el archivo de log de SAS forzando la lectura en la carpeta data/"""
    ruta_segura = asegurar_ruta_data(ruta)
    try:
        if not os.path.exists(ruta_segura):
            print(f"❌ ERROR: El archivo Log '{ruta_segura}' no existe.")
            return "No se encontró el archivo Log."
            
        with open(ruta_segura, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
        
        print(f"DEBUG: Leyendo Log en {ruta_segura}. Tamaño: {len(contenido)} caracteres.")
        return contenido
    except Exception as e:
        print(f"❌ ERROR crítico leyendo el archivo Log: {str(e)}")
        return f"Error al leer el archivo Log: {str(e)}"