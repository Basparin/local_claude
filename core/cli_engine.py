"""
Motor principal de la CLI LocalClaude
"""

import sys
import os
import time
from typing import Optional, Dict, Any
from pathlib import Path

from core.ollama_interface import OllamaInterface
from core.command_processor import CommandProcessor
from context.context_manager import ContextManager
from context.compression import ContextCompressor
from workspace.explorer import WorkspaceExplorer
from workspace.file_manager import FileManager
from workspace.code_analyzer import CodeAnalyzer
from ui.interface import UserInterface
from config.settings import Settings
from monitoring.metrics import get_metrics_collector

# Conversational system imports
from core.nlp_parser import NLPParser
from core.conversation_engine import ConversationEngine
from core.intent_router import IntentRouter
from core.response_generator import ResponseGenerator

class CLIEngine:
    """Motor principal de la CLI"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.running = False
        
        # Inicializar métricas
        self.metrics = get_metrics_collector()
        
        # Inicializar componentes
        self.ollama = OllamaInterface(settings)
        self.context_manager = ContextManager(settings)
        self.compressor = ContextCompressor(settings, self.ollama)
        self.workspace_explorer = WorkspaceExplorer(settings)
        self.file_manager = FileManager(settings, self.ollama)
        self.code_analyzer = CodeAnalyzer(settings, self.ollama)
        self.command_processor = CommandProcessor(settings)
        self.ui = UserInterface(settings)
        
        # Inicializar sistema conversacional
        self.nlp_parser = NLPParser()
        self.conversation_engine = ConversationEngine(max_context_turns=10)
        self.intent_router = IntentRouter(self.conversation_engine)
        self.response_generator = ResponseGenerator()
        
        # Configurar conversational system
        self._setup_conversational_system()
        
        # Configurar procesador de comandos
        self._setup_command_processor()
    
    def _setup_conversational_system(self):
        """Configurar sistema conversacional"""
        # Configurar intent router con LLM interface
        self.intent_router.set_llm_interface(self.ollama)
        
        # Configurar workspace tools para el router
        workspace_tools = {
            "code_analyzer": self.code_analyzer,
            "workspace_explorer": self.workspace_explorer,
            "file_manager": self.file_manager
        }
        self.intent_router.set_workspace_tools(workspace_tools)
        
        # Iniciar sesión conversacional
        session_id = self.conversation_engine.start_conversation()
        self.ui.show_debug(f"Sesión conversacional iniciada: {session_id}")
    
    def _setup_command_processor(self):
        """Configurar el procesador de comandos"""
        # Registrar comandos del sistema
        self.command_processor.register_command('help', self._cmd_help)
        self.command_processor.register_command('exit', self._cmd_exit)
        self.command_processor.register_command('quit', self._cmd_exit)
        self.command_processor.register_command('status', self._cmd_status)
        self.command_processor.register_command('context', self._cmd_context)
        self.command_processor.register_command('clear', self._cmd_clear)
        self.command_processor.register_command('model', self._cmd_model)
        self.command_processor.register_command('metrics', self._cmd_metrics)
        self.command_processor.register_command('conversation', self._cmd_conversation)
        
        # Registrar comandos de workspace
        self.command_processor.register_command('ls', self._cmd_ls)
        self.command_processor.register_command('cat', self._cmd_cat)
        self.command_processor.register_command('grep', self._cmd_grep)
        self.command_processor.register_command('tree', self._cmd_tree)
        self.command_processor.register_command('find', self._cmd_find)
        
        # Registrar comandos de construcción
        self.command_processor.register_command('create', self._cmd_create)
        self.command_processor.register_command('edit', self._cmd_edit)
        self.command_processor.register_command('build', self._cmd_build)
        self.command_processor.register_command('generate', self._cmd_generate)
        
        # Registrar comandos de análisis
        self.command_processor.register_command('analyze', self._cmd_analyze)
        self.command_processor.register_command('issues', self._cmd_issues)
        self.command_processor.register_command('suggest', self._cmd_suggest)
        self.command_processor.register_command('complexity', self._cmd_complexity)
        
        # Registrar comandos de performance/cache
        self.command_processor.register_command('cache-stats', self._cmd_cache_stats)
        self.command_processor.register_command('cache-clear', self._cmd_cache_clear)
        
        # Registrar comandos de contexto avanzado
        self.command_processor.register_command('compress', self._cmd_compress)
        self.command_processor.register_command('summary', self._cmd_summary)
        
        # Registrar comandos de memoria
        self.command_processor.register_command('history', self._cmd_history)
        self.command_processor.register_command('sessions', self._cmd_sessions)
        self.command_processor.register_command('projects', self._cmd_projects)
        self.command_processor.register_command('stats', self._cmd_stats)
    
    def run(self):
        """Ejecutar la CLI principal"""
        self.running = True
        
        # Mostrar bienvenida
        self.ui.show_welcome()
        
        # Verificar conexión con Ollama
        connection_result = self.ollama.test_connection()
        if not connection_result:
            self.ui.show_error("No se pudo conectar con Ollama. Verifica que esté corriendo.")
            return
        
        # Bucle principal
        while self.running:
            try:
                # Mostrar prompt
                user_input = self.ui.get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Procesar entrada del usuario
                self._process_user_input(user_input)
                
            except KeyboardInterrupt:
                self.ui.show_message("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                self.ui.show_error(f"Error inesperado: {e}")
                if self.settings.cli['debug']:
                    import traceback
                    traceback.print_exc()
    
    def _process_user_input(self, user_input: str):
        """Procesar entrada del usuario"""
        start_time = time.time()
        
        try:
            # Verificar si es un comando especial
            if user_input.startswith(self.settings.cli['command_prefix']):
                # Es un comando especial
                command_name = user_input[1:].split()[0] if len(user_input) > 1 else ''
                command_result = self.command_processor.process_command(user_input)
                
                # Calcular tiempo de ejecución
                execution_time = time.time() - start_time
                
                # Registrar métricas
                self.metrics.log_command(command_name, execution_time, success=True)
                
                if command_result:
                    self.ui.show_message(command_result)
                    
                    # Registrar uso del comando (legacy)
                    if command_name:
                        self.context_manager.memory_store.record_command_usage(
                            command_name, self.context_manager.session_id
                        )
            else:
                # Es una conversación normal
                self._handle_conversation(user_input)
                
        except Exception as e:
            # Registrar error
            execution_time = time.time() - start_time
            command_name = user_input[1:].split()[0] if user_input.startswith(self.settings.cli['command_prefix']) else 'conversation'
            
            self.metrics.log_command(command_name, execution_time, success=False)
            self.metrics.log_error('command_execution', str(e), {'input': user_input})
            
            # Re-lanzar excepción
            raise
    
    def _handle_conversation(self, user_input: str):
        """Manejar conversación con sistema conversacional avanzado"""
        start_time = time.time()
        
        try:
            # 1. Parse de intención usando NLP Parser
            parsed_intent = self.nlp_parser.parse(user_input)
            
            # Log del intent detectado
            if self.settings.cli['debug']:
                self.ui.show_debug(f"Intent detectado: {parsed_intent.intent.value} (confianza: {parsed_intent.confidence:.2f})")
            
            # 2. Router intención a través del Intent Router
            self.ui.show_thinking()
            route_result = self.intent_router.route_intent(user_input, parsed_intent)
            
            # 3. Generar respuesta formateada con Response Generator
            conversation_context = self.conversation_engine.get_context_for_llm()
            formatted_result = self.response_generator.generate_response(
                route_result["response"],
                parsed_intent,
                route_result,
                conversation_context
            )
            
            # 4. Mostrar respuesta al usuario
            self.ui.show_response(formatted_result["presentation"])
            
            # 5. Métricas y logging
            execution_time = time.time() - start_time
            self.metrics.log_command('conversation', execution_time, success=route_result["success"])
            
            # Log adicional para debugging
            if self.settings.cli['debug']:
                self.ui.show_debug(f"Manejado por: {route_result['handled_by']} | Tiempo: {execution_time:.2f}s")
                if formatted_result["metadata"].confidence_level == "low":
                    self.ui.show_debug("⚠️ Respuesta de baja confianza")
            
            # 6. Agregar al contexto legacy si es necesario
            self.context_manager.add_user_message(user_input)
            self.context_manager.add_assistant_message(route_result["response"])
            
        except Exception as e:
            # Manejo de errores con response generator
            error_response = self.response_generator.create_error_response(
                f"Error procesando conversación: {str(e)}",
                parsed_intent if 'parsed_intent' in locals() else None
            )
            
            self.ui.show_error(error_response["presentation"])
            
            # Métricas de error
            execution_time = time.time() - start_time
            self.metrics.log_command('conversation', execution_time, success=False)
            self.metrics.log_error('conversation_error', str(e), {'input': user_input})
            
            if self.settings.cli['debug']:
                import traceback
                traceback.print_exc()
    
    def _select_model_for_task(self, user_input: str) -> str:
        """Seleccionar modelo apropiado para la tarea"""
        # Análisis simple para determinar tipo de tarea
        task_type = self._analyze_task_type(user_input)
        
        if self.settings.should_use_fast_model(task_type):
            return self.settings.models['fast']
        else:
            return self.settings.models['primary']
    
    def _analyze_task_type(self, user_input: str) -> str:
        """Analizar tipo de tarea del usuario"""
        user_input_lower = user_input.lower()
        
        # Tareas simples
        if any(word in user_input_lower for word in ['estado', 'status', 'qué', 'cómo']):
            return 'simple_question'
        
        # Tareas de código
        if any(word in user_input_lower for word in ['código', 'programar', 'función', 'clase']):
            return 'coding'
        
        # Por defecto, tarea compleja
        return 'complex'
    
    # Comandos del sistema
    def _cmd_help(self, args: list) -> str:
        """Mostrar ayuda"""
        return self.ui.get_help_text()
    
    def _cmd_exit(self, args: list) -> str:
        """Salir de la CLI"""
        self.running = False
        return "👋 ¡Hasta luego!"
    
    def _cmd_status(self, args: list) -> str:
        """Mostrar estado del sistema"""
        status = {
            'modelo_actual': self.settings.models['current'],
            'contexto_usado': f"{self.context_manager.get_token_count()}/{self.settings.context['max_tokens']}",
            'directorio_trabajo': str(self.settings.workspace_dir),
            'conexion_ollama': 'OK' if self.ollama.test_connection() else 'ERROR'
        }
        
        result = "📊 Estado del sistema:\n"
        for key, value in status.items():
            result += f"  • {key}: {value}\n"
        
        return result
    
    def _cmd_context(self, args: list) -> str:
        """Mostrar información del contexto"""
        return self.context_manager.get_context_summary()
    
    def _cmd_clear(self, args: list) -> str:
        """Limpiar contexto"""
        self.context_manager.clear_context()
        return "🧹 Contexto limpiado"
    
    def _cmd_model(self, args: list) -> str:
        """Cambiar modelo actual"""
        if not args:
            return f"Modelo actual: {self.settings.models['current']}"
        
        new_model = args[0]
        if self.ollama.test_model(new_model):
            self.settings.models['current'] = new_model
            return f"✅ Modelo cambiado a: {new_model}"
        else:
            return f"❌ Modelo no disponible: {new_model}"
    
    def _cmd_metrics(self, args: list) -> str:
        """Mostrar métricas del sistema"""
        try:
            summary = self.metrics.get_session_summary()
            
            result = "📊 **Métricas de Sesión Actual**\n\n"
            
            # Información general
            duration_mins = summary['session_duration'] / 60
            result += f"⏱️  **Duración**: {duration_mins:.1f} minutos\n"
            result += f"🔢 **Comandos ejecutados**: {summary['commands_executed']}\n"
            result += f"⚡ **Tiempo promedio**: {summary['avg_response_time']:.3f}s\n"
            result += f"❌ **Errores**: {summary['errors_count']}\n\n"
            
            # Cache performance
            result += f"💾 **Cache Hit Rate**: {summary['cache_hit_rate']:.1f}%\n\n"
            
            # Modelos utilizados
            if summary['models_used']:
                result += "🤖 **Modelos utilizados**:\n"
                for model, count in summary['models_used'].items():
                    result += f"  • {model}: {count} veces\n"
            else:
                result += "🤖 **Modelos**: Ninguno usado aún\n"
            
            # Guardar estado actual
            self.metrics.save_current_state()
            
            return result
            
        except Exception as e:
            return f"❌ Error obteniendo métricas: {e}"
    
    def _cmd_conversation(self, args: list) -> str:
        """Mostrar estado del sistema conversacional"""
        try:
            # Obtener contexto conversacional
            context = self.conversation_engine.get_context_for_llm()
            session_summary = self.conversation_engine.get_session_summary()
            
            result = "💬 **Estado del Sistema Conversacional**\n\n"
            
            if self.conversation_engine.current_context:
                # Información de sesión
                result += f"🆔 **Sesión**: {session_summary.get('session_id', 'N/A')}\n"
                result += f"⏱️  **Duración**: {session_summary.get('duration_minutes', 0):.1f} minutos\n"
                result += f"🔢 **Turnos**: {session_summary.get('total_turns', 0)} ({session_summary.get('successful_turns', 0)} exitosos)\n"
                result += f"✅ **Tasa de éxito**: {session_summary.get('success_rate', 0):.1%}\n\n"
                
                # Contexto actual
                result += "🎯 **Contexto Actual**:\n"
                result += f"  • **Tarea**: {context.get('current_task', 'Ninguna')}\n"
                result += f"  • **Target**: {context.get('current_target', 'Ninguno')}\n"
                
                recent_actions = context.get('recent_actions', [])
                if recent_actions:
                    result += f"  • **Acciones recientes**: {', '.join(recent_actions[-3:])}\n"
                
                # Patrones del usuario
                patterns = context.get('user_patterns', {})
                if patterns.get('most_common_intent'):
                    result += f"  • **Intent frecuente**: {patterns['most_common_intent']}\n"
                
                # Sugerencias
                suggestions = context.get('suggested_continuations', [])
                if suggestions:
                    result += "\n💡 **Sugerencias**:\n"
                    for suggestion in suggestions[:2]:
                        result += f"  • {suggestion}\n"
            else:
                result += "❌ No hay sesión conversacional activa\n"
            
            # Configuración del NLP Parser
            result += f"\n🧠 **NLP Parser**: Threshold {self.nlp_parser.confidence_threshold}\n"
            result += f"🔧 **Intent Router**: {len(self.intent_router.direct_handlers)} handlers directos\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error obteniendo estado conversacional: {e}"
    
    # Comandos de workspace
    def _cmd_ls(self, args: list) -> str:
        """Listar archivos"""
        path = args[0] if args else '.'
        return self.workspace_explorer.list_files(path)
    
    def _cmd_cat(self, args: list) -> str:
        """Mostrar contenido de archivo"""
        if not args:
            return "❌ Especifica un archivo: /cat <archivo>"
        
        return self.workspace_explorer.show_file(args[0])
    
    def _cmd_grep(self, args: list) -> str:
        """Buscar patrón en archivos"""
        if not args:
            return "❌ Especifica un patrón: /grep <patrón>"
        
        pattern = args[0]
        path = args[1] if len(args) > 1 else '.'
        return self.workspace_explorer.search_pattern(pattern, path)
    
    def _cmd_tree(self, args: list) -> str:
        """Mostrar estructura de directorios"""
        path = args[0] if args else '.'
        return self.workspace_explorer.show_tree(path)
    
    def _cmd_find(self, args: list) -> str:
        """Buscar archivos"""
        if not args:
            return "❌ Especifica un patrón: /find <patrón>"
        
        return self.workspace_explorer.find_files(args[0])
    
    # Comandos de construcción
    def _cmd_create(self, args: list) -> str:
        """Crear nuevo archivo"""
        if not args:
            return "❌ Especifica un archivo: /create <archivo> [tipo]"
        
        file_path = args[0]
        file_type = args[1] if len(args) > 1 else None
        
        return self.file_manager.create_file(file_path, file_type=file_type)
    
    def _cmd_edit(self, args: list) -> str:
        """Editar archivo existente"""
        if not args:
            return "❌ Especifica un archivo y las instrucciones: /edit <archivo> <instrucciones>"
        
        if len(args) < 2:
            return "❌ Especifica las instrucciones de edición: /edit <archivo> <instrucciones>"
        
        file_path = args[0]
        instructions = ' '.join(args[1:])
        
        return self.file_manager.edit_file(file_path, instructions)
    
    def _cmd_build(self, args: list) -> str:
        """Construir proyecto completo"""
        if len(args) < 2:
            return "❌ Especifica tipo y nombre: /build <tipo> <nombre>"
        
        project_type = args[0]
        project_name = args[1]
        
        return self.file_manager.build_project(project_type, project_name)
    
    def _cmd_generate(self, args: list) -> str:
        """Generar código"""
        if not args:
            return "❌ Especifica qué generar: /generate <descripción> [archivo]"
        
        # Separar descripción y archivo opcional
        if len(args) > 1 and args[-1].endswith(('.py', '.js', '.html', '.css')):
            file_path = args[-1]
            description = ' '.join(args[:-1])
        else:
            file_path = None
            description = ' '.join(args)
        
        return self.file_manager.generate_code(description, file_path)
    
    # Comandos de análisis
    def _cmd_analyze(self, args: list) -> str:
        """Analizar proyecto o archivo"""
        path = args[0] if args else '.'
        
        # Determinar si es archivo o proyecto
        target_path = Path(self.settings.workspace_dir) / path
        
        if target_path.is_file():
            return self.code_analyzer.analyze_file(path)
        else:
            return self.code_analyzer.analyze_project(path)
    
    def _cmd_issues(self, args: list) -> str:
        """Encontrar problemas en el código"""
        path = args[0] if args else '.'
        return self.code_analyzer.find_issues(path)
    
    def _cmd_suggest(self, args: list) -> str:
        """Sugerir mejoras para un archivo"""
        if not args:
            return "❌ Especifica un archivo: /suggest <archivo>"
        
        return self.code_analyzer.suggest_improvements(args[0])
    
    def _cmd_complexity(self, args: list) -> str:
        """Calcular complejidad de código"""
        if not args:
            return "❌ Especifica un archivo Python: /complexity <archivo.py>"
        
        return self.code_analyzer.calculate_complexity(args[0])
    
    # Comandos de contexto avanzado
    def _cmd_compress(self, args: list) -> str:
        """Comprimir contexto manualmente"""
        original_count = len(self.context_manager.messages)
        
        if original_count <= 4:
            return "📋 El contexto ya es pequeño, no es necesario comprimir"
        
        # Comprimir contexto
        compressed_messages = self.compressor.compress_messages(self.context_manager.messages)
        self.context_manager.messages = compressed_messages
        self.context_manager._update_token_count()
        
        new_count = len(compressed_messages)
        saved = original_count - new_count
        
        return f"🗜️ Contexto comprimido: {original_count} → {new_count} mensajes (ahorrados: {saved})"
    
    def _cmd_summary(self, args: list) -> str:
        """Crear resumen de la sesión"""
        if not self.context_manager.messages:
            return "📋 No hay mensajes para resumir"
        
        summary = self.compressor.create_session_summary(self.context_manager.messages)
        return f"📊 **Resumen de la sesión:**\n\n{summary}"
    
    # Comandos de memoria
    def _cmd_history(self, args: list) -> str:
        """Mostrar historial de archivos o comandos"""
        if not args:
            # Mostrar historial de archivos reciente
            history = self.context_manager.memory_store.get_file_history(limit=10)
            
            if not history:
                return "📋 No hay historial de archivos"
            
            result = "📋 **Historial de archivos reciente:**\n\n"
            for entry in history:
                timestamp = time.strftime('%H:%M:%S', time.localtime(entry['timestamp']))
                result += f"• {timestamp} - {entry['action']} {entry['file_path']}\n"
            
            return result
        
        elif args[0] == 'commands':
            # Mostrar comandos populares
            commands = self.context_manager.memory_store.get_popular_commands()
            
            if not commands:
                return "📋 No hay historial de comandos"
            
            result = "📋 **Comandos más utilizados:**\n\n"
            for cmd in commands:
                result += f"• {cmd['command']} - {cmd['usage_count']} veces\n"
            
            return result
        
        else:
            return "❌ Uso: /history [commands]"
    
    def _cmd_sessions(self, args: list) -> str:
        """Mostrar sesiones recientes"""
        limit = 5
        if args and args[0].isdigit():
            limit = int(args[0])
        
        sessions = self.context_manager.memory_store.get_recent_sessions(
            workspace_path=str(self.settings.workspace_dir),
            limit=limit
        )
        
        if not sessions:
            return "📋 No hay sesiones previas en este workspace"
        
        result = f"📋 **Últimas {len(sessions)} sesiones:**\n\n"
        
        for session in sessions:
            start_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(session['start_time']))
            duration = ""
            
            if session['end_time']:
                duration_sec = session['end_time'] - session['start_time']
                duration = f" ({duration_sec/60:.1f} min)"
            
            result += f"• {start_time}{duration} - {session['total_messages']} mensajes\n"
            
            if session['summary']:
                result += f"  📄 {session['summary'][:80]}...\n"
            
            result += "\n"
        
        return result
    
    def _cmd_projects(self, args: list) -> str:
        """Mostrar proyectos recientes"""
        projects = self.context_manager.memory_store.get_recent_projects(limit=10)
        
        if not projects:
            return "📋 No hay proyectos registrados"
        
        result = "📋 **Proyectos recientes:**\n\n"
        
        for project in projects:
            last_access = time.strftime('%Y-%m-%d', time.localtime(project['last_accessed']))
            
            result += f"• **{project['project_name']}**\n"
            result += f"  📁 {project['project_path']}\n"
            result += f"  📅 Último acceso: {last_access}\n"
            
            if project.get('project_type'):
                result += f"  🏷️ Tipo: {project['project_type']}\n"
            
            if project.get('languages'):
                result += f"  💻 Lenguajes: {', '.join(project['languages'])}\n"
            
            if project.get('files_count'):
                result += f"  📄 Archivos: {project['files_count']}\n"
            
            result += "\n"
        
        return result
    
    def _cmd_stats(self, args: list) -> str:
        """Mostrar estadísticas de memoria"""
        stats = self.context_manager.memory_store.get_memory_stats()
        
        result = "📊 **Estadísticas de LocalClaude:**\n\n"
        result += f"💬 Sesiones totales: {stats['total_sessions']}\n"
        result += f"📝 Mensajes totales: {stats['total_messages']}\n"
        result += f"📁 Proyectos registrados: {stats['total_projects']}\n"
        result += f"📄 Archivos únicos trabajados: {stats['unique_files']}\n"
        
        if stats.get('most_used_command'):
            cmd_info = stats['most_used_command']
            result += f"🔥 Comando más usado: {cmd_info['command']} ({cmd_info['count']} veces)\n"
        
        # Tamaño de base de datos
        db_size = stats['db_size']
        if db_size > 1024 * 1024:
            size_str = f"{db_size/(1024*1024):.1f} MB"
        elif db_size > 1024:
            size_str = f"{db_size/1024:.1f} KB"
        else:
            size_str = f"{db_size} B"
        
        result += f"💾 Tamaño de memoria: {size_str}\n"
        
        return result
    
    def _cmd_cache_stats(self, args: list) -> str:
        """Mostrar estadísticas del cache de análisis"""
        return self.code_analyzer.get_cache_stats()
    
    def _cmd_cache_clear(self, args: list) -> str:
        """Limpiar cache de análisis"""
        return self.code_analyzer.clear_analysis_cache()