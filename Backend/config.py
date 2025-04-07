import os
from dotenv import load_dotenv
import json

load_dotenv()

class Config:
    # Configuración de Hugging Face
    HF_API_TOKEN = os.getenv("HF_API_TOKEN")
    MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
    
    # Configuración del servidor
    PORT = int(os.getenv("PORT", 10000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    ALLOWED_ORIGINS = json.loads(os.getenv("ALLOWED_ORIGINS", 
        '["http://localhost:5173", "http://127.0.0.1:5173", "https://ai-devguide-huggin-1.onrender.com"]'))
    
    # Configuración de caché
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_DIR = os.getenv("CACHE_DIR", "cache/responses")
    MAX_CACHE_AGE_DAYS = int(os.getenv("MAX_CACHE_AGE_DAYS", 7))
    
    # Configuración de monitoreo
    MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"