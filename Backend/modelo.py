import ollama
import json
import re
from html import unescape

FRAMEWORKS_CONOCIDOS = {
    "Django", "Flask", "FastAPI", "React", "Vue", 
    "Angular", "Spring", "Express", "Laravel"
}

def limpiar_json(texto):
    """Limpia y valida el JSON generado por el modelo"""
    try:
        texto = unescape(texto.strip())
        # Extraer JSON entre ```json``` si existe
        json_match = re.search(r'```(?:json)?\n(.*?)\n```', texto, re.DOTALL)
        if json_match:
            texto = json_match.group(1)
        return json.loads(texto)
    except Exception as e:
        return {
            "error": "invalid_json",
            "message": str(e),
            "original_response": texto[:500] + ("..." if len(texto) > 500 else "")
        }

def modelo_experto(descripcion):
    prompt = f"""
    Como arquitecto de software, genera un JSON con tecnologías esenciales para:
    "{descripcion}"

    Estructura requerida:
    {{
        "lenguaje": "string",        // Solo 1 lenguaje principal
        "framework": "string",       // Framework principal (no alternativas)
        "librerias": ["string"],     // 3-4 librerías clave máximo
        "bases_de_datos": ["string"],// 1-2 bases de datos
        "frontend": ["string"],      // Tecnologías frontend esenciales
        "backend": ["string"]        // Tecnologías backend esenciales
    }}

    Reglas estrictas:
    1. Solo tecnologías maduras y ampliamente usadas
    2. No incluir alternativas o opciones secundarias
    3. Máximo 4 ítems por categoría
    4. Solo responder con JSON válido
    5. No incluir texto fuera del JSON
    """

    try:
        response = ollama.chat(
            model="llama3:latest",
            messages=[{
                "role": "system",
                "content": "Eres un arquitecto de software conciso. Solo responde con JSON válido."
            }, {
                "role": "user",
                "content": prompt
            }],
            options={"temperature": 0.5}
        )
        data = limpiar_json(response['message']['content'])
        
        # Post-procesamiento para eliminar redundancias
        if isinstance(data, dict):
            if "backend" in data and "lenguaje" in data:
                data["backend"] = [tech for tech in data["backend"] if tech != data["lenguaje"]]
            if "librerias" in data:
                data["librerias"] = [lib for lib in data["librerias"] if lib not in FRAMEWORKS_CONOCIDOS]
        
        return data
    except Exception as e:
        return {"error": "model_error", "message": str(e)}

def modelo_respuesta(descripcion, recomendacion):
    prompt = f"""
    Genera un informe técnico en JSON para:
    Proyecto: "{descripcion}"
    Tecnologías: {json.dumps(recomendacion, indent=2)}

    Estructura requerida:
    {{
        "introduccion": "string",
        "explicacion_tecnologias": {{
            "lenguaje": {{
                "nombre": "string",
                "descripcion": "string",
                "justificacion": "string",  // Explicación específica para este proyecto
                "caracteristicas": ["string"]  // 2-3 características relevantes
            }},
            "framework": {{
                "nombre": "string",
                "descripcion": "string",
                "justificacion": "string",
                "casos_uso": ["string"]  // Cómo se usará en este proyecto
            }},
            "librerias": [
                {{
                    "nombre": "string",
                    "descripcion": "string",
                    "uso": "string",      // Uso concreto en el proyecto
                    "justificacion": "string",
                    "instalacion": "string"  // Formato: 'npm install nombre'
                }}
            ]
        }},
        "base_datos": {{
            "nombre": "string",
            "descripcion": "string",
            "justificacion": "string",
            "instalacion": {{
                "windows": "string",  // Comando completo
                "linux": "string",    // Comando completo
                "macos": "string"     // Comando completo
            }}
        }},
        "arquitectura": {{
            "diagrama": "string",     // Breve descripción textual
            "componentes": ["string"] // Componentes principales
        }},
        "instalacion": {{
            "requisitos": ["string"], // Requisitos previos
            "librerias": {{
                "comando": "string",  // Ej: 'npm install'
                "ejemplo": "string"   // Ej: 'npm install express mongoose'
            }}
        }},
        "recomendaciones": ["string"] // 3-4 recomendaciones clave
    }}

    Instrucciones:
    1. Explicaciones técnicas específicas para este proyecto
    2. Comandos de instalación completos y verificados
    3. Sin información redundante
    4. Solo JSON válido, sin markdown o texto adicional
    """

    try:
        response = ollama.chat(
            model="llama3:latest",
            messages=[{
                "role": "system",
                "content": "Eres un ingeniero senior que genera informes técnicos precisos en JSON."
            }, {
                "role": "user",
                "content": prompt
            }],
            options={"temperature": 0.3}
        )
        return limpiar_json(response['message']['content'])
    except Exception as e:
        return {"error": "report_error", "message": str(e)}

def modelo_codigo(descripcion, recomendacion):
    prompt = f"""
    Genera código de ejemplo para:
    Proyecto: "{descripcion}"
    Tecnologías: {json.dumps(recomendacion, indent=2)}

    Requisitos:
    1. Código funcional y bien estructurado
    2. Incluir:
       - Configuración inicial
       - Modelo de datos ejemplo
       - API REST básica
       - Componente frontend simple
    3. Comentarios claros y concisos
    4. Sin marcas de código (```)
    5. Solo el código, sin explicaciones
    """

    try:
        response = ollama.chat(
            model="llama3:latest",
            messages=[{
                "role": "system",
                "content": "Eres un desarrollador senior que escribe código limpio y documentado."
            }, {
                "role": "user",
                "content": prompt
            }],
            options={"temperature": 0.2}
        )
        # Limpieza exhaustiva del código
        code = response['message']['content']
        code = re.sub(r'^```[a-z]*\n?|\n```$', '', code, flags=re.IGNORECASE)
        code = re.sub(r'^(Aquí|Here).*?\n', '', code, flags=re.IGNORECASE)
        return {"codigo": code.strip()}
    except Exception as e:
        return {"codigo": f"// Error generando código: {str(e)}", "advertencia": "El código puede estar incompleto"}