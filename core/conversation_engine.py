"""
Context Engine para mantener conversaciones fluidas
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from core.nlp_parser import ParsedIntent, IntentType


@dataclass
class ConversationTurn:
    """Un turno de conversación"""
    timestamp: float
    user_input: str
    parsed_intent: ParsedIntent
    response: str
    execution_time: float
    success: bool = True


@dataclass 
class ConversationContext:
    """Contexto de conversación actual"""
    session_id: str
    started_at: float
    current_task: Optional[str] = None
    current_target: Optional[str] = None
    user_preferences: Dict[str, Any] = None
    recent_actions: List[str] = None
    
    def __post_init__(self):
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.recent_actions is None:
            self.recent_actions = []


class ConversationEngine:
    """Motor conversacional para mantener contexto y estado"""
    
    def __init__(self, max_context_turns: int = 10):
        self.max_context_turns = max_context_turns
        self.current_context = None
        self.conversation_history = []
        self.session_start = time.time()
        
    def start_conversation(self, session_id: str = None) -> str:
        """Iniciar nueva conversación"""
        if session_id is None:
            session_id = f"conv_{int(time.time())}"
            
        self.current_context = ConversationContext(
            session_id=session_id,
            started_at=time.time()
        )
        self.conversation_history = []
        
        return session_id
    
    def add_turn(self, user_input: str, parsed_intent: ParsedIntent, 
                 response: str, execution_time: float, success: bool = True):
        """Agregar turno de conversación"""
        turn = ConversationTurn(
            timestamp=time.time(),
            user_input=user_input,
            parsed_intent=parsed_intent,
            response=response,
            execution_time=execution_time,
            success=success
        )
        
        self.conversation_history.append(turn)
        
        # Mantener solo los últimos N turnos
        if len(self.conversation_history) > self.max_context_turns:
            self.conversation_history = self.conversation_history[-self.max_context_turns:]
        
        # Actualizar contexto
        self._update_context(turn)
    
    def _update_context(self, turn: ConversationTurn):
        """Actualizar contexto basado en el último turno"""
        if not self.current_context:
            return
            
        intent = turn.parsed_intent
        
        # Actualizar tarea actual
        if intent.intent in [IntentType.ANALYZE, IntentType.CREATE, IntentType.OPTIMIZE]:
            self.current_context.current_task = intent.intent.value
            if intent.target:
                self.current_context.current_target = intent.target
        
        # Actualizar acciones recientes
        action_desc = f"{intent.intent.value}:{intent.target or 'general'}"
        self.current_context.recent_actions.append(action_desc)
        
        # Mantener solo las últimas 5 acciones
        if len(self.current_context.recent_actions) > 5:
            self.current_context.recent_actions = self.current_context.recent_actions[-5:]
        
        # Aprender preferencias del usuario
        self._learn_preferences(intent)
    
    def _learn_preferences(self, intent: ParsedIntent):
        """Aprender preferencias del usuario"""
        if not self.current_context:
            return
            
        prefs = self.current_context.user_preferences
        
        # Contar frecuencia de intents
        intent_key = f"intent_{intent.intent.value}"
        prefs[intent_key] = prefs.get(intent_key, 0) + 1
        
        # Targets preferidos
        if intent.target:
            target_key = "preferred_targets"
            if target_key not in prefs:
                prefs[target_key] = {}
            prefs[target_key][intent.target] = prefs[target_key].get(intent.target, 0) + 1
        
        # Detalles de acción
        if intent.action_details:
            for key, value in intent.action_details.items():
                detail_key = f"pref_{key}_{value}"
                prefs[detail_key] = prefs.get(detail_key, 0) + 1
    
    def get_context_for_llm(self) -> Dict[str, Any]:
        """Obtener contexto optimizado para LLM"""
        if not self.current_context:
            return {}
        
        # Contexto comprimido y específico
        recent_turns = self.conversation_history[-3:]  # Solo últimos 3 turnos
        
        return {
            "session_duration_minutes": (time.time() - self.current_context.started_at) / 60,
            "current_task": self.current_context.current_task,
            "current_target": self.current_context.current_target,
            "recent_actions": self.current_context.recent_actions[-3:],
            "recent_conversation": [
                {
                    "user": turn.user_input,
                    "intent": turn.parsed_intent.intent.value,
                    "success": turn.success
                }
                for turn in recent_turns
            ],
            "user_patterns": self._get_user_patterns(),
            "suggested_continuations": self._get_suggested_continuations()
        }
    
    def _get_user_patterns(self) -> Dict[str, Any]:
        """Analizar patrones del usuario"""
        if not self.current_context:
            return {}
            
        prefs = self.current_context.user_preferences
        
        # Intent más frecuente
        intent_counts = {k: v for k, v in prefs.items() if k.startswith("intent_")}
        most_common_intent = max(intent_counts.items(), key=lambda x: x[1])[0].replace("intent_", "") if intent_counts else None
        
        # Target más frecuente
        preferred_targets = prefs.get("preferred_targets", {})
        most_common_target = max(preferred_targets.items(), key=lambda x: x[1])[0] if preferred_targets else None
        
        return {
            "most_common_intent": most_common_intent,
            "most_common_target": most_common_target,
            "total_interactions": len(self.conversation_history)
        }
    
    def _get_suggested_continuations(self) -> List[str]:
        """Sugerir continuaciones basadas en contexto"""
        if not self.current_context or not self.conversation_history:
            return []
        
        suggestions = []
        last_turn = self.conversation_history[-1]
        
        # Sugerencias basadas en el último intent
        if last_turn.parsed_intent.intent == IntentType.ANALYZE:
            suggestions.extend([
                "¿Quieres que optimice los problemas encontrados?",
                "¿Te interesa ver métricas específicas?",
                "¿Debo crear un reporte detallado?"
            ])
        elif last_turn.parsed_intent.intent == IntentType.CREATE:
            suggestions.extend([
                "¿Quieres que analice lo que creé?",
                "¿Debo generar tests para esto?",
                "¿Te ayudo a integrarlo con el proyecto?"
            ])
        elif last_turn.parsed_intent.intent == IntentType.OPTIMIZE:
            suggestions.extend([
                "¿Quieres que analice el resultado?",
                "¿Debo hacer más optimizaciones?",
                "¿Te interesa ver las métricas de mejora?"
            ])
        
        return suggestions[:2]  # Máximo 2 sugerencias
    
    def is_continuation_of_task(self, new_intent: ParsedIntent) -> bool:
        """Verificar si es continuación de tarea actual"""
        if not self.current_context or not self.current_context.current_task:
            return False
        
        # Misma tarea y mismo target
        if (new_intent.intent.value == self.current_context.current_task and 
            new_intent.target == self.current_context.current_target):
            return True
        
        # Tareas relacionadas
        related_tasks = {
            "analyze": ["optimize", "explain"],
            "create": ["analyze", "test"],
            "optimize": ["analyze", "test"]
        }
        
        current_task = self.current_context.current_task
        if current_task in related_tasks:
            return new_intent.intent.value in related_tasks[current_task]
        
        return False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Obtener resumen de la sesión"""
        if not self.current_context:
            return {}
        
        successful_turns = [t for t in self.conversation_history if t.success]
        failed_turns = [t for t in self.conversation_history if not t.success]
        
        avg_execution_time = (
            sum(t.execution_time for t in self.conversation_history) / 
            len(self.conversation_history)
        ) if self.conversation_history else 0
        
        return {
            "session_id": self.current_context.session_id,
            "duration_minutes": (time.time() - self.current_context.started_at) / 60,
            "total_turns": len(self.conversation_history),
            "successful_turns": len(successful_turns),
            "failed_turns": len(failed_turns),
            "success_rate": len(successful_turns) / len(self.conversation_history) if self.conversation_history else 0,
            "avg_execution_time": avg_execution_time,
            "current_task": self.current_context.current_task,
            "user_patterns": self._get_user_patterns()
        }
    
    def save_context(self, filepath: str):
        """Guardar contexto en archivo"""
        if not self.current_context:
            return
            
        data = {
            "context": asdict(self.current_context),
            "conversation_history": [asdict(turn) for turn in self.conversation_history],
            "session_start": self.session_start
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_context(self, filepath: str):
        """Cargar contexto desde archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruir contexto
            self.current_context = ConversationContext(**data["context"])
            self.session_start = data["session_start"]
            
            # Reconstruir historial (simplificado)
            self.conversation_history = []
            for turn_data in data["conversation_history"]:
                # Crear ParsedIntent simplificado
                intent_data = turn_data["parsed_intent"]
                
                # Extraer enum correctamente - handle both string values and IntentType names
                intent_value = intent_data["intent"]
                if isinstance(intent_value, str):
                    if intent_value.startswith("IntentType."):
                        intent_value = intent_value.replace("IntentType.", "")
                    # Map enum names to values
                    intent_name_to_value = {
                        "ANALYZE": "analyze",
                        "CREATE": "create", 
                        "MODIFY": "modify",
                        "FIND": "find",
                        "EXPLAIN": "explain",
                        "OPTIMIZE": "optimize",
                        "TEST": "test",
                        "STATUS": "status",
                        "HELP": "help",
                        "UNKNOWN": "unknown"
                    }
                    if intent_value in intent_name_to_value:
                        intent_value = intent_name_to_value[intent_value]
                
                parsed_intent = ParsedIntent(
                    intent=IntentType(intent_value),
                    confidence=intent_data["confidence"],
                    target=intent_data.get("target"),
                    action_details=intent_data.get("action_details", {}),
                    original_text=intent_data.get("original_text", "")
                )
                
                turn = ConversationTurn(
                    timestamp=turn_data["timestamp"],
                    user_input=turn_data["user_input"],
                    parsed_intent=parsed_intent,
                    response=turn_data["response"],
                    execution_time=turn_data["execution_time"],
                    success=turn_data.get("success", True)
                )
                self.conversation_history.append(turn)
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Si falla la carga, iniciar contexto limpio
            self.start_conversation()