"""
Interfaz de comunicación con Ollama
"""

import subprocess
import json
from typing import List, Dict, Any, Optional

class OllamaInterface:
    """Interfaz para comunicarse con Ollama"""
    
    def __init__(self, settings):
        self.settings = settings
        self.current_model = settings.models['current']
    
    def test_connection(self) -> bool:
        """Probar conexión con Ollama"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def test_model(self, model_name: str) -> bool:
        """Probar si un modelo específico funciona"""
        try:
            result = subprocess.run(
                ['ollama', 'run', model_name, 'Responde solo "OK"'],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0 and 'OK' in result.stdout
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def chat(self, messages: List[Dict[str, str]], model_name: str = None) -> Optional[str]:
        """
        Enviar mensajes a Ollama y obtener respuesta
        
        Args:
            messages: Lista de mensajes en formato [{'role': 'user/assistant', 'content': '...'}]
            model_name: Nombre del modelo a usar (opcional)
        
        Returns:
            Respuesta del modelo o None si hay error
        """
        if model_name is None:
            model_name = self.current_model
        
        try:
            # Preparar el prompt final
            prompt = self._format_messages_for_ollama(messages)
            
            # Ejecutar ollama
            result = subprocess.run(
                ['ollama', 'run', model_name, prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutos timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"❌ Error de Ollama: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout: El modelo tardó demasiado en responder")
            return None
        except FileNotFoundError:
            print("❌ Ollama no encontrado. Asegúrate de que esté instalado y en el PATH")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None
    
    def _format_messages_for_ollama(self, messages: List[Dict[str, str]]) -> str:
        """
        Formatear mensajes para Ollama
        
        Ollama no maneja el formato de mensajes estructurados como OpenAI,
        así que convertimos a un prompt simple
        """
        system_prompt = """Eres Claude, un asistente de IA especializado en programación y análisis de código.
Estás corriendo localmente a través de Ollama.

Características:
- Eres experto en programación, análisis de código y tareas de desarrollo
- Puedes explorar archivos y directorios
- Ayudas a crear, editar y analizar código
- Respondes de manera concisa y práctica
- Usas emojis apropiados para hacer las respuestas más claras

Contexto actual: Estás en una CLI local similar a Claude Code."""
        
        # Construir prompt
        prompt_parts = [system_prompt, "\n\n"]
        
        for message in messages:
            role = message['role']
            content = message['content']
            
            if role == 'user':
                prompt_parts.append(f"Usuario: {content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"Asistente: {content}\n")
        
        prompt_parts.append("Asistente: ")
        
        return "".join(prompt_parts)
    
    def get_available_models(self) -> List[str]:
        """Obtener lista de modelos disponibles"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Saltar header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            else:
                return []
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def switch_model(self, model_name: str) -> bool:
        """Cambiar modelo actual"""
        if self.test_model(model_name):
            self.current_model = model_name
            return True
        return False
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Obtener información de un modelo"""
        if model_name is None:
            model_name = self.current_model
        
        # Información básica (podría expandirse)
        return {
            'name': model_name,
            'current': model_name == self.current_model,
            'available': self.test_model(model_name)
        }