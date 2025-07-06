"""
NLP Parser para interpretar intenciones desde lenguaje natural
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Tipos de intenciones soportadas"""
    ANALYZE = "analyze"
    CREATE = "create"
    MODIFY = "modify"
    FIND = "find"
    EXPLAIN = "explain"
    OPTIMIZE = "optimize"
    TEST = "test"
    STATUS = "status"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Resultado del parsing de una intención"""
    intent: IntentType
    confidence: float  # 0.0 - 1.0
    target: Optional[str] = None  # Archivo, directorio, concepto objetivo
    action_details: Dict[str, Any] = None  # Detalles específicos de la acción
    original_text: str = ""
    

class NLPParser:
    """Parser de intenciones desde lenguaje natural"""
    
    def __init__(self):
        self.patterns = self._load_intent_patterns()
        self.confidence_threshold = 0.4  # Threshold más bajo para ser más permisivo
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[Dict]]:
        """Cargar patrones de intenciones con confianza"""
        return {
            IntentType.ANALYZE: [
                {
                    "patterns": [
                        r"analiz[ae].*?(?:proyecto|código|archivo|este|esto)",
                        r"revisa.*?(?:código|proyecto|archivo)",
                        r"qué.*?(?:problemas|issues|errores)",
                        r"dame.*?(?:análisis|reporte|resumen)",
                        r"examina.*?(?:este|esto|el|la)"
                    ],
                    "confidence": 0.9,
                    "keywords": ["analizar", "revisar", "problemas", "análisis", "examinar", "evaluar"]
                }
            ],
            IntentType.CREATE: [
                {
                    "patterns": [
                        r"crea.*?(?:archivo|proyecto|función|clase)",
                        r"genera.*?(?:código|archivo|proyecto)",
                        r"hacer.*?(?:nuevo|nueva|un|una)",
                        r"construye.*?(?:proyecto|aplicación|api)",
                        r"implementa.*?(?:función|clase|método)"
                    ],
                    "confidence": 0.85,
                    "keywords": ["crear", "generar", "nuevo", "nueva", "construir", "implementar", "hacer"]
                }
            ],
            IntentType.FIND: [
                {
                    "patterns": [
                        r"busca.*?(?:archivo|función|clase|patrón)",
                        r"encuentra.*?(?:donde|dónde|el|la)",
                        r"(?:donde|dónde).*?(?:está|se encuentra)",
                        r"localiza.*?(?:archivo|función|código)"
                    ],
                    "confidence": 0.8,
                    "keywords": ["buscar", "encontrar", "donde", "dónde", "localizar", "ubicar"]
                }
            ],
            IntentType.OPTIMIZE: [
                {
                    "patterns": [
                        r"optimiza.*?(?:código|performance|rendimiento)",
                        r"mejora.*?(?:velocidad|performance|eficiencia)",
                        r"acelera.*?(?:esto|función|código)",
                        r"reduce.*?(?:tiempo|latencia|memoria)"
                    ],
                    "confidence": 0.8,
                    "keywords": ["optimizar", "mejorar", "acelerar", "performance", "rendimiento", "eficiencia"]
                }
            ],
            IntentType.EXPLAIN: [
                {
                    "patterns": [
                        r"explica.*?(?:como|cómo|qué|este|esto)",
                        r"(?:como|cómo).*?(?:funciona|trabaja|opera)",
                        r"qué.*?(?:hace|significa|es)",
                        r"describe.*?(?:el|la|este|esto)"
                    ],
                    "confidence": 0.75,
                    "keywords": ["explicar", "como", "cómo", "qué", "describe", "significa"]
                }
            ],
            IntentType.STATUS: [
                {
                    "patterns": [
                        r"(?:estado|status|situación).*?(?:actual|del|de)",
                        r"como.*?(?:está|van|va).*?(?:proyecto|desarrollo)",
                        r"progreso.*?(?:actual|del|de)",
                        r"métricas.*?(?:sistema|proyecto)"
                    ],
                    "confidence": 0.9,
                    "keywords": ["estado", "status", "progreso", "métricas", "situación"]
                }
            ],
            IntentType.HELP: [
                {
                    "patterns": [
                        r"ayuda.*?(?:con|a|para)",
                        r"(?:como|cómo).*?(?:puedo|debo|hago)",
                        r"no.*?(?:sé|entiendo|comprendo)",
                        r"qué.*?(?:comandos|opciones|puedo)"
                    ],
                    "confidence": 0.8,
                    "keywords": ["ayuda", "como", "cómo", "puedo", "debo", "comandos", "opciones"]
                }
            ]
        }
    
    def parse(self, text: str) -> ParsedIntent:
        """Parsear texto natural y extraer intención"""
        if text is None:
            text = ""
            
        if not text or not text.strip():
            return ParsedIntent(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                original_text=text or ""
            )
        
        text_lower = text.lower().strip()
        
        # Buscar patrones de intención
        best_match = None
        best_confidence = 0.0
        best_intent = IntentType.UNKNOWN
        
        for intent_type, pattern_groups in self.patterns.items():
            for pattern_group in pattern_groups:
                confidence = self._calculate_confidence(text_lower, pattern_group)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent_type
                    best_match = pattern_group
        
        # Extraer target y detalles
        target = self._extract_target(text_lower, best_intent)
        action_details = self._extract_action_details(text_lower, best_intent, best_match)
        
        return ParsedIntent(
            intent=best_intent,
            confidence=best_confidence,
            target=target,
            action_details=action_details,
            original_text=text
        )
    
    def _calculate_confidence(self, text: str, pattern_group: Dict) -> float:
        """Calcular confianza basada en patrones y keywords"""
        confidence = 0.0
        base_confidence = pattern_group.get("confidence", 0.5)
        
        # Verificar patrones regex - dar más peso a los matches
        pattern_matches = 0
        for pattern in pattern_group["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_matches += 1
        
        if pattern_matches > 0:
            # Aumentar confianza por pattern match
            pattern_confidence = base_confidence * 0.8  # 80% del base por cualquier match
            confidence += pattern_confidence
        
        # Verificar keywords - más generoso
        keyword_matches = 0
        for keyword in pattern_group["keywords"]:
            if keyword.lower() in text:
                keyword_matches += 1
        
        if keyword_matches > 0:
            # Más peso a keywords
            keyword_confidence = 0.5 * (keyword_matches / len(pattern_group["keywords"]))
            confidence += keyword_confidence
        
        return min(confidence, 1.0)
    
    def _extract_target(self, text: str, intent: IntentType) -> Optional[str]:
        """Extraer objetivo/target de la intención"""
        # Patrones comunes para targets
        target_patterns = [
            r"(?:archivo|file|fichero)\s+([^\s]+)",
            r"(?:proyecto|project)\s+([^\s]+)",
            r"(?:función|function|método|method)\s+([^\s]+)",
            r"(?:clase|class)\s+([^\s]+)",
            r"(?:este|esto|el|la)\s+([^\s]+)",
            r"([^\s]+\.py)",
            r"([^\s]+\.js)",
            r"([^\s]+\.json)",
            r"([^\s]+/[^\s]*)"  # Paths
        ]
        
        for pattern in target_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_action_details(self, text: str, intent: IntentType, pattern_group: Dict) -> Dict[str, Any]:
        """Extraer detalles específicos de la acción"""
        details = {}
        
        # Detalles específicos por intent
        if intent == IntentType.ANALYZE:
            # Buscar qué tipo de análisis
            if "problemas" in text or "errores" in text or "issues" in text:
                details["focus"] = "issues"
            elif "performance" in text or "rendimiento" in text:
                details["focus"] = "performance"
            elif "métricas" in text or "estadísticas" in text:
                details["focus"] = "metrics"
            else:
                details["focus"] = "general"
        
        elif intent == IntentType.CREATE:
            # Buscar tipo de archivo/proyecto
            if "api" in text or "servidor" in text:
                details["type"] = "api"
            elif "web" in text or "frontend" in text:
                details["type"] = "web"
            elif "función" in text or "método" in text:
                details["type"] = "function"
            elif "clase" in text:
                details["type"] = "class"
        
        elif intent == IntentType.OPTIMIZE:
            # Buscar qué optimizar
            if "memoria" in text:
                details["target"] = "memory"
            elif "velocidad" in text or "tiempo" in text:
                details["target"] = "speed"
            elif "cpu" in text:
                details["target"] = "cpu"
        
        return details
    
    def is_confident(self, parsed_intent: ParsedIntent) -> bool:
        """Verificar si la confianza es suficiente"""
        return parsed_intent.confidence >= self.confidence_threshold
    
    def get_suggestions(self, text: str) -> List[str]:
        """Obtener sugerencias si la confianza es baja"""
        parsed = self.parse(text)
        
        if self.is_confident(parsed):
            return []
        
        suggestions = [
            "Intenta ser más específico sobre lo que quieres hacer",
            "Menciona el archivo o proyecto específico",
            "Usa palabras clave como 'analizar', 'crear', 'buscar', etc."
        ]
        
        # Sugerencias específicas basadas en el texto
        if "archivo" in text.lower():
            suggestions.append("Especifica el nombre del archivo o su ubicación")
        
        if any(word in text.lower() for word in ["problema", "error", "falla"]):
            suggestions.append("Prueba: 'Analiza este proyecto y encuentra problemas'")
        
        return suggestions[:3]  # Máximo 3 sugerencias