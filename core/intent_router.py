"""
Intent Router para mapear conversación → acciones del sistema
"""

import time
from typing import Dict, Optional, Any, Callable
from core.nlp_parser import ParsedIntent, IntentType
from core.conversation_engine import ConversationEngine


class IntentRouter:
    """Router de intenciones para decidir cómo procesar cada intent"""
    
    def __init__(self, conversation_engine: ConversationEngine):
        self.conversation_engine = conversation_engine
        self.direct_handlers = {}
        self.llm_interface = None
        self.workspace_tools = {}
        
        # Configurar handlers directos
        self._setup_direct_handlers()
    
    def _setup_direct_handlers(self):
        """Configurar handlers que no necesitan LLM"""
        self.direct_handlers = {
            IntentType.STATUS: self._handle_status,
            IntentType.HELP: self._handle_help,
        }
    
    def set_llm_interface(self, llm_interface):
        """Configurar interfaz LLM"""
        self.llm_interface = llm_interface
    
    def set_workspace_tools(self, tools: Dict[str, Any]):
        """Configurar herramientas del workspace"""
        self.workspace_tools = tools
    
    def route_intent(self, user_input: str, parsed_intent: ParsedIntent) -> Dict[str, Any]:
        """Rutear intent y devolver respuesta"""
        start_time = time.time()
        
        try:
            # 1. Verificar si puede manejarse directamente
            if self._can_handle_directly(parsed_intent):
                response = self._handle_directly(parsed_intent)
                execution_time = time.time() - start_time
                
                # Registrar en conversación
                self.conversation_engine.add_turn(
                    user_input, parsed_intent, response, execution_time, True
                )
                
                return {
                    "response": response,
                    "handled_by": "direct",
                    "execution_time": execution_time,
                    "success": True
                }
            
            # 2. Verificar si puede manejarse con workspace tools
            elif self._can_handle_with_tools(parsed_intent):
                response = self._handle_with_tools(parsed_intent)
                execution_time = time.time() - start_time
                
                self.conversation_engine.add_turn(
                    user_input, parsed_intent, response, execution_time, True
                )
                
                return {
                    "response": response,
                    "handled_by": "tools",
                    "execution_time": execution_time,
                    "success": True
                }
            
            # 3. Enviar a LLM con contexto enriquecido
            else:
                response = self._handle_with_llm(user_input, parsed_intent)
                execution_time = time.time() - start_time
                
                success = response is not None
                self.conversation_engine.add_turn(
                    user_input, parsed_intent, response or "Error en LLM", execution_time, success
                )
                
                return {
                    "response": response or "Lo siento, hubo un error procesando tu solicitud.",
                    "handled_by": "llm",
                    "execution_time": execution_time,
                    "success": success
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_response = f"Error procesando solicitud: {str(e)}"
            
            self.conversation_engine.add_turn(
                user_input, parsed_intent, error_response, execution_time, False
            )
            
            return {
                "response": error_response,
                "handled_by": "error",
                "execution_time": execution_time,
                "success": False
            }
    
    def _can_handle_directly(self, parsed_intent: ParsedIntent) -> bool:
        """Verificar si puede manejarse sin LLM ni tools"""
        return (
            parsed_intent.intent in self.direct_handlers and
            parsed_intent.confidence >= 0.7
        )
    
    def _can_handle_with_tools(self, parsed_intent: ParsedIntent) -> bool:
        """Verificar si puede manejarse con workspace tools"""
        if parsed_intent.confidence < 0.6:
            return False
            
        # Intents que pueden manejarse con tools del workspace
        tool_intents = {
            IntentType.ANALYZE: "code_analyzer",
            IntentType.FIND: "workspace_explorer", 
            IntentType.CREATE: "file_manager"
        }
        
        intent_tool = tool_intents.get(parsed_intent.intent)
        return intent_tool is not None and intent_tool in self.workspace_tools
    
    def _handle_directly(self, parsed_intent: ParsedIntent) -> str:
        """Manejar intent directamente sin LLM"""
        handler = self.direct_handlers.get(parsed_intent.intent)
        if handler:
            return handler(parsed_intent)
        return "Intent no soportado para manejo directo"
    
    def _handle_status(self, parsed_intent: ParsedIntent) -> str:
        """Manejar intent de status"""
        if not self.conversation_engine.current_context:
            return "📊 **Estado**: No hay conversación activa"
        
        summary = self.conversation_engine.get_session_summary()
        context = self.conversation_engine.get_context_for_llm()
        
        response = f"""📊 **Estado de la Conversación**

⏱️ **Duración**: {summary['duration_minutes']:.1f} minutos
🔢 **Turnos**: {summary['total_turns']} ({summary['successful_turns']} exitosos)
⚡ **Tiempo promedio**: {summary['avg_execution_time']:.2f}s
✅ **Tasa de éxito**: {summary['success_rate']:.1%}

🎯 **Contexto Actual**:
• **Tarea**: {context.get('current_task', 'Ninguna')}
• **Objetivo**: {context.get('current_target', 'Ninguno')}
• **Acciones recientes**: {', '.join(context.get('recent_actions', []))}"""

        # Agregar sugerencias si las hay
        suggestions = context.get('suggested_continuations', [])
        if suggestions:
            response += f"\n\n💡 **Sugerencias**:\n" + "\n".join(f"• {s}" for s in suggestions)
        
        return response
    
    def _handle_help(self, parsed_intent: ParsedIntent) -> str:
        """Manejar intent de ayuda"""
        base_help = """🤖 **LocalClaude - Ayuda Conversacional**

Puedes hablar conmigo naturalmente:

🔍 **Análisis**:
• "Analiza este proyecto"
• "Qué problemas tiene el código"
• "Revisa el performance"

🏗️ **Creación**:
• "Crea una nueva función"
• "Genera una API REST"
• "Hacer un proyecto Python"

🔧 **Optimización**:
• "Optimiza este código"
• "Mejora el performance"
• "Acelera la función X"

📊 **Estado**:
• "Estado del proyecto"
• "Métricas del sistema"
• "Progreso actual"

🔎 **Búsqueda**:
• "Busca la función main"
• "Dónde está definida la clase X"

💡 **Ejemplo**: En lugar de `/analyze --metrics performance`, simplemente di "Analiza el performance de este proyecto"
"""
        
        # Contexto específico si está en una conversación
        if self.conversation_engine.current_context:
            context = self.conversation_engine.get_context_for_llm()
            if context.get('current_task'):
                base_help += f"\n🎯 **Contexto actual**: Estás trabajando en {context['current_task']}"
                
                suggestions = context.get('suggested_continuations', [])
                if suggestions:
                    base_help += f"\n💡 **Puedes continuar con**: {suggestions[0]}"
        
        return base_help
    
    def _handle_with_tools(self, parsed_intent: ParsedIntent) -> str:
        """Manejar intent con herramientas del workspace"""
        try:
            if parsed_intent.intent == IntentType.ANALYZE:
                analyzer = self.workspace_tools.get("code_analyzer")
                if analyzer and hasattr(analyzer, 'analyze_project'):
                    target = parsed_intent.target or "."
                    result = analyzer.analyze_project(target)
                    return f"📊 **Análisis completado**:\n{result}"
            
            elif parsed_intent.intent == IntentType.FIND:
                explorer = self.workspace_tools.get("workspace_explorer")
                if explorer and hasattr(explorer, 'find_files'):
                    target = parsed_intent.target or "*"
                    result = explorer.find_files(target)
                    return f"🔍 **Búsqueda completada**:\n{result}"
            
            elif parsed_intent.intent == IntentType.CREATE:
                file_manager = self.workspace_tools.get("file_manager")
                if file_manager and hasattr(file_manager, 'create_file'):
                    target = parsed_intent.target or "new_file.py"
                    file_type = parsed_intent.action_details.get("type", "python")
                    result = file_manager.create_file(target, file_type)
                    return f"📁 **Archivo creado**:\n{result}"
            
            return "Herramienta no disponible para este intent"
            
        except Exception as e:
            return f"Error usando herramientas: {str(e)}"
    
    def _handle_with_llm(self, user_input: str, parsed_intent: ParsedIntent) -> Optional[str]:
        """Manejar intent con LLM"""
        if not self.llm_interface:
            return "LLM no configurado"
        
        try:
            # Obtener contexto optimizado
            context = self.conversation_engine.get_context_for_llm()
            
            # Construir prompt optimizado para DeepSeek
            system_prompt = self._build_optimized_prompt(parsed_intent, context)
            
            # Preparar mensajes
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Determinar task_type para model switching
            task_type = self._get_task_type(parsed_intent)
            
            # Llamar a LLM
            response = self.llm_interface.chat(messages, task_type=task_type)
            
            return response
            
        except Exception as e:
            return f"Error en LLM: {str(e)}"
    
    def _build_optimized_prompt(self, parsed_intent: ParsedIntent, context: Dict) -> str:
        """Construir prompt optimizado para DeepSeek"""
        prompt_parts = []
        
        # 1. Identidad conversacional
        prompt_parts.append("Eres LocalClaude, un asistente conversacional para desarrollo. Responde de forma natural y útil.")
        
        # 2. Intent específico
        intent_prompts = {
            IntentType.ANALYZE: "El usuario quiere que analices código/proyecto. Enfócate en findings específicos y sugerencias.",
            IntentType.CREATE: "El usuario quiere crear algo. Pregunta detalles si necesitas y genera contenido útil.",
            IntentType.OPTIMIZE: "El usuario quiere optimizar algo. Identifica bottlenecks y sugiere mejoras específicas.",
            IntentType.EXPLAIN: "El usuario quiere explicación. Sé claro, didáctico y da ejemplos.",
            IntentType.FIND: "El usuario busca algo. Ayúdale a localizar lo que necesita."
        }
        
        if parsed_intent.intent in intent_prompts:
            prompt_parts.append(intent_prompts[parsed_intent.intent])
        
        # 3. Contexto de conversación
        if context.get('current_task'):
            prompt_parts.append(f"Contexto: El usuario está trabajando en {context['current_task']}")
        
        if context.get('recent_actions'):
            recent = ', '.join(context['recent_actions'][-2:])
            prompt_parts.append(f"Acciones recientes: {recent}")
        
        # 4. Target específico
        if parsed_intent.target:
            prompt_parts.append(f"Target específico: {parsed_intent.target}")
        
        # 5. Instrucciones de respuesta
        prompt_parts.append("Responde de forma conversacional, no como comando. Si necesitas acción específica, sé proactivo.")
        
        return "\n\n".join(prompt_parts)
    
    def _get_task_type(self, parsed_intent: ParsedIntent) -> str:
        """Determinar task_type para model switching"""
        if parsed_intent.intent in [IntentType.ANALYZE, IntentType.OPTIMIZE]:
            return "complex"  # DeepSeek para reasoning
        elif parsed_intent.intent in [IntentType.CREATE, IntentType.EXPLAIN]:
            return "coding"   # Modelo rápido para generación
        else:
            return "general"  # Default