"""
Gestor de contexto y memoria de conversaciones
"""

import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from .memory_store import MemoryStore

class ContextManager:
    """Gestor del contexto de conversación"""
    
    def __init__(self, settings):
        self.settings = settings
        self.messages: List[Dict[str, Any]] = []
        self.current_tokens = 0
        self.session_start = time.time()
        
        # Sistema de memoria persistente
        self.memory_store = MemoryStore(settings)
        self.session_id = self.memory_store.create_session(str(settings.workspace_dir))
        
        # Cargar contexto previo si existe
        self._load_context()
    
    def add_user_message(self, content: str):
        """Agregar mensaje del usuario"""
        message = {
            'role': 'user',
            'content': content,
            'timestamp': time.time()
        }
        
        self.messages.append(message)
        self._update_token_count()
        self._check_compression_needed()
        
        # Guardar en memoria persistente
        self.memory_store.save_message(
            session_id=self.session_id,
            role='user',
            content=content
        )
    
    def add_assistant_message(self, content: str, model_used: str = None):
        """Agregar mensaje del asistente"""
        message = {
            'role': 'assistant',
            'content': content,
            'timestamp': time.time()
        }
        
        self.messages.append(message)
        self._update_token_count()
        self._check_compression_needed()
        
        # Guardar en memoria persistente
        self.memory_store.save_message(
            session_id=self.session_id,
            role='assistant',
            content=content,
            model_used=model_used,
            tokens_used=self.current_tokens
        )
    
    def get_context_for_llm(self) -> List[Dict[str, str]]:
        """Obtener contexto formateado para la LLM"""
        # Convertir mensajes al formato requerido por la LLM
        formatted_messages = []
        
        for message in self.messages:
            formatted_messages.append({
                'role': message['role'],
                'content': message['content']
            })
        
        return formatted_messages
    
    def get_token_count(self) -> int:
        """Obtener conteo aproximado de tokens"""
        return self.current_tokens
    
    def _update_token_count(self):
        """Actualizar conteo de tokens (aproximado)"""
        # Estimación simple: ~4 caracteres por token
        total_chars = sum(len(msg['content']) for msg in self.messages)
        self.current_tokens = total_chars // 4
    
    def _check_compression_needed(self):
        """Verificar si se necesita comprimir el contexto"""
        max_tokens = self.settings.context['max_tokens']
        threshold = self.settings.context['compression_threshold']
        
        if self.current_tokens > (max_tokens * threshold):
            self._compress_context()
    
    def _compress_context(self):
        """Comprimir contexto manteniendo mensajes recientes"""
        if len(self.messages) <= 4:  # Mantener mínimo de mensajes
            return
        
        # Mantener los últimos mensajes
        recent_messages = self.messages[-4:]
        
        # Comprimir mensajes antiguos
        old_messages = self.messages[:-4]
        
        if old_messages:
            # Crear resumen de mensajes antiguos
            summary = self._create_summary(old_messages)
            
            # Crear nuevo contexto
            compressed_messages = [{
                'role': 'system',
                'content': f"Resumen de conversación anterior: {summary}",
                'timestamp': time.time()
            }]
            
            # Agregar mensajes recientes
            compressed_messages.extend(recent_messages)
            
            # Reemplazar contexto
            self.messages = compressed_messages
            self._update_token_count()
            
            print("🗜️ Contexto comprimido automáticamente")
    
    def _create_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Crear resumen de mensajes antiguos"""
        # Resumen básico - podría mejorarse con LLM
        summary_parts = []
        
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        assistant_messages = [msg for msg in messages if msg['role'] == 'assistant']
        
        if user_messages:
            summary_parts.append(f"Usuario preguntó sobre: {', '.join(msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content'] for msg in user_messages[-3:])}")
        
        if assistant_messages:
            summary_parts.append(f"Se discutieron temas de: programación, análisis de código, y desarrollo")
        
        return ". ".join(summary_parts)
    
    def clear_context(self):
        """Limpiar contexto completamente"""
        self.messages = []
        self.current_tokens = 0
        self._save_context()
    
    def get_context_summary(self) -> str:
        """Obtener resumen del contexto actual"""
        session_duration = time.time() - self.session_start
        
        summary = f"📊 Resumen del contexto:\n"
        summary += f"  • Mensajes: {len(self.messages)}\n"
        summary += f"  • Tokens estimados: {self.current_tokens}/{self.settings.context['max_tokens']}\n"
        summary += f"  • Duración de sesión: {session_duration/60:.1f} minutos\n"
        
        if self.messages:
            last_message = self.messages[-1]
            summary += f"  • Último mensaje: {last_message['role']} ({time.ctime(last_message['timestamp'])})\n"
        
        return summary
    
    def _save_context(self):
        """Guardar contexto a archivo"""
        try:
            context_data = {
                'messages': self.messages,
                'session_start': self.session_start,
                'saved_at': time.time()
            }
            
            with open(self.settings.files['context_cache'], 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error guardando contexto: {e}")
    
    def _load_context(self):
        """Cargar contexto desde archivo"""
        try:
            if self.settings.files['context_cache'].exists():
                with open(self.settings.files['context_cache'], 'r', encoding='utf-8') as f:
                    context_data = json.load(f)
                
                # Verificar si el contexto no es muy antiguo (24 horas)
                saved_at = context_data.get('saved_at', 0)
                if time.time() - saved_at < 24 * 3600:  # 24 horas
                    self.messages = context_data.get('messages', [])
                    self.session_start = context_data.get('session_start', time.time())
                    self._update_token_count()
                    
        except Exception as e:
            print(f"⚠️ Error cargando contexto: {e}")
    
    def __del__(self):
        """Guardar contexto al destruir el objeto"""
        self._save_context()