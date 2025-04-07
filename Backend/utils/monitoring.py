from datetime import datetime
from config import Config
import requests
import json

class UsageMonitor:
    def __init__(self):
        self.usage_data = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "tokens_used": 0,
            "last_request": None,
            "endpoints": {
                "/predict": 0,
                "/usage": 0
            }
        }
        
    def log_request(self, endpoint, success=True, tokens=0):
        if not Config.MONITORING_ENABLED:
            return
            
        self.usage_data["total_requests"] += 1
        self.usage_data["endpoints"][endpoint] = self.usage_data["endpoints"].get(endpoint, 0) + 1
        
        if success:
            self.usage_data["successful_requests"] += 1
            self.usage_data["tokens_used"] += tokens
        else:
            self.usage_data["failed_requests"] += 1
            
        self.usage_data["last_request"] = datetime.now().isoformat()
        
    def get_usage_stats(self):
        return {
            "usage": self.usage_data,
            "cache_enabled": Config.CACHE_ENABLED,
            "monitoring_enabled": Config.MONITORING_ENABLED
        }
        
    def check_hf_quota(self):
        if not Config.HF_API_TOKEN:
            return {"error": "No HF_API_TOKEN configured"}
            
        try:
            response = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers={"Authorization": f"Bearer {Config.HF_API_TOKEN}"},
                timeout=5
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

monitor = UsageMonitor()