"""
Tests de integración para el sistema conversacional completo
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock

from core.nlp_parser import NLPParser, IntentType, ParsedIntent
from core.conversation_engine import ConversationEngine, ConversationContext
from core.intent_router import IntentRouter
from core.response_generator import ResponseGenerator


class TestConversationalIntegration:
    """Tests de integración del sistema conversacional completo"""
    
    def setup_method(self):
        """Setup antes de cada test"""
        # Componentes principales
        self.nlp_parser = NLPParser()
        self.conversation_engine = ConversationEngine(max_context_turns=5)
        self.intent_router = IntentRouter(self.conversation_engine)
        self.response_generator = ResponseGenerator()
        
        # Mocks para LLM y herramientas
        self.mock_llm = Mock()
        self.mock_tools = {
            "code_analyzer": Mock(),
            "workspace_explorer": Mock(), 
            "file_manager": Mock()
        }
        
        # Configurar router
        self.intent_router.set_llm_interface(self.mock_llm)
        self.intent_router.set_workspace_tools(self.mock_tools)
        
        # Iniciar conversación
        self.session_id = self.conversation_engine.start_conversation()
    
    def test_complete_conversational_flow(self):
        """Test flujo conversacional completo: parse -> route -> generate"""
        user_input = "Analiza este proyecto y encuentra problemas"
        
        # 1. Parse de intención
        parsed_intent = self.nlp_parser.parse(user_input)
        
        assert parsed_intent.intent == IntentType.ANALYZE
        assert parsed_intent.confidence > 0.5
        assert parsed_intent.target is not None or "proyecto" in user_input
        
        # 2. Configurar mock de herramienta
        self.mock_tools["code_analyzer"].analyze_project.return_value = "Encontrados 3 problemas de performance"
        self.mock_tools["code_analyzer"].analyze_project.__name__ = "analyze_project"
        
        # 3. Rutear intención
        route_result = self.intent_router.route_intent(user_input, parsed_intent)
        
        assert route_result["success"] == True
        assert route_result["handled_by"] == "tools"
        assert "problemas" in route_result["response"].lower()
        
        # 4. Generar respuesta formateada
        formatted_result = self.response_generator.generate_response(
            route_result["response"],
            parsed_intent,
            route_result,
            self.conversation_engine.get_context_for_llm()
        )
        
        assert "✅" in formatted_result["formatted_response"] or "🔧" in formatted_result["formatted_response"]
        assert len(formatted_result["metadata"].follow_up_questions) > 0
        assert formatted_result["metadata"].confidence_level in ["high", "medium", "low"]
    
    def test_conversational_context_building(self):
        """Test construcción de contexto conversacional entre turnos"""
        conversation_turns = [
            ("Analiza este proyecto", IntentType.ANALYZE),
            ("Crea una función para optimizar", IntentType.CREATE),
            ("Estado del progreso", IntentType.STATUS)
        ]
        
        for i, (user_input, expected_intent) in enumerate(conversation_turns):
            # Parse
            parsed_intent = self.nlp_parser.parse(user_input)
            assert parsed_intent.intent == expected_intent
            
            # Route (mock response)
            if expected_intent == IntentType.STATUS:
                route_result = self.intent_router.route_intent(user_input, parsed_intent)
                # Status se maneja directamente
                assert route_result["handled_by"] == "direct"
                assert "Estado de la Conversación" in route_result["response"]
            else:
                # Simular respuesta exitosa
                self.conversation_engine.add_turn(
                    user_input, parsed_intent, "Respuesta simulada", 0.5, True
                )
            
            # Verificar contexto
            context = self.conversation_engine.get_context_for_llm()
            assert context["session_duration_minutes"] >= 0
            assert len(context["recent_actions"]) == i + 1
            
            if i > 0:  # Después del primer turno
                assert context["current_task"] is not None
                assert len(context["recent_conversation"]) > 0
    
    def test_error_handling_integration(self):
        """Test manejo de errores en el flujo completo"""
        user_input = "haz algo raro que no existe"
        
        # Parse debería dar UNKNOWN o baja confianza
        parsed_intent = self.nlp_parser.parse(user_input)
        
        # Router debería enviar a LLM
        self.mock_llm.chat.return_value = None  # Simular error LLM
        
        route_result = self.intent_router.route_intent(user_input, parsed_intent)
        
        assert route_result["success"] == False
        assert route_result["handled_by"] == "llm"
        
        # Response generator debería manejar error gracefully
        formatted_result = self.response_generator.generate_response(
            route_result["response"],
            parsed_intent,
            route_result
        )
        
        assert "❌" in formatted_result["formatted_response"] or "💥" in formatted_result["formatted_response"]
        assert formatted_result["metadata"].confidence_level == "low"
        # Error responses should have some form of help
        assert (len(formatted_result["metadata"].suggested_actions) > 0 or 
                len(formatted_result["metadata"].follow_up_questions) > 0 or
                "especí" in formatted_result["presentation"].lower())
    
    def test_llm_integration_with_context(self):
        """Test integración LLM con contexto conversacional"""
        # Simular conversación previa
        prev_input = "Analiza el archivo main.py"
        prev_intent = self.nlp_parser.parse(prev_input)
        self.conversation_engine.add_turn(
            prev_input, prev_intent, "Análisis completado", 1.0, True
        )
        
        # Nueva solicitud relacionada
        user_input = "Optimiza los problemas que encontraste"
        parsed_intent = self.nlp_parser.parse(user_input)
        
        # Configurar mock LLM
        self.mock_llm.chat.return_value = "Optimizaciones aplicadas exitosamente"
        
        # Verificar que router usa contexto
        route_result = self.intent_router.route_intent(user_input, parsed_intent)
        
        # Verificar que LLM fue llamado con contexto
        assert self.mock_llm.chat.called
        call_args = self.mock_llm.chat.call_args
        messages = call_args[0][0]  # Primer argumento es messages
        
        # Verificar que system prompt contiene contexto
        system_message = messages[0]["content"]
        assert "contexto" in system_message.lower() or "target específico" in system_message
        
        # Verificar task_type para model switching
        kwargs = call_args[1]
        assert "task_type" in kwargs
        assert kwargs["task_type"] in ["complex", "coding", "general"]
    
    def test_suggestion_system_integration(self):
        """Test sistema de sugerencias integrado"""
        user_input = "Analiza este código"
        
        # Parse y route
        parsed_intent = self.nlp_parser.parse(user_input)
        
        # Simular respuesta tools
        self.mock_tools["code_analyzer"].analyze_project.return_value = "Análisis completado"
        route_result = self.intent_router.route_intent(user_input, parsed_intent)
        
        # Generar respuesta con sugerencias
        formatted_result = self.response_generator.generate_response(
            route_result["response"],
            parsed_intent,
            route_result,
            self.conversation_engine.get_context_for_llm()
        )
        
        # Verificar sugerencias de continuación
        metadata = formatted_result["metadata"]
        assert len(metadata.follow_up_questions) > 0
        # Verificar que hay sugerencias de seguimiento relevantes
        all_suggestions = metadata.follow_up_questions + metadata.suggested_actions
        assert len(all_suggestions) > 0
        
        # Verificar presentación incluye sugerencias
        presentation = formatted_result["presentation"]
        assert "💡" in presentation or "🤔" in presentation
    
    def test_conversational_persistence(self):
        """Test persistencia de contexto conversacional"""
        # Crear archivo temporal para persistencia
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            # Simular conversación
            user_inputs = [
                "Analiza el proyecto",
                "Crea una función nueva",
                "Estado del desarrollo"
            ]
            
            for user_input in user_inputs:
                parsed_intent = self.nlp_parser.parse(user_input)
                self.conversation_engine.add_turn(
                    user_input, parsed_intent, "Respuesta simulada", 0.5, True
                )
            
            # Guardar contexto
            self.conversation_engine.save_context(temp_path)
            
            # Crear nueva engine y cargar contexto
            new_engine = ConversationEngine()
            new_engine.load_context(temp_path)
            
            # Verificar que contexto se cargó correctamente
            assert new_engine.current_context is not None
            assert len(new_engine.conversation_history) == 3
            assert new_engine.current_context.session_id == self.session_id
            
            # Verificar que contexto es utilizable
            context = new_engine.get_context_for_llm()
            assert len(context["recent_actions"]) > 0
            assert context["current_task"] is not None
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_confidence_threshold_integration(self):
        """Test umbrales de confianza en flujo completo"""
        test_cases = [
            ("Analiza este proyecto completamente", "high"),  # Alta confianza
            ("revisa el código", "medium"),                    # Media confianza  
            ("algo", "low")                                   # Baja confianza
        ]
        
        for user_input, expected_confidence in test_cases:
            # Parse
            parsed_intent = self.nlp_parser.parse(user_input)
            
            # Route según confianza
            if parsed_intent.confidence >= 0.7:
                # Alta confianza -> tools o direct
                expected_handlers = ["tools", "direct"]
            elif parsed_intent.confidence >= 0.4:
                # Media confianza -> puede ir a LLM
                expected_handlers = ["tools", "direct", "llm"]
            else:
                # Baja confianza -> probablemente LLM o error
                expected_handlers = ["llm", "error"]
            
            # Configurar mocks apropiados
            if "analiza" in user_input.lower():
                self.mock_tools["code_analyzer"].analyze_project.return_value = "Análisis OK"
            
            route_result = self.intent_router.route_intent(user_input, parsed_intent)
            
            # Verificar manejo apropiado
            assert route_result["handled_by"] in expected_handlers
            
            # Generate response
            formatted_result = self.response_generator.generate_response(
                route_result["response"],
                parsed_intent,
                route_result
            )
            
            # Verificar confianza en metadata
            confidence_level = formatted_result["metadata"].confidence_level
            if expected_confidence == "high":
                assert confidence_level in ["high", "medium"]
            elif expected_confidence == "low":
                assert confidence_level in ["low", "medium"]
    
    def test_model_switching_integration(self):
        """Test lógica de model switching integrada"""
        test_cases = [
            ("Analiza y optimiza este código complejo", "complex"),  # Reasoning
            ("Crea una función simple", "coding"),                   # Code gen
            ("Estado del proyecto", "general")                       # General
        ]
        
        self.mock_llm.chat.return_value = "Respuesta simulada"
        
        for user_input, expected_task_type in test_cases:
            parsed_intent = self.nlp_parser.parse(user_input)
            
            # Si va a LLM, verificar task_type
            if parsed_intent.confidence < 0.6 or parsed_intent.intent not in [IntentType.STATUS, IntentType.HELP]:
                # Force LLM path
                route_result = self.intent_router.route_intent(user_input, parsed_intent)
                
                if route_result["handled_by"] == "llm":
                    # Verificar que se llamó con task_type correcto
                    call_args = self.mock_llm.chat.call_args
                    if call_args and len(call_args) > 1:
                        kwargs = call_args[1]
                        assert "task_type" in kwargs
                        assert kwargs["task_type"] == expected_task_type


class TestConversationalRealFlow:
    """Tests de flujo real sin mocks (para verificar integración total)"""
    
    def setup_method(self):
        """Setup básico sin mocks"""
        self.nlp_parser = NLPParser()
        self.conversation_engine = ConversationEngine()
        self.intent_router = IntentRouter(self.conversation_engine)
        self.response_generator = ResponseGenerator()
        
        self.session_id = self.conversation_engine.start_conversation()
    
    def test_direct_handling_flow(self):
        """Test flujo directo (STATUS, HELP) sin dependencias externas"""
        test_cases = [
            ("Estado del proyecto", IntentType.STATUS),
            ("Ayuda con comandos", IntentType.HELP)
        ]
        
        for user_input, expected_intent in test_cases:
            # Parse
            parsed_intent = self.nlp_parser.parse(user_input)
            assert parsed_intent.intent == expected_intent
            
            # Route (debería manejar directamente)
            route_result = self.intent_router.route_intent(user_input, parsed_intent)
            
            assert route_result["success"] == True
            assert route_result["handled_by"] == "direct"
            assert len(route_result["response"]) > 0
            
            # Generate response
            formatted_result = self.response_generator.generate_response(
                route_result["response"],
                parsed_intent,
                route_result,
                self.conversation_engine.get_context_for_llm()
            )
            
            assert formatted_result["metadata"].confidence_level in ["high", "medium"]
            assert len(formatted_result["presentation"]) > len(route_result["response"])
    
    def test_parser_suggestions_flow(self):
        """Test flujo de sugerencias cuando confianza es baja"""
        ambiguous_inputs = [
            "esto no funciona",
            "hay un problema", 
            "necesito ayuda con algo"
        ]
        
        for user_input in ambiguous_inputs:
            # Parse debería dar baja confianza
            parsed_intent = self.nlp_parser.parse(user_input)
            
            # Verificar sugerencias del parser
            suggestions = self.nlp_parser.get_suggestions(user_input)
            
            if not self.nlp_parser.is_confident(parsed_intent):
                assert len(suggestions) > 0
                assert all(isinstance(s, str) for s in suggestions)
                
                # Response generator debería crear respuesta de error con sugerencias
                error_response = self.response_generator.create_error_response(
                    "No pude entender tu solicitud completamente",
                    parsed_intent,
                    suggestions
                )
                
                assert "❌" in error_response["formatted_response"]
                assert "💡" in error_response["formatted_response"]
                assert len(error_response["metadata"].suggested_actions) > 0