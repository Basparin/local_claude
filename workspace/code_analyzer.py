"""
Analizador inteligente de código
"""

import ast
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter

from .analysis_cache import AnalysisCache

class CodeAnalyzer:
    """Analizador inteligente de código y proyectos"""
    
    def __init__(self, settings, ollama_interface):
        self.settings = settings
        self.ollama_interface = ollama_interface
        self.workspace_dir = settings.workspace_dir
        
        # Initialize intelligent caching system
        self.cache = AnalysisCache(self.workspace_dir)
    
    def analyze_project(self, path: str = '.') -> str:
        """
        Analizar un proyecto completo
        
        Args:
            path: Ruta del proyecto a analizar
        
        Returns:
            Análisis completo del proyecto
        """
        try:
            target_path = Path(self.workspace_dir) / path
            
            if not target_path.exists():
                return f"❌ El directorio '{path}' no existe"
            
            # Recopilar información del proyecto
            project_info = self._gather_project_info(target_path)
            
            # Generar análisis con LLM
            analysis = self._generate_project_analysis(project_info)
            
            return analysis
            
        except Exception as e:
            return f"❌ Error analizando proyecto: {e}"
    
    def analyze_file(self, file_path: str) -> str:
        """
        Analizar un archivo específico (con cache inteligente)
        
        Args:
            file_path: Ruta del archivo a analizar
        
        Returns:
            Análisis detallado del archivo
        """
        try:
            target_path = Path(self.workspace_dir) / file_path
            
            if not target_path.exists():
                return f"❌ El archivo '{file_path}' no existe"
            
            if not target_path.is_file():
                return f"❌ '{file_path}' no es un archivo"
            
            # 🚀 OPTIMIZACIÓN: Usar cache para leer contenido
            content = self.cache.get_file_content(target_path)
            if content is None:
                return f"❌ '{file_path}' parece ser un archivo binario o inaccesible"
            
            # 🚀 OPTIMIZACIÓN: Verificar cache de análisis LLM
            content_hash = hashlib.md5(content.encode()).hexdigest()
            cached_analysis = self.cache.get_llm_analysis(content_hash, 'file_analysis')
            
            if cached_analysis:
                return f"📋 Análisis de {file_path} (cached):\n\n{cached_analysis}"
            
            # Análisis no cacheado - proceder normalmente
            file_type = self._detect_file_type(target_path)
            analysis = self._analyze_by_type(content, file_path, file_type)
            
            # 🚀 OPTIMIZACIÓN: Cachear resultado del análisis
            self.cache.cache_llm_analysis(content_hash, 'file_analysis', analysis)
            
            return analysis
            
        except Exception as e:
            return f"❌ Error analizando archivo: {e}"
    
    def find_issues(self, path: str = '.') -> str:
        """
        Encontrar problemas potenciales en el código (optimizado con cache)
        
        Args:
            path: Ruta a analizar
        
        Returns:
            Lista de problemas encontrados
        """
        try:
            target_path = Path(self.workspace_dir) / path
            issues = []
            
            # 🚀 OPTIMIZACIÓN: Usar cache de estructura de proyecto
            project_structure = self.cache.get_project_structure()
            
            if project_structure:
                # Usar estructura cacheada
                code_files = [
                    self.workspace_dir / file_info['path'] 
                    for file_info in project_structure['code_files']
                    if str(self.workspace_dir / file_info['path']).startswith(str(target_path))
                ]
            else:
                # Fallback al método original
                code_files = [
                    file_path for file_path in target_path.rglob('*')
                    if file_path.is_file() and self._is_code_file(file_path)
                ]
            
            # Analizar archivos de código encontrados
            for file_path in code_files:
                file_issues = self._find_file_issues(file_path)
                if file_issues:
                    issues.extend(file_issues)
            
            if not issues:
                return "✅ No se encontraron problemas obvios en el código"
            
            # Formatear resultados
            result = f"⚠️ Encontrados {len(issues)} problemas potenciales:\n\n"
            
            # Agrupar por tipo
            issues_by_type = defaultdict(list)
            for issue in issues:
                issues_by_type[issue['type']].append(issue)
            
            for issue_type, type_issues in issues_by_type.items():
                result += f"🔍 **{issue_type.upper()}**:\n"
                for issue in type_issues[:5]:  # Limitar a 5 por tipo
                    result += f"  • {issue['file']}:{issue['line']} - {issue['message']}\n"
                
                if len(type_issues) > 5:
                    result += f"  ... y {len(type_issues) - 5} más\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error buscando problemas: {e}"
    
    def suggest_improvements(self, file_path: str) -> str:
        """
        Sugerir mejoras para un archivo
        
        Args:
            file_path: Archivo a analizar
        
        Returns:
            Sugerencias de mejora
        """
        try:
            target_path = Path(self.workspace_dir) / file_path
            
            if not target_path.exists():
                return f"❌ El archivo '{file_path}' no existe"
            
            # Leer y analizar archivo
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generar sugerencias con LLM
            suggestions = self._generate_suggestions(content, file_path)
            
            return suggestions
            
        except Exception as e:
            return f"❌ Error generando sugerencias: {e}"
    
    def calculate_complexity(self, file_path: str) -> str:
        """
        Calcular complejidad de un archivo Python
        
        Args:
            file_path: Archivo Python a analizar
        
        Returns:
            Métricas de complejidad
        """
        try:
            target_path = Path(self.workspace_dir) / file_path
            
            if not target_path.exists():
                return f"❌ El archivo '{file_path}' no existe"
            
            if not str(target_path).endswith('.py'):
                return f"❌ Solo se puede analizar complejidad de archivos Python"
            
            # 🚀 OPTIMIZACIÓN: Usar cache para contenido y AST
            content = self.cache.get_file_content(target_path)
            if content is None:
                return f"❌ No se pudo leer el archivo '{file_path}'"
            
            # Intentar obtener análisis AST del cache
            ast_analysis = self.cache.get_ast_analysis(target_path, content)
            
            if ast_analysis:
                # Usar datos del cache
                functions_count = len(ast_analysis['functions'])
                classes_count = len(ast_analysis['classes'])
                imports_count = len(ast_analysis['imports'])
                complexity_score = ast_analysis['complexity_score']
                
                # Crear métricas desde el cache
                metrics = {
                    'functions': functions_count,
                    'classes': classes_count, 
                    'imports': imports_count,
                    'complexity': complexity_score,
                    'lines': len(content.splitlines()),
                    'cached': True
                }
            else:
                # Parsear AST (fallback)
                try:
                    tree = ast.parse(content)
                except SyntaxError as e:
                    return f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}"
                
                # Calcular métricas
                metrics = self._calculate_ast_metrics(tree)
                metrics['cached'] = False
            
            # Formatear resultados
            result = f"📊 Análisis de complejidad para '{file_path}':\n\n"
            result += f"📏 Líneas de código: {len(content.split())}\n"
            result += f"🔢 Funciones: {metrics['functions']}\n"
            result += f"📚 Clases: {metrics['classes']}\n"
            result += f"📥 Imports: {metrics['imports']}\n"
            result += f"🔄 Complejidad ciclomática promedio: {metrics['avg_complexity']:.1f}\n"
            
            if metrics['max_complexity'] > 10:
                result += f"⚠️ Función más compleja: {metrics['max_complexity']} (considerar refactoring)\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error calculando complejidad: {e}"
    
    def _gather_project_info(self, project_path: Path) -> Dict[str, Any]:
        """Recopilar información general del proyecto"""
        info = {
            'name': project_path.name,
            'path': str(project_path),
            'files': [],
            'languages': Counter(),
            'structure': {},
            'config_files': [],
            'documentation': [],
            'tests': [],
            'size_info': {'total_files': 0, 'total_size': 0}
        }
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                # Información básica del archivo
                rel_path = file_path.relative_to(project_path)
                file_info = {
                    'path': str(rel_path),
                    'size': file_path.stat().st_size,
                    'type': self._detect_file_type(file_path)
                }
                
                info['files'].append(file_info)
                info['languages'][file_info['type']] += 1
                info['size_info']['total_files'] += 1
                info['size_info']['total_size'] += file_info['size']
                
                # Categorizar archivos especiales
                if file_info['type'] in ['json', 'yaml', 'toml'] or 'config' in str(rel_path).lower():
                    info['config_files'].append(str(rel_path))
                elif file_info['type'] == 'markdown' or 'readme' in str(rel_path).lower():
                    info['documentation'].append(str(rel_path))
                elif 'test' in str(rel_path).lower():
                    info['tests'].append(str(rel_path))
        
        return info
    
    def _generate_project_analysis(self, project_info: Dict[str, Any]) -> str:
        """Generar análisis del proyecto usando LLM"""
        try:
            # Preparar prompt para LLM
            prompt = f"""Analiza este proyecto de software y proporciona un resumen completo:

INFORMACIÓN DEL PROYECTO:
- Nombre: {project_info['name']}
- Total de archivos: {project_info['size_info']['total_files']}
- Tamaño total: {self._format_size(project_info['size_info']['total_size'])}

LENGUAJES/TECNOLOGÍAS:
{self._format_languages(project_info['languages'])}

ARCHIVOS DE CONFIGURACIÓN:
{', '.join(project_info['config_files'][:5]) if project_info['config_files'] else 'Ninguno'}

DOCUMENTACIÓN:
{', '.join(project_info['documentation'][:3]) if project_info['documentation'] else 'Ninguna'}

TESTS:
{', '.join(project_info['tests'][:3]) if project_info['tests'] else 'Ninguno'}

ESTRUCTURA PRINCIPAL:
{self._format_main_structure(project_info['files'])}

Por favor proporciona:
1. Tipo de proyecto (web app, CLI, biblioteca, etc.)
2. Tecnologías principales identificadas
3. Calidad del proyecto (estructura, documentación, tests)
4. Posibles mejoras o problemas
5. Sugerencias de desarrollo

Responde de forma concisa y práctica."""

            messages = [{'role': 'user', 'content': prompt}]
            analysis = self.ollama_interface.chat(messages, self.settings.models['primary'])
            
            if analysis:
                return f"🔍 **Análisis del proyecto '{project_info['name']}':**\n\n{analysis}"
            else:
                return self._generate_basic_analysis(project_info)
                
        except Exception as e:
            return self._generate_basic_analysis(project_info)
    
    def _generate_basic_analysis(self, project_info: Dict[str, Any]) -> str:
        """Generar análisis básico sin LLM"""
        result = f"📊 **Análisis básico del proyecto '{project_info['name']}':**\n\n"
        
        # Estadísticas básicas
        result += f"📁 **Estadísticas:**\n"
        result += f"  • {project_info['size_info']['total_files']} archivos\n"
        result += f"  • {self._format_size(project_info['size_info']['total_size'])} de tamaño total\n\n"
        
        # Lenguajes
        result += f"💻 **Tecnologías:**\n"
        for lang, count in project_info['languages'].most_common(5):
            result += f"  • {lang}: {count} archivos\n"
        result += "\n"
        
        # Evaluación básica
        result += f"✅ **Evaluación:**\n"
        
        if project_info['documentation']:
            result += f"  • ✅ Tiene documentación ({len(project_info['documentation'])} archivos)\n"
        else:
            result += f"  • ⚠️ Falta documentación\n"
        
        if project_info['tests']:
            result += f"  • ✅ Tiene tests ({len(project_info['tests'])} archivos)\n"
        else:
            result += f"  • ⚠️ No se encontraron tests\n"
        
        if project_info['config_files']:
            result += f"  • ✅ Archivos de configuración presentes\n"
        
        return result
    
    def _analyze_by_type(self, content: str, file_path: str, file_type: str) -> str:
        """Analizar archivo según su tipo"""
        if file_type == 'python':
            return self._analyze_python_file(content, file_path)
        elif file_type == 'javascript':
            return self._analyze_javascript_file(content, file_path)
        elif file_type == 'json':
            return self._analyze_json_file(content, file_path)
        else:
            return self._analyze_generic_file(content, file_path, file_type)
    
    def _analyze_python_file(self, content: str, file_path: str) -> str:
        """Análisis específico para archivos Python"""
        try:
            tree = ast.parse(content)
            metrics = self._calculate_ast_metrics(tree)
            
            result = f"🐍 **Análisis de '{file_path}':**\n\n"
            result += f"📊 **Métricas:**\n"
            result += f"  • Líneas: {len(content.split())}\n"
            result += f"  • Funciones: {metrics['functions']}\n"
            result += f"  • Clases: {metrics['classes']}\n"
            result += f"  • Imports: {metrics['imports']}\n"
            result += f"  • Complejidad promedio: {metrics['avg_complexity']:.1f}\n\n"
            
            # Funciones principales
            if metrics['function_names']:
                result += f"🔧 **Funciones principales:**\n"
                for func in metrics['function_names'][:5]:
                    result += f"  • {func}\n"
                result += "\n"
            
            # Imports
            if metrics['import_names']:
                result += f"📦 **Dependencias:**\n"
                for imp in metrics['import_names'][:5]:
                    result += f"  • {imp}\n"
                result += "\n"
            
            return result
            
        except SyntaxError as e:
            return f"❌ Error de sintaxis en '{file_path}' línea {e.lineno}: {e.msg}"
        except Exception as e:
            return f"❌ Error analizando '{file_path}': {e}"
    
    def _analyze_javascript_file(self, content: str, file_path: str) -> str:
        """Análisis básico para archivos JavaScript"""
        lines = content.split('\n')
        
        # Análisis básico con regex
        functions = len(re.findall(r'function\s+\w+', content))
        classes = len(re.findall(r'class\s+\w+', content))
        imports = len(re.findall(r'import\s+.*from', content))
        
        result = f"🟨 **Análisis de '{file_path}':**\n\n"
        result += f"📊 **Métricas:**\n"
        result += f"  • Líneas: {len(lines)}\n"
        result += f"  • Funciones: {functions}\n"
        result += f"  • Clases: {classes}\n"
        result += f"  • Imports: {imports}\n"
        
        return result
    
    def _analyze_json_file(self, content: str, file_path: str) -> str:
        """Análisis para archivos JSON"""
        try:
            data = json.loads(content)
            
            result = f"📋 **Análisis de '{file_path}':**\n\n"
            result += f"📊 **Estructura:**\n"
            result += f"  • Tipo: {type(data).__name__}\n"
            
            if isinstance(data, dict):
                result += f"  • Claves principales: {len(data)}\n"
                result += f"  • Claves: {', '.join(list(data.keys())[:5])}\n"
            elif isinstance(data, list):
                result += f"  • Elementos: {len(data)}\n"
            
            return result
            
        except json.JSONDecodeError as e:
            return f"❌ JSON inválido en '{file_path}': {e.msg}"
    
    def _analyze_generic_file(self, content: str, file_path: str, file_type: str) -> str:
        """Análisis genérico para otros tipos de archivo"""
        lines = content.split('\n')
        
        result = f"📄 **Análisis de '{file_path}' ({file_type}):**\n\n"
        result += f"📊 **Estadísticas básicas:**\n"
        result += f"  • Líneas: {len(lines)}\n"
        result += f"  • Caracteres: {len(content)}\n"
        result += f"  • Tamaño: {self._format_size(len(content.encode('utf-8')))}\n"
        
        # Líneas no vacías
        non_empty_lines = [line for line in lines if line.strip()]
        result += f"  • Líneas con contenido: {len(non_empty_lines)}\n"
        
        return result
    
    def _calculate_ast_metrics(self, tree: ast.AST) -> Dict[str, Any]:
        """Calcular métricas del AST de Python"""
        functions = []
        classes = []
        imports = []
        complexities = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                complexity = self._calculate_cyclomatic_complexity(node)
                complexities.append(complexity)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    imports.append(node.module or 'relative')
        
        return {
            'functions': len(functions),
            'classes': len(classes),
            'imports': len(imports),
            'function_names': functions,
            'class_names': classes,
            'import_names': imports,
            'avg_complexity': sum(complexities) / len(complexities) if complexities else 0,
            'max_complexity': max(complexities) if complexities else 0
        }
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calcular complejidad ciclomática básica"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _find_file_issues(self, file_path: Path) -> List[Dict[str, Any]]:
        """Encontrar problemas en un archivo específico"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            rel_path = file_path.relative_to(self.workspace_dir)
            
            for i, line in enumerate(lines, 1):
                # Problemas comunes
                if len(line.rstrip()) > 120:
                    issues.append({
                        'type': 'style',
                        'file': str(rel_path),
                        'line': i,
                        'message': 'Línea muy larga (>120 caracteres)'
                    })
                
                if line.rstrip().endswith('  '):
                    issues.append({
                        'type': 'style',
                        'file': str(rel_path),
                        'line': i,
                        'message': 'Espacios al final de línea'
                    })
                
                if 'TODO' in line or 'FIXME' in line:
                    issues.append({
                        'type': 'todo',
                        'file': str(rel_path),
                        'line': i,
                        'message': 'Comentario TODO/FIXME pendiente'
                    })
                
                if 'print(' in line and file_path.suffix == '.py':
                    issues.append({
                        'type': 'debug',
                        'file': str(rel_path),
                        'line': i,
                        'message': 'Posible debug print()'
                    })
            
        except Exception:
            pass
        
        return issues
    
    def _generate_suggestions(self, content: str, file_path: str) -> str:
        """Generar sugerencias usando LLM"""
        try:
            prompt = f"""Analiza este código y proporciona sugerencias de mejora específicas:

ARCHIVO: {file_path}

CÓDIGO:
```
{content[:2000]}...
```

Proporciona sugerencias sobre:
1. Calidad del código
2. Performance
3. Legibilidad
4. Buenas prácticas
5. Posibles bugs

Responde de forma concisa y práctica."""

            messages = [{'role': 'user', 'content': prompt}]
            suggestions = self.ollama_interface.chat(messages, self.settings.models['primary'])
            
            if suggestions:
                return f"💡 **Sugerencias para '{file_path}':**\n\n{suggestions}"
            else:
                return f"💡 No se pudieron generar sugerencias para '{file_path}'"
                
        except Exception as e:
            return f"❌ Error generando sugerencias: {e}"
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detectar tipo de archivo"""
        suffix = file_path.suffix.lower()
        
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.toml': 'toml',
            '.txt': 'text'
        }
        
        return type_map.get(suffix, 'unknown')
    
    def _is_code_file(self, file_path: Path) -> bool:
        """Verificar si es un archivo de código"""
        code_extensions = {'.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.yml', '.yaml'}
        return file_path.suffix.lower() in code_extensions
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Verificar si un archivo debe ser ignorado"""
        ignore_patterns = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        
        for part in file_path.parts:
            if part in ignore_patterns or part.startswith('.'):
                return True
        
        return False
    
    def _format_size(self, size: int) -> str:
        """Formatear tamaño"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size/(1024*1024):.1f}MB"
    
    def _format_languages(self, languages: Counter) -> str:
        """Formatear lista de lenguajes"""
        if not languages:
            return "No identificados"
        
        result = []
        for lang, count in languages.most_common(5):
            result.append(f"{lang} ({count})")
        
        return ", ".join(result)
    
    def _format_main_structure(self, files: List[Dict[str, Any]]) -> str:
        """Formatear estructura principal"""
        # Obtener directorios principales
        directories = set()
        for file_info in files:
            path_parts = Path(file_info['path']).parts
            if len(path_parts) > 1:
                directories.add(path_parts[0])
        
        return ", ".join(sorted(list(directories)[:8]))
    
    def get_cache_stats(self) -> str:
        """
        Obtener estadísticas del sistema de cache
        
        Returns:
            Estadísticas formateadas del cache
        """
        stats = self.cache.get_cache_stats()
        
        result = "📊 Estadísticas del Cache de Análisis:\n\n"
        result += f"📁 Contenido de archivos cacheado: {stats['file_content_cache_size']}\n"
        result += f"🌳 Análisis AST cacheado: {stats['ast_cache_size']}\n"
        result += f"🤖 Análisis LLM cacheado: {stats['analysis_cache_size']}\n"
        result += f"📋 Estructura de proyecto: {'✅ Cacheada' if stats['project_structure_cached'] else '❌ No cacheada'}\n"
        result += f"📏 Límite máximo: {stats['max_cache_size']} entradas por cache\n\n"
        
        total_cached = stats['file_content_cache_size'] + stats['ast_cache_size'] + stats['analysis_cache_size']
        if total_cached > 0:
            result += f"🚀 Total: {total_cached} elementos cacheados - acelera análisis repetitivos"
        else:
            result += "📝 Cache vacío - se poblará con el uso"
            
        return result
    
    def clear_analysis_cache(self) -> str:
        """
        Limpiar el cache de análisis
        
        Returns:
            Mensaje de confirmación
        """
        self.cache.clear_cache()
        return "🧹 Cache de análisis limpiado - próximos análisis serán recalculados"