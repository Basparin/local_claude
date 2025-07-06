"""
Sistema de cache inteligente para análisis de código
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import OrderedDict


class AnalysisCache:
    """Cache inteligente para operaciones de análisis costosas"""
    
    def __init__(self, workspace_dir: str, max_cache_size: int = 100):
        self.workspace_dir = Path(workspace_dir)
        self.max_cache_size = max_cache_size
        
        # Caches en memoria (LRU)
        self.file_content_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.ast_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.analysis_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.project_structure_cache: Optional[Dict[str, Any]] = None
        self.project_structure_timestamp: float = 0
        
        # Cache persistence
        self.cache_dir = self.workspace_dir / '.local_claude_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
    def _get_file_hash(self, file_path: Path) -> str:
        """Obtener hash único del archivo basado en contenido + timestamp"""
        try:
            stat = file_path.stat()
            content_hash = hashlib.md5(
                f"{file_path.absolute()}:{stat.st_mtime}:{stat.st_size}".encode()
            ).hexdigest()
            return content_hash
        except (OSError, IOError):
            return ""
    
    def _maintain_cache_size(self, cache: OrderedDict):
        """Mantener el tamaño del cache bajo el límite (LRU)"""
        while len(cache) >= self.max_cache_size:
            cache.popitem(last=False)  # Remove oldest (LRU)
    
    def get_file_content(self, file_path: Path) -> Optional[str]:
        """Obtener contenido del archivo con cache"""
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return None
            
        # Check cache
        if file_hash in self.file_content_cache:
            # Move to end (most recently used)
            self.file_content_cache.move_to_end(file_hash)
            return self.file_content_cache[file_hash]['content']
        
        # Read and cache
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._maintain_cache_size(self.file_content_cache)
            self.file_content_cache[file_hash] = {
                'content': content,
                'timestamp': time.time(),
                'file_path': str(file_path)
            }
            
            return content
            
        except (UnicodeDecodeError, OSError, IOError):
            return None
    
    def get_ast_analysis(self, file_path: Path, file_content: str) -> Optional[Dict[str, Any]]:
        """Obtener análisis AST con cache"""
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return None
            
        # Check cache
        if file_hash in self.ast_cache:
            self.ast_cache.move_to_end(file_hash)
            return self.ast_cache[file_hash]['analysis']
        
        # Analyze and cache (solo para Python)
        if file_path.suffix != '.py':
            return None
            
        try:
            import ast
            tree = ast.parse(file_content)
            
            # Análisis básico del AST
            analysis = {
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity_score': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args),
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            analysis['imports'].append(f"{module}.{alias.name}")
                    else:
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
            
            # Simple complexity score
            analysis['complexity_score'] = len(analysis['functions']) + len(analysis['classes'])
            
            self._maintain_cache_size(self.ast_cache)
            self.ast_cache[file_hash] = {
                'analysis': analysis,
                'timestamp': time.time(),
                'file_path': str(file_path)
            }
            
            return analysis
            
        except (SyntaxError, ValueError):
            return None
    
    def get_llm_analysis(self, content_hash: str, analysis_type: str) -> Optional[str]:
        """Obtener análisis de LLM con cache"""
        cache_key = f"{content_hash}:{analysis_type}"
        
        # Check cache
        if cache_key in self.analysis_cache:
            self.analysis_cache.move_to_end(cache_key)
            return self.analysis_cache[cache_key]['result']
        
        return None
    
    def cache_llm_analysis(self, content_hash: str, analysis_type: str, result: str):
        """Cachear resultado de análisis LLM"""
        cache_key = f"{content_hash}:{analysis_type}"
        
        self._maintain_cache_size(self.analysis_cache)
        self.analysis_cache[cache_key] = {
            'result': result,
            'timestamp': time.time(),
            'analysis_type': analysis_type
        }
    
    def get_project_structure(self, max_age_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """Obtener estructura del proyecto con cache (5 min default)"""
        current_time = time.time()
        
        # Check if cache is still valid
        if (self.project_structure_cache and 
            current_time - self.project_structure_timestamp < max_age_seconds):
            return self.project_structure_cache
        
        # Rebuild cache
        try:
            structure = {
                'files': [],
                'directories': [],
                'code_files': [],
                'total_size': 0,
                'file_count': 0
            }
            
            for item in self.workspace_dir.rglob('*'):
                if item.name.startswith('.'):
                    continue
                    
                try:
                    stat = item.stat()
                    
                    if item.is_file():
                        file_info = {
                            'path': str(item.relative_to(self.workspace_dir)),
                            'size': stat.st_size,
                            'modified': stat.st_mtime,
                            'extension': item.suffix
                        }
                        structure['files'].append(file_info)
                        structure['total_size'] += stat.st_size
                        structure['file_count'] += 1
                        
                        # Detect code files
                        if item.suffix in {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h'}:
                            structure['code_files'].append(file_info)
                            
                    elif item.is_dir():
                        structure['directories'].append({
                            'path': str(item.relative_to(self.workspace_dir)),
                            'modified': stat.st_mtime
                        })
                        
                except (OSError, IOError):
                    continue
            
            self.project_structure_cache = structure
            self.project_structure_timestamp = current_time
            
            return structure
            
        except Exception:
            return None
    
    def invalidate_file_cache(self, file_path: Path):
        """Invalidar cache específico de un archivo"""
        file_hash = self._get_file_hash(file_path)
        
        # Remove from all caches
        self.file_content_cache.pop(file_hash, None)
        self.ast_cache.pop(file_hash, None)
        
        # Invalidate project structure if file was modified
        self.project_structure_cache = None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        return {
            'file_content_cache_size': len(self.file_content_cache),
            'ast_cache_size': len(self.ast_cache),
            'analysis_cache_size': len(self.analysis_cache),
            'project_structure_cached': self.project_structure_cache is not None,
            'max_cache_size': self.max_cache_size
        }
    
    def clear_cache(self):
        """Limpiar todos los caches"""
        self.file_content_cache.clear()
        self.ast_cache.clear()
        self.analysis_cache.clear()
        self.project_structure_cache = None
        self.project_structure_timestamp = 0