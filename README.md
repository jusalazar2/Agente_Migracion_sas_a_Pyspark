# 🤖 SAS to PySpark Migration Auditor

## 📝 Descripción del Proyecto
En proyectos de modernización de datos a gran escala, garantizar la paridad exacta entre los entornos legacy (SAS) y las nuevas arquitecturas (PySpark/Databricks) es un desafío crítico. 

Esta herramienta proporciona un **Asistente Autónomo con IA (Gemini 1.5 Pro)** diseñado para auditar la traducción de código paso a paso. El sistema cruza la lógica de los scripts SAS originales, sus logs de ejecución y los Jupyter Notebooks en PySpark, inyectando automáticamente bloques de validación (`logger.info`) para comparar los recuentos de registros de forma precisa.

## ✨ Características Principales
* **Auditoría Automatizada:** Analiza logs de SAS (`.log`) para extraer métricas esperadas y generar comparaciones dinámicas contra DataFrames de PySpark (`df.count()`).
* **Flujo Human-in-the-Loop (HITL):** Interfaz gráfica construida en **Streamlit** que permite al ingeniero validar cada *chunk* de código de forma aislada antes de hacer commit en el Notebook final.
* **Aislamiento de Entorno (Data-Centric):** Motor de lectura/escritura robusto que protege el código fuente y opera exclusivamente en un directorio de trabajo (`/data`), generando un archivo `_validado.ipynb` listo para producción.
* **Memoria Temporal (Draft & Commit):** Sistema de control de versiones interno por celda, previniendo sobrescrituras accidentales durante el proceso de corrección asistido por el LLM.

## 🛠️ Stack Tecnológico
* **Core:** Python 3.x, PySpark, Pandas
* **UI & Interacción:** Streamlit
* **IA / LLM:** Google Gemini API (`gemini-1.5-pro`)
* **Gestión de Notebooks:** `json`, `nbformat` (manipulación nativa de `.ipynb`)

## 🚀 Instalación y Uso

1. Clonar el repositorio:
```bash
git clone [https://github.com/jusalazar2/Agente_Migracion_sas_a_Pyspark.git](https://github.com/jusalazar2/Agente_Migracion_sas_a_Pyspark.git)
```

2. Crear y activar el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar credenciales:
Crear un archivo `.env` en la raíz del proyecto y añadir el API Key de Gemini:
```env
GEMINI_API_KEY=tu_clave_aqui
```

5. Ejecutar la aplicación:
Coloca tus archivos de origen (`.sas`, `.log`, `.ipynb`) en la carpeta `/data` y lanza la interfaz:
```bash
streamlit run app.py
```

---
