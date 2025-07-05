"""
Configuración y gestión de modelos Ollama
"""

import subprocess
import json
from typing import List, Dict, Any, Optional

class ModelManager:
    """Gestor de modelos Ollama"""
    
    def __init__(self):
        self.available_models = []
        self.current_model = None
        self._refresh_models()
    
    def _refresh_models(self):
        """Actualizar lista de modelos disponibles"""
        try:
            result = subprocess.run(
                ['ollama', 'list'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Parsear salida de ollama list
            lines = result.stdout.strip().split('\n')[1:]  # Saltar header
            self.available_models = []
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        size = parts[2] if len(parts) > 2 else 'Unknown'
                        self.available_models.append({
                            'name': name,
                            'size': size,
                            'id': parts[1] if len(parts) > 1 else ''
                        })
                        
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback si ollama no está disponible
            self.available_models = []
    
    def is_model_available(self, model_name: str) -> bool:
        """Verificar si un modelo está disponible"""
        return any(model['name'] == model_name for model in self.available_models)
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un modelo"""
        for model in self.available_models:
            if model['name'] == model_name:
                return model
        return None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Listar todos los modelos disponibles"""
        return self.available_models
    
    def get_recommended_model(self, task_type: str = 'general') -> str:
        """Obtener modelo recomendado para un tipo de tarea"""
        recommendations = {
            'reasoning': ['deepseek-r1:8b', 'qwen2.5:7b'],
            'coding': ['qwen2.5-coder:1.5b', 'codellama:7b'],
            'fast': ['qwen2.5-coder:1.5b', 'phi3:mini'],
            'general': ['deepseek-r1:8b', 'qwen2.5:7b']
        }
        
        preferred = recommendations.get(task_type, recommendations['general'])
        
        # Retornar el primer modelo disponible de la lista preferida
        for model in preferred:
            if self.is_model_available(model):
                return model
        
        # Si no hay modelos preferidos, retornar el primero disponible
        if self.available_models:
            return self.available_models[0]['name']
        
        return 'deepseek-r1:8b'  # Fallback
    
    def pull_model(self, model_name: str) -> bool:
        """Descargar un modelo si no está disponible"""
        try:
            print(f"🔄 Descargando modelo {model_name}...")
            subprocess.run(['ollama', 'pull', model_name], check=True)
            self._refresh_models()
            print(f"✅ Modelo {model_name} descargado exitosamente")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ Error descargando modelo {model_name}")
            return False
    
    def test_model(self, model_name: str) -> bool:
        """Probar si un modelo funciona correctamente"""
        try:
            result = subprocess.run(
                ['ollama', 'run', model_name, 'Responde solo "OK"'],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0 and 'OK' in result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False