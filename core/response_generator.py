"""
Response Generator para formatear respuestas naturales y sugerencias
"""

import re
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from core.nlp_parser import ParsedIntent, IntentType


@dataclass
class ResponseMetadata:
    """Metadatos de respuesta generada"""
    generation_time: float
    suggested_actions: List[str]
    confidence_level: str  # "high", "medium", "low"
    follow_up_questions: List[str]
    proactive_suggestions: List[str]


class ResponseGenerator:
    """Generador de respuestas naturales y sugerencias proactivas"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.suggestion_patterns = self._load_suggestion_patterns()
    
    def _load_response_templates(self) -> Dict[str, Dict]:
        """Cargar plantillas de respuesta para diferentes contextos"""
        return {
            "success": {
                "direct_action": [
                    "✅ {action} completado exitosamente",
                    "🎯 {action} realizado correctamente",
                    "✨ {action} terminado sin problemas"
                ],
                "llm_response": [
                    "🤖 Aquí tienes la respuesta:",
                    "💡 He analizado tu solicitud:",
                    "📋 Basándome en tu petición:"
                ],
                "tool_response": [
                    "🔧 Herramientas ejecutadas:",
                    "⚙️ Resultado de las operaciones:",
                    "🛠️ Operación completada:"
                ]
            },
            "error": {
                "parsing_error": [
                    "❌ No pude entender completamente tu solicitud",
                    "🤔 Tu mensaje no es muy claro para mí",
                    "⚠️ Necesito más información para ayudarte"
                ],
                "execution_error": [
                    "💥 Hubo un error ejecutando la acción",
                    "🚨 Se produjo un problema durante la ejecución",
                    "⚠️ No pude completar la operación"
                ],
                "tool_error": [
                    "🔧 Error en las herramientas",
                    "⚙️ Fallo en el sistema",
                    "🛠️ Problema técnico"
                ]
            },
            "suggestions": {
                "continuation": [
                    "💡 Puedes continuar con:",
                    "🎯 Siguientes pasos sugeridos:",
                    "✨ Te recomiendo:"
                ],
                "clarification": [
                    "🤔 ¿Podrías especificar?",
                    "📝 Para ayudarte mejor, dime:",
                    "🎯 ¿Te refieres a?"
                ]
            }
        }
    
    def _load_suggestion_patterns(self) -> Dict[IntentType, Dict]:
        """Cargar patrones de sugerencias por tipo de intent"""
        return {
            IntentType.ANALYZE: {
                "follow_up": [
                    "¿Quieres que optimice los problemas encontrados?",
                    "¿Te interesa un análisis más detallado de algún área?",
                    "¿Debo generar un reporte con los hallazgos?"
                ],
                "proactive": [
                    "Crear plan de optimización basado en el análisis",
                    "Generar tests para las áreas problemáticas",
                    "Documentar mejores prácticas encontradas"
                ]
            },
            IntentType.CREATE: {
                "follow_up": [
                    "¿Quieres que agregue tests para esto?",
                    "¿Debo integrarlo con el resto del proyecto?",
                    "¿Te ayudo a documentar lo que creé?"
                ],
                "proactive": [
                    "Analizar lo creado para verificar calidad",
                    "Generar documentación automática",
                    "Crear tests unitarios correspondientes"
                ]
            },
            IntentType.OPTIMIZE: {
                "follow_up": [
                    "¿Quieres que analice el impacto de las optimizaciones?",
                    "¿Debo hacer más optimizaciones en otras áreas?",
                    "¿Te interesa ver métricas de mejora?"
                ],
                "proactive": [
                    "Medir performance antes/después",
                    "Buscar otras oportunidades de optimización",
                    "Documentar cambios realizados"
                ]
            },
            IntentType.FIND: {
                "follow_up": [
                    "¿Quieres que analice lo que encontré?",
                    "¿Necesitas buscar algo relacionado?",
                    "¿Te ayudo a entender lo que encontré?"
                ],
                "proactive": [
                    "Analizar contexto de lo encontrado",
                    "Buscar patrones similares",
                    "Explicar funcionalidad encontrada"
                ]
            },
            IntentType.EXPLAIN: {
                "follow_up": [
                    "¿Necesitas más detalles sobre algún aspecto?",
                    "¿Quieres ejemplos prácticos?",
                    "¿Te ayudo con implementación?"
                ],
                "proactive": [
                    "Crear ejemplos de código",
                    "Generar documentación relacionada",
                    "Buscar mejores prácticas"
                ]
            }
        }
    
    def generate_response(
        self, 
        raw_response: str,
        intent: ParsedIntent,
        execution_metadata: Dict[str, Any],
        conversation_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generar respuesta natural formateada con metadatos"""
        start_time = time.time()
        
        # Determinar tipo de respuesta
        response_type = self._determine_response_type(execution_metadata)
        
        # Formatear respuesta principal
        formatted_response = self._format_main_response(
            raw_response, intent, response_type, execution_metadata
        )
        
        # Generar sugerencias
        suggestions = self._generate_suggestions(intent, conversation_context)
        
        # Calcular nivel de confianza
        confidence_level = self._calculate_confidence_level(intent, execution_metadata)
        
        # Generar metadatos
        metadata = ResponseMetadata(
            generation_time=time.time() - start_time,
            suggested_actions=suggestions["actions"],
            confidence_level=confidence_level,
            follow_up_questions=suggestions["follow_up"],
            proactive_suggestions=suggestions["proactive"]
        )
        
        return {
            "formatted_response": formatted_response,
            "metadata": metadata,
            "raw_response": raw_response,
            "suggestions": suggestions,
            "presentation": self._create_presentation(formatted_response, metadata)
        }
    
    def _determine_response_type(self, execution_metadata: Dict[str, Any]) -> str:
        """Determinar tipo de respuesta basado en metadatos de ejecución"""
        if not execution_metadata.get("success", False):
            return "error"
        
        handled_by = execution_metadata.get("handled_by", "unknown")
        
        if handled_by == "direct":
            return "direct_action"
        elif handled_by == "tools":
            return "tool_response"
        elif handled_by == "llm":
            return "llm_response"
        else:
            return "error"
    
    def _format_main_response(
        self, 
        raw_response: str, 
        intent: ParsedIntent, 
        response_type: str,
        execution_metadata: Dict[str, Any]
    ) -> str:
        """Formatear respuesta principal"""
        
        # Si es error, usar plantillas de error
        if response_type == "error" or not execution_metadata.get("success", False):
            error_type = self._classify_error(execution_metadata)
            templates = self.response_templates["error"][error_type]
            prefix = templates[0]  # Usar primera plantilla
            
            return f"{prefix}\n\n{raw_response}"
        
        # Para respuestas exitosas
        if response_type == "direct_action":
            action = intent.intent.value.title()
            templates = self.response_templates["success"]["direct_action"]
            prefix = templates[0].format(action=action)
            
            return f"{prefix}\n\n{raw_response}"
        
        elif response_type == "tool_response":
            templates = self.response_templates["success"]["tool_response"]
            prefix = templates[0]
            
            return f"{prefix}\n\n{raw_response}"
        
        elif response_type == "llm_response":
            templates = self.response_templates["success"]["llm_response"]
            prefix = templates[0]
            
            # Para respuestas LLM, ser más natural
            return f"{prefix}\n\n{raw_response}"
        
        return raw_response
    
    def _classify_error(self, execution_metadata: Dict[str, Any]) -> str:
        """Clasificar tipo de error"""
        error_response = execution_metadata.get("response", "")
        
        if "no pude entender" in error_response.lower():
            return "parsing_error"
        elif "herramientas" in error_response.lower():
            return "tool_error"
        else:
            return "execution_error"
    
    def _generate_suggestions(
        self, 
        intent: ParsedIntent, 
        conversation_context: Dict[str, Any] = None
    ) -> Dict[str, List[str]]:
        """Generar sugerencias inteligentes"""
        if conversation_context is None:
            conversation_context = {}
        
        suggestions = {
            "actions": [],
            "follow_up": [],
            "proactive": []
        }
        
        # Sugerencias específicas por intent
        if intent.intent in self.suggestion_patterns:
            patterns = self.suggestion_patterns[intent.intent]
            suggestions["follow_up"] = patterns.get("follow_up", [])[:2]
            suggestions["proactive"] = patterns.get("proactive", [])[:2]
        
        # Sugerencias basadas en contexto de conversación
        if conversation_context:
            context_suggestions = self._generate_context_suggestions(
                intent, conversation_context
            )
            suggestions["actions"].extend(context_suggestions)
        
        # Sugerencias de continuación de tareas
        if conversation_context.get("current_task"):
            task_suggestions = self._generate_task_continuation_suggestions(
                intent, conversation_context
            )
            suggestions["actions"].extend(task_suggestions)
        
        return suggestions
    
    def _generate_context_suggestions(
        self, 
        intent: ParsedIntent, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generar sugerencias basadas en contexto conversacional"""
        suggestions = []
        
        recent_actions = context.get("recent_actions", [])
        current_task = context.get("current_task")
        
        # Si hay patrón en acciones recientes
        if len(recent_actions) >= 2:
            last_actions = recent_actions[-2:]
            
            # Patrón: analyze -> create
            if "analyze" in last_actions and intent.intent == IntentType.CREATE:
                suggestions.append("Continuar con tests para lo creado")
            
            # Patrón: create -> optimize
            if "create" in last_actions and intent.intent == IntentType.OPTIMIZE:
                suggestions.append("Analizar impacto de optimizaciones")
        
        # Sugerencias basadas en tarea actual
        if current_task:
            if current_task == "analyze" and intent.intent != IntentType.ANALYZE:
                suggestions.append("Volver al análisis iniciado")
            elif current_task == "create" and intent.intent != IntentType.CREATE:
                suggestions.append("Continuar con la creación")
        
        return suggestions[:2]
    
    def _generate_task_continuation_suggestions(
        self, 
        intent: ParsedIntent, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generar sugerencias de continuación de tareas"""
        suggestions = []
        current_task = context.get("current_task")
        current_target = context.get("current_target")
        
        if not current_task:
            return suggestions
        
        # Sugerencias específicas por combinación task + intent
        task_intent_map = {
            ("analyze", IntentType.CREATE): f"Crear solución para {current_target or 'el problema'}",
            ("analyze", IntentType.OPTIMIZE): f"Optimizar {current_target or 'lo analizado'}",
            ("create", IntentType.ANALYZE): f"Analizar calidad de {current_target or 'lo creado'}",
            ("create", IntentType.TEST): f"Crear tests para {current_target or 'lo desarrollado'}",
            ("optimize", IntentType.ANALYZE): f"Verificar mejoras en {current_target or 'lo optimizado'}"
        }
        
        key = (current_task, intent.intent)
        if key in task_intent_map:
            suggestions.append(task_intent_map[key])
        
        return suggestions
    
    def _calculate_confidence_level(
        self, 
        intent: ParsedIntent, 
        execution_metadata: Dict[str, Any]
    ) -> str:
        """Calcular nivel de confianza general"""
        # Confianza de parsing
        parse_confidence = intent.confidence
        
        # Éxito de ejecución
        execution_success = execution_metadata.get("success", False)
        
        # Tiempo de ejecución (rápido = mejor)
        execution_time = execution_metadata.get("execution_time", 0)
        
        # Calcular score general
        score = 0.0
        
        # 40% peso al parsing
        score += parse_confidence * 0.4
        
        # 40% peso al éxito
        if execution_success:
            score += 0.4
        
        # 20% peso al tiempo (inverso)
        if execution_time > 0:
            time_score = max(0, 1 - (execution_time / 10))  # Penalizar >10s
            score += time_score * 0.2
        
        # Clasificar
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _create_presentation(
        self, 
        formatted_response: str, 
        metadata: ResponseMetadata
    ) -> str:
        """Crear presentación final para mostrar al usuario"""
        presentation_parts = [formatted_response]
        
        # Agregar sugerencias si hay
        if metadata.follow_up_questions:
            presentation_parts.append("\n🤔 **Preguntas de seguimiento:**")
            for question in metadata.follow_up_questions:
                presentation_parts.append(f"• {question}")
        
        if metadata.suggested_actions:
            presentation_parts.append("\n💡 **Sugerencias:**")
            for action in metadata.suggested_actions:
                presentation_parts.append(f"• {action}")
        
        # Agregar indicador de confianza si es bajo
        if metadata.confidence_level == "low":
            presentation_parts.append("\n⚠️ *Si necesitas algo diferente, intenta ser más específico*")
        
        return "\n".join(presentation_parts)
    
    def create_error_response(
        self, 
        error_message: str, 
        intent: ParsedIntent = None,
        suggestions: List[str] = None
    ) -> Dict[str, Any]:
        """Crear respuesta de error formateada"""
        if suggestions is None:
            suggestions = [
                "Intenta ser más específico",
                "Verifica que el comando sea válido",
                "Usa 'ayuda' para ver opciones disponibles"
            ]
        
        formatted_response = f"❌ **Error**: {error_message}"
        
        if suggestions:
            formatted_response += "\n\n💡 **Sugerencias:**"
            for suggestion in suggestions:
                formatted_response += f"\n• {suggestion}"
        
        metadata = ResponseMetadata(
            generation_time=0.0,
            suggested_actions=suggestions,
            confidence_level="low",
            follow_up_questions=[],
            proactive_suggestions=[]
        )
        
        return {
            "formatted_response": formatted_response,
            "metadata": metadata,
            "raw_response": error_message,
            "suggestions": {"actions": suggestions, "follow_up": [], "proactive": []},
            "presentation": formatted_response
        }
    
    def enhance_llm_response(
        self, 
        llm_response: str, 
        intent: ParsedIntent,
        conversation_context: Dict[str, Any] = None
    ) -> str:
        """Mejorar respuesta LLM con formato y sugerencias"""
        if not llm_response:
            return llm_response
        
        # Detectar y mejorar formato
        enhanced = self._improve_formatting(llm_response)
        
        # Agregar contexto conversacional si es relevante
        if conversation_context and conversation_context.get("current_task"):
            task = conversation_context["current_task"]
            if task != intent.intent.value:
                enhanced += f"\n\n🔄 *Continuando trabajo en: {task}*"
        
        return enhanced
    
    def _improve_formatting(self, text: str) -> str:
        """Mejorar formato de texto agregando iconos y estructura"""
        # Detectar listas y mejorarlas
        lines = text.split('\n')
        improved_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Mejorar listas simples
            if stripped.startswith('-') or stripped.startswith('*'):
                improved_lines.append(f"• {stripped[1:].strip()}")
            # Detectar títulos (líneas cortas seguidas de contenido)
            elif len(stripped) < 50 and ':' in stripped and not stripped.endswith('.'):
                improved_lines.append(f"**{stripped}**")
            else:
                improved_lines.append(line)
        
        return '\n'.join(improved_lines)