"""
Sistema de compresión avanzada de contexto
"""

import json
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

class ContextCompressor:
    """Compresor inteligente de contexto de conversaciones"""
    
    def __init__(self, settings, ollama_interface):
        self.settings = settings
        self.ollama_interface = ollama_interface
        self.compression_strategies = [
            self._compress_repetitive_content,
            self._compress_code_blocks,
            self._compress_file_listings,
            self._compress_similar_questions,
            self._extract_key_decisions
        ]
    
    def compress_messages(self, messages: List[Dict[str, Any]], target_reduction: float = 0.5) -> List[Dict[str, Any]]:
        """
        Comprimir lista de mensajes manteniendo información importante
        
        Args:
            messages: Lista de mensajes a comprimir
            target_reduction: Porcentaje objetivo de reducción (0.5 = 50%)
        
        Returns:
            Lista de mensajes comprimidos
        """
        if len(messages) <= 4:  # No comprimir si hay pocos mensajes
            return messages
        
        # Separar mensajes recientes (mantener sin comprimir)
        recent_messages = messages[-2:]  # Últimos 2 mensajes
        old_messages = messages[:-2]     # Mensajes antiguos
        
        if not old_messages:
            return messages
        
        # Comprimir mensajes antiguos
        compressed_summary = self._create_intelligent_summary(old_messages)
        
        # Crear nuevo contexto
        compressed_messages = [
            {
                'role': 'system',
                'content': f"📋 Resumen de conversación anterior:\n{compressed_summary}",
                'timestamp': time.time(),
                'compressed': True
            }
        ]
        
        # Agregar mensajes recientes sin comprimir
        compressed_messages.extend(recent_messages)
        
        return compressed_messages
    
    def create_session_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        Crear resumen completo de una sesión
        
        Args:
            messages: Mensajes de la sesión
        
        Returns:
            Resumen detallado de la sesión
        """
        if not messages:
            return "Sesión vacía"
        
        # Extraer información clave
        session_info = self._extract_session_info(messages)
        
        # Generar resumen usando LLM
        summary = self._generate_llm_summary(session_info, messages)
        
        return summary or self._generate_basic_summary(session_info)
    
    def compress_code_context(self, code_content: str, max_length: int = 1000) -> str:
        """
        Comprimir contexto de código manteniendo partes importantes
        
        Args:
            code_content: Contenido de código a comprimir
            max_length: Longitud máxima del resultado
        
        Returns:
            Código comprimido
        """
        if len(code_content) <= max_length:
            return code_content
        
        # Extraer partes importantes
        important_parts = []
        
        # Imports y definiciones de funciones/clases
        lines = code_content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Imports
            if stripped.startswith(('import ', 'from ')):
                important_parts.append((i, line, 'import'))
            
            # Definiciones de funciones
            elif stripped.startswith(('def ', 'class ', 'async def')):
                important_parts.append((i, line, 'definition'))
                
                # Incluir docstring si existe
                if i + 1 < len(lines) and '"""' in lines[i + 1]:
                    for j in range(i + 1, min(i + 4, len(lines))):
                        if '"""' in lines[j]:
                            important_parts.append((j, lines[j], 'docstring'))
                            if lines[j].count('"""') == 2:
                                break
            
            # Comentarios importantes
            elif stripped.startswith('#') and any(word in stripped.lower() for word in ['todo', 'fixme', 'important', 'note']):
                important_parts.append((i, line, 'comment'))
        
        # Construir versión comprimida
        if important_parts:
            compressed_lines = []
            prev_line = -1
            
            for line_num, line, part_type in important_parts:
                if line_num > prev_line + 1:
                    compressed_lines.append("# ... código omitido ...")
                compressed_lines.append(line)
                prev_line = line_num
            
            compressed = '\n'.join(compressed_lines)
            
            if len(compressed) <= max_length:
                return compressed
        
        # Si aún es muy largo, truncar inteligentemente
        return self._truncate_intelligently(code_content, max_length)
    
    def _create_intelligent_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Crear resumen inteligente de mensajes antiguos"""
        # Aplicar estrategias de compresión
        compressed_content = self._apply_compression_strategies(messages)
        
        # Usar LLM para crear resumen final
        llm_summary = self._generate_llm_compression(compressed_content)
        
        return llm_summary or compressed_content
    
    def _apply_compression_strategies(self, messages: List[Dict[str, Any]]) -> str:
        """Aplicar estrategias de compresión"""
        content_by_type = {
            'questions': [],
            'code_blocks': [],
            'file_operations': [],
            'decisions': [],
            'other': []
        }
        
        # Categorizar contenido
        for message in messages:
            content = message.get('content', '')
            role = message.get('role', 'user')
            
            if role == 'user':
                if any(word in content.lower() for word in ['?', 'cómo', 'qué', 'por qué']):
                    content_by_type['questions'].append(content)
                elif any(cmd in content for cmd in ['/ls', '/cat', '/grep', '/tree']):
                    content_by_type['file_operations'].append(content)
                else:
                    content_by_type['other'].append(content)
            else:  # assistant
                if '```' in content:
                    content_by_type['code_blocks'].append(content)
                elif any(word in content.lower() for word in ['recomiendo', 'sugiero', 'deberías']):
                    content_by_type['decisions'].append(content)
                else:
                    content_by_type['other'].append(content)
        
        # Comprimir cada categoría
        summary_parts = []
        
        if content_by_type['questions']:
            questions_summary = self._compress_questions(content_by_type['questions'])
            summary_parts.append(f"❓ Preguntas principales: {questions_summary}")
        
        if content_by_type['file_operations']:
            files_summary = self._compress_file_operations(content_by_type['file_operations'])
            summary_parts.append(f"📁 Archivos explorados: {files_summary}")
        
        if content_by_type['code_blocks']:
            code_summary = self._compress_code_responses(content_by_type['code_blocks'])
            summary_parts.append(f"💻 Código discutido: {code_summary}")
        
        if content_by_type['decisions']:
            decisions_summary = self._compress_decisions(content_by_type['decisions'])
            summary_parts.append(f"💡 Decisiones/Recomendaciones: {decisions_summary}")
        
        return '\n'.join(summary_parts)
    
    def _compress_questions(self, questions: List[str]) -> str:
        """Comprimir lista de preguntas"""
        if not questions:
            return ""
        
        # Extraer temas principales
        topics = set()
        for question in questions:
            # Extraer palabras clave
            words = re.findall(r'\b[a-záéíóúñ]{4,}\b', question.lower())
            topics.update(words[:3])  # Máximo 3 palabras por pregunta
        
        main_topics = list(topics)[:5]  # Máximo 5 temas
        
        return f"Se consultó sobre: {', '.join(main_topics)}"
    
    def _compress_file_operations(self, operations: List[str]) -> str:
        """Comprimir operaciones de archivos"""
        files_mentioned = set()
        commands_used = set()
        
        for op in operations:
            # Extraer comandos
            if op.startswith('/'):
                cmd = op.split()[0]
                commands_used.add(cmd)
            
            # Extraer nombres de archivos
            file_patterns = re.findall(r'[\w/]+\.\w+', op)
            files_mentioned.update(file_patterns[:2])  # Máximo 2 por operación
        
        result_parts = []
        if commands_used:
            result_parts.append(f"comandos usados: {', '.join(commands_used)}")
        if files_mentioned:
            files_list = list(files_mentioned)[:5]  # Máximo 5 archivos
            result_parts.append(f"archivos: {', '.join(files_list)}")
        
        return '; '.join(result_parts)
    
    def _compress_code_responses(self, code_responses: List[str]) -> str:
        """Comprimir respuestas con código"""
        languages = set()
        concepts = set()
        
        for response in code_responses:
            # Detectar lenguajes
            if '```python' in response:
                languages.add('Python')
            elif '```javascript' in response:
                languages.add('JavaScript')
            elif '```html' in response:
                languages.add('HTML')
            elif '```css' in response:
                languages.add('CSS')
            
            # Extraer conceptos técnicos
            tech_words = re.findall(r'\b(?:function|class|import|def|async|await|return)\b', response.lower())
            concepts.update(tech_words[:3])
        
        result_parts = []
        if languages:
            result_parts.append(f"Lenguajes: {', '.join(languages)}")
        if concepts:
            result_parts.append(f"Conceptos: {', '.join(concepts)}")
        
        return '; '.join(result_parts)
    
    def _compress_decisions(self, decisions: List[str]) -> str:
        """Comprimir decisiones y recomendaciones"""
        key_recommendations = []
        
        for decision in decisions:
            # Extraer frases clave
            sentences = re.split(r'[.!?]', decision)
            for sentence in sentences:
                if any(word in sentence.lower() for word in ['recomiendo', 'sugiero', 'deberías', 'mejor']):
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 10:
                        key_recommendations.append(clean_sentence[:80] + '...' if len(clean_sentence) > 80 else clean_sentence)
                        break
        
        return '; '.join(key_recommendations[:3])  # Máximo 3 recomendaciones
    
    def _generate_llm_compression(self, content: str) -> Optional[str]:
        """Generar compresión usando LLM"""
        try:
            prompt = f"""Resume este contenido de conversación de manera muy concisa:

{content}

Crea un resumen de máximo 3 líneas que capture:
1. Los temas principales discutidos
2. Decisiones o conclusiones importantes
3. Archivos o código relevante mencionado

Sé muy conciso pero informativo."""

            messages = [{'role': 'user', 'content': prompt}]
            
            # Usar modelo rápido para compresión
            summary = self.ollama_interface.chat(messages, self.settings.models['fast'])
            
            return summary
            
        except Exception as e:
            print(f"Error en compresión LLM: {e}")
            return None
    
    def _extract_session_info(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extraer información clave de la sesión"""
        info = {
            'total_messages': len(messages),
            'user_messages': 0,
            'assistant_messages': 0,
            'commands_used': set(),
            'files_mentioned': set(),
            'topics': set(),
            'duration': 0
        }
        
        timestamps = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            timestamp = message.get('timestamp')
            
            if timestamp:
                timestamps.append(timestamp)
            
            if role == 'user':
                info['user_messages'] += 1
                
                # Extraer comandos
                if content.startswith('/'):
                    cmd = content.split()[0]
                    info['commands_used'].add(cmd)
                
                # Extraer archivos mencionados
                files = re.findall(r'[\w/]+\.\w+', content)
                info['files_mentioned'].update(files)
                
                # Extraer temas (palabras clave)
                words = re.findall(r'\b[a-záéíóúñ]{4,}\b', content.lower())
                info['topics'].update(words[:3])
                
            else:
                info['assistant_messages'] += 1
        
        # Calcular duración
        if len(timestamps) >= 2:
            info['duration'] = timestamps[-1] - timestamps[0]
        
        return info
    
    def _generate_llm_summary(self, session_info: Dict[str, Any], messages: List[Dict[str, Any]]) -> Optional[str]:
        """Generar resumen de sesión usando LLM"""
        try:
            # Extraer contenido relevante
            sample_content = []
            for message in messages[-10:]:  # Últimos 10 mensajes
                content = message.get('content', '')[:200]  # Primeros 200 chars
                role = message.get('role', 'user')
                sample_content.append(f"{role}: {content}")
            
            prompt = f"""Crea un resumen de esta sesión de trabajo:

ESTADÍSTICAS:
- {session_info['total_messages']} mensajes totales
- Comandos usados: {', '.join(list(session_info['commands_used'])[:5])}
- Archivos mencionados: {', '.join(list(session_info['files_mentioned'])[:5])}
- Duración: {session_info['duration']/60:.1f} minutos

MUESTRA DE CONVERSACIÓN:
{chr(10).join(sample_content[-5:])}

Crea un resumen estructurado con:
1. **Objetivo principal** de la sesión
2. **Tareas realizadas**
3. **Archivos/proyectos trabajados**
4. **Resultados o conclusiones**

Máximo 4 líneas por sección."""

            messages_for_llm = [{'role': 'user', 'content': prompt}]
            summary = self.ollama_interface.chat(messages_for_llm, self.settings.models['primary'])
            
            return summary
            
        except Exception as e:
            print(f"Error generando resumen LLM: {e}")
            return None
    
    def _generate_basic_summary(self, session_info: Dict[str, Any]) -> str:
        """Generar resumen básico sin LLM"""
        summary = f"📊 **Resumen de sesión:**\n"
        summary += f"• {session_info['total_messages']} mensajes intercambiados\n"
        
        if session_info['commands_used']:
            commands = ', '.join(list(session_info['commands_used'])[:5])
            summary += f"• Comandos utilizados: {commands}\n"
        
        if session_info['files_mentioned']:
            files = ', '.join(list(session_info['files_mentioned'])[:3])
            summary += f"• Archivos trabajados: {files}\n"
        
        if session_info['duration'] > 0:
            summary += f"• Duración: {session_info['duration']/60:.1f} minutos\n"
        
        return summary
    
    def _truncate_intelligently(self, content: str, max_length: int) -> str:
        """Truncar contenido de manera inteligente"""
        if len(content) <= max_length:
            return content
        
        # Intentar cortar en líneas completas
        lines = content.split('\n')
        truncated_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 > max_length - 20:  # Dejar espacio para "..."
                break
            truncated_lines.append(line)
            current_length += len(line) + 1
        
        result = '\n'.join(truncated_lines)
        
        if len(result) < len(content):
            result += "\n... (contenido truncado)"
        
        return result
    
    # Estrategias de compresión específicas
    def _compress_repetitive_content(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Comprimir contenido repetitivo"""
        # TODO: Implementar detección de contenido repetitivo
        return messages
    
    def _compress_code_blocks(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Comprimir bloques de código largos"""
        # TODO: Implementar compresión de código
        return messages
    
    def _compress_file_listings(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Comprimir listados de archivos largos"""
        # TODO: Implementar compresión de listados
        return messages
    
    def _compress_similar_questions(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Comprimir preguntas similares"""
        # TODO: Implementar detección de preguntas similares
        return messages
    
    def _extract_key_decisions(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extraer decisiones clave"""
        # TODO: Implementar extracción de decisiones
        return messages