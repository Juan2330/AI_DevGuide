import json
from datetime import datetime
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from modelo import modelo_experto, modelo_respuesta, modelo_codigo
from utils.monitoring import monitor
from config import Config

app = Flask(__name__)
CORS(app, resources={
    r"/predict": {"origins": Config.ALLOWED_ORIGINS},
    r"/usage": {"origins": Config.ALLOWED_ORIGINS}
})

def validate_description(descripcion):
    """Valida la descripción del proyecto"""
    if not descripcion or not isinstance(descripcion, str):
        return False
    return len(descripcion.strip()) >= 20

@app.route('/')
def home():
    return "AI DevGuide API está activa", 200

@app.route('/usage')
def get_usage():
    if not Config.MONITORING_ENABLED:
        return jsonify({"error": "Monitoring disabled"}), 403
        
    usage_data = monitor.get_usage_stats()
    hf_quota = monitor.check_hf_quota()
    
    response = {
        "system": {
            "status": "active",
            "model": Config.MODEL_NAME,
            "cache_enabled": Config.CACHE_ENABLED,
            "monitoring_enabled": Config.MONITORING_ENABLED
        },
        "usage": usage_data,
        "huggingface": hf_quota
    }
    
    return jsonify(response)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Formato inválido",
                "message": "El request debe ser JSON"
            }), 400

        data = request.get_json()

        if not data or 'descripcion' not in data:
            return jsonify({
                "success": False,
                "error": "Campo faltante",
                "message": "El campo 'descripcion' es requerido"
            }), 400

        descripcion = data['descripcion'].strip()
        if not validate_description(descripcion):
            return jsonify({
                "success": False,
                "error": "Descripción inválida",
                "message": "La descripción debe tener al menos 20 caracteres"
            }), 400

        recomendacion = None
        for _ in range(3):
            recomendacion = modelo_experto(descripcion)
            if "error" not in recomendacion:
                break

        if "error" in recomendacion:
            return jsonify({
                "success": False,
                "error": "Error en el modelo",
                "message": "No se pudo generar recomendaciones técnicas",
                "details": recomendacion
            }), 500

        informe = modelo_respuesta(descripcion, recomendacion)
        if "error" in informe:
            return jsonify({
                "success": False,
                "error": "Error en el informe",
                "message": "No se pudo generar el informe técnico",
                "details": informe
            }), 500

        codigo_ejemplo = modelo_codigo(descripcion, recomendacion)

        response = {
            "success": True,
            "metadata": {
                "version": "1.0",
                "model": Config.MODEL_NAME,
                "timestamp": datetime.now().isoformat(),
                "cache_hit": hasattr(recomendacion, "_from_cache")
            },
            "technologies": {
                "language": {
                    "name": recomendacion.get("lenguaje"),
                    "type": "programming"
                },
                "framework": {
                    "name": recomendacion.get("framework"),
                    "type": "web_framework"
                } if recomendacion.get("framework") else None,
                "libraries": [{
                    "name": lib,
                    "type": "library"
                } for lib in recomendacion.get("librerias", [])],
                "database": {
                    "name": recomendacion.get("bases_de_datos", [])[0] if recomendacion.get("bases_de_datos") else None,
                    "type": "database"
                },
                "frontend": [{
                    "name": tech,
                    "type": "frontend"
                } for tech in recomendacion.get("frontend", [])],
                "backend": [{
                    "name": tech,
                    "type": "backend"
                } for tech in recomendacion.get("backend", [])]
            },
            "report": informe,
            "code_example": {
                "content": codigo_ejemplo.get("codigo") if isinstance(codigo_ejemplo, dict) else codigo_ejemplo,
                "language": recomendacion.get("lenguaje") or "javascript",
                "lines": len(codigo_ejemplo.get("codigo", "").split('\n')) if isinstance(codigo_ejemplo, dict) else 0
            },
            "warnings": {
                "code": codigo_ejemplo.get("advertencia") if isinstance(codigo_ejemplo, dict) else None,
                "report": informe.get("advertencia") if isinstance(informe, dict) else None
            }
        }

        return jsonify(response)

    except Exception as e:
        monitor.log_request("/predict", False)
        return jsonify({
            "success": False,
            "error": "server_error",
            "message": "Error interno del servidor",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    if os.getenv("ENV") == "production":
        from gunicorn.app.wsgiapp import WSGIApplication
        WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()
    else:
        app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)