from config import Config
from cache.cache_manager import cache
from utils.monitoring import monitor
from huggingface_hub import InferenceClient
import json
import re
from html import unescape

client = InferenceClient(model=Config.MODEL_NAME, token=Config.HF_API_TOKEN)

FRAMEWORKS_CONOCIDOS = {
    "Django", "Flask", "FastAPI", "React", "Vue", 
    "Angular", "Spring", "Express", "Laravel"
}

def limpiar_json(texto):
    """Limpia y valida el JSON generado por el modelo"""
    try:
        texto = unescape(texto.strip())
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

def generar_respuesta(prompt, system_prompt="", temperature=0.7, cache_key=None):
    """Función genérica para interactuar con la API con caché"""
    if cache_key and Config.CACHE_ENABLED:
        cached = cache.get(cache_key)
        if cached is not None:
            monitor.log_request("/predict", True, 0)
            return cached
            
    try:
        response = client.text_generation(
            prompt=f"<s>[INST] {system_prompt} {prompt} [/INST]",
            max_new_tokens=1500,
            temperature=temperature,
            return_full_text=False
        )
        
        # Estimación de tokens (aproximadamente 1.33 tokens por palabra)
        tokens_used = int(len(response.split()) * 1.33)
        monitor.log_request("/predict", True, tokens_used)
        
        if cache_key and Config.CACHE_ENABLED:
            cache.set(cache_key, response)
            
        return response
    except Exception as e:
        monitor.log_request("/predict", False)
        return {"error": str(e)}

def modelo_experto(descripcion):
    cache_key = f"expert_{descripcion[:100]}"  # Usamos los primeros 100 caracteres para el key
    
    prompt = f"""
    Como arquitecto de software, genera un JSON con tecnologías esenciales para:
    "{descripcion}"

    Estructura requerida:
    {{
        "lenguaje": "string",
        "framework": "string",
        "librerias": ["string"],
        "bases_de_datos": ["string"],
        "frontend": ["string"],
        "backend": ["string"]
    }}

    Reglas estrictas:
    1. Solo tecnologías maduras y ampliamente usadas
    2. No incluir alternativas
    3. Máximo 4 ítems por categoría
    4. Solo responder con JSON válido
    5. No incluir texto fuera del JSON
    """

    system_prompt = "Eres un arquitecto de software conciso. Solo responde con JSON válido."
    response = generar_respuesta(prompt, system_prompt, 0.5, cache_key)
    
    if isinstance(response, dict) and "error" in response:
        return response
        
    data = limpiar_json(response)
    
    # Post-procesamiento
    if isinstance(data, dict):
        if "backend" in data and "lenguaje" in data:
            data["backend"] = [tech for tech in data["backend"] if tech != data["lenguaje"]]
        if "librerias" in data:
            data["librerias"] = [lib for lib in data["librerias"] if lib not in FRAMEWORKS_CONOCIDOS]
    
    return data

def modelo_respuesta(descripcion, recomendacion):
    cache_key = f"report_{hash(descripcion + str(recomendacion))}"
    
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
                "justificacion": "string",
                "caracteristicas": ["string"]
            }},
            "framework": {{
                "nombre": "string",
                "descripcion": "string",
                "justificacion": "string",
                "casos_uso": ["string"]
            }},
            "librerias": [
                {{
                    "nombre": "string",
                    "descripcion": "string",
                    "uso": "string",
                    "justificacion": "string",
                    "instalacion": "string"
                }}
            ]
        }},
        "base_datos": {{
            "nombre": "string",
            "descripcion": "string",
            "justificacion": "string",
            "instalacion": {{
                "windows": "string",
                "linux": "string",
                "macos": "string"
            }}
        }},
        "arquitectura": {{
            "diagrama": "string",
            "componentes": ["string"]
        }},
        "instalacion": {{
            "requisitos": ["string"],
            "librerias": {{
                "comando": "string",
                "ejemplo": "string"
            }}
        }},
        "recomendaciones": ["string"]
    }}
    """

    system_prompt = "Eres un ingeniero senior que genera informes técnicos precisos en JSON."
    response = generar_respuesta(prompt, system_prompt, 0.3, cache_key)
    
    if isinstance(response, dict) and "error" in response:
        return response
        
    return limpiar_json(response)

def modelo_codigo(descripcion, recomendacion):
    cache_key = f"code_{hash(descripcion + str(recomendacion))}"
    
    prompt = f"""
    Genera código de ejemplo para:
    Proyecto: "{descripcion}"
    Tecnologías: {json.dumps(recomendacion, indent=2)}

    Requisitos:
    1. Código funcional y bien estructurado
    2. Incluir configuración inicial, modelo de datos, API REST y componente frontend
    3. Comentarios claros
    4. Sin marcas de código (```)
    5. Solo el código, sin explicaciones
    """

    system_prompt = "Eres un desarrollador senior que escribe código limpio y documentado."
    response = generar_respuesta(prompt, system_prompt, 0.2, cache_key)
    
    if isinstance(response, dict) and "error" in response:
        return {"codigo": f"// Error: {response['error']}", "advertencia": "Error generando código"}
    
    # Limpieza del código
    code = re.sub(r'^```[a-z]*\n?|\n```$', '', response, flags=re.IGNORECASE)
    code = re.sub(r'^(Aquí|Here).*?\n', '', code, flags=re.IGNORECASE)
    return {"codigo": code.strip()}