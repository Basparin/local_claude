"""
Configuración del sistema LocalClaude
"""

import os
from pathlib import Path
from typing import Dict, Any

class Settings:
    """Configuración global del sistema"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.workspace_dir = Path.cwd()
        
        # Configuración de modelos
        self.models = {
            'primary': 'deepseek-r1:8b',    # Modelo principal para razonamiento
            'fast': 'qwen2.5-coder:1.5b',   # Modelo rápido para tareas simples
            'current': 'qwen2.5-coder:1.5b'     # Modelo actual en uso (cambiado a rápido)
        }
        
        # Configuración de contexto
        self.context = {
            'max_tokens': 32000,              # Límite máximo de tokens
            'compression_threshold': 0.8,     # Comprimir al 80% del límite
            'memory_limit': 100,              # Límite de mensajes en memoria
            'summary_length': 500             # Longitud de resúmenes
        }
        
        # Configuración de la CLI
        self.cli = {
            'prompt': '💬 Tú: ',
            'response_prefix': '🤖 Claude: ',
            'command_prefix': '/',
            'colors': True,
            'debug': False  # Debug deshabilitado
        }
        
        # Configuración de archivos
        self.files = {
            'memory_db': self.base_dir / 'data' / 'memory.db',
            'context_cache': self.base_dir / 'data' / 'context_cache.json',
            'settings_file': self.base_dir / 'data' / 'user_settings.json'
        }
        
        # Crear directorios necesarios
        self._create_directories()
    
    def _create_directories(self):
        """Crear directorios necesarios"""
        data_dir = self.base_dir / 'data'
        data_dir.mkdir(exist_ok=True)
    
    def get_model_config(self, model_name: str = None) -> Dict[str, Any]:
        """Obtener configuración de un modelo específico"""
        if model_name is None:
            model_name = self.models['current']
        
        configs = {
            'deepseek-r1:8b': {
                'max_tokens': 32000,
                'temperature': 0.7,
                'top_p': 0.9,
                'use_for': ['reasoning', 'complex_tasks', 'coding']
            },
            'qwen2.5-coder:1.5b': {
                'max_tokens': 8192,
                'temperature': 0.3,
                'top_p': 0.8,
                'use_for': ['simple_tasks', 'code_completion', 'quick_answers']
            }
        }
        
        return configs.get(model_name, configs['deepseek-r1:8b'])
    
    def should_use_fast_model(self, task_type: str) -> bool:
        """Determinar si usar el modelo rápido para una tarea"""
        fast_tasks = ['ls', 'cat', 'grep', 'tree', 'find', 'status', 'help', 'context', 'history']
        complex_tasks = ['analyze', 'build', 'edit', 'generate', 'suggest', 'complexity']
        
        if task_type in fast_tasks:
            return True
        elif task_type in complex_tasks:
            return False
        else:
            # Default: usar modelo rápido para comandos simples
            return len(task_type) < 10
    
    def get_optimal_model(self, task_type: str) -> str:
        """Obtener modelo óptimo según tipo de tarea"""
        if self.should_use_fast_model(task_type):
            return "qwen2.5-coder:1.5b"
        else:
            return "deepseek-r1:8b"