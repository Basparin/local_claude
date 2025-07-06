"""
Explorador inteligente del workspace
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import mimetypes

class WorkspaceExplorer:
    """Explorador inteligente del workspace"""
    
    def __init__(self, settings):
        self.settings = settings
        self.workspace_dir = settings.workspace_dir
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        self.ignored_files = {'.gitignore', '.env', '.pyc'}
    
    def list_files(self, path: str = '.') -> str:
        """Listar archivos con información contextual"""
        try:
            target_path = Path(self.workspace_dir) / path
            
            if not target_path.exists():
                return f"❌ El directorio '{path}' no existe"
            
            if not target_path.is_dir():
                return f"❌ '{path}' no es un directorio"
            
            # Obtener archivos
            items = []
            for item in target_path.iterdir():
                if item.name.startswith('.') and item.name not in {'.gitignore', '.env'}:
                    continue
                
                if item.is_dir() and item.name in self.ignored_dirs:
                    continue
                
                items.append(item)
            
            # Ordenar: directorios primero, luego archivos
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            # Formatear salida
            result = f"📁 Contenido de '{path}':\n"
            
            for item in items:
                if item.is_dir():
                    # Contar archivos en directorio
                    try:
                        file_count = len([f for f in item.iterdir() if f.is_file()])
                        result += f"  📂 {item.name}/ ({file_count} archivos)\n"
                    except PermissionError:
                        result += f"  📂 {item.name}/ (sin acceso)\n"
                else:
                    # Información del archivo
                    size = self._format_size(item.stat().st_size)
                    file_type = self._get_file_type(item)
                    result += f"  📄 {item.name} ({size}) {file_type}\n"
            
            if not items:
                result += "  (directorio vacío)\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error listando '{path}': {e}"
    
    def show_file(self, file_path: str) -> str:
        """Mostrar contenido de un archivo con análisis"""
        try:
            target_path = Path(self.workspace_dir) / file_path
            
            if not target_path.exists():
                return f"❌ El archivo '{file_path}' no existe"
            
            if not target_path.is_file():
                return f"❌ '{file_path}' no es un archivo"
            
            # Verificar tamaño del archivo
            size = target_path.stat().st_size
            if size > 1024 * 1024:  # 1MB
                return f"❌ Archivo demasiado grande ({self._format_size(size)}). Usa /grep para buscar contenido específico."
            
            # Leer archivo
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                return f"❌ '{file_path}' parece ser un archivo binario"
            
            # Análisis básico
            lines = content.split('\n')
            file_type = self._get_file_type(target_path)
            
            result = f"📄 Archivo: {file_path}\n"
            result += f"📊 Tamaño: {self._format_size(size)} | Líneas: {len(lines)} | Tipo: {file_type}\n"
            result += "─" * 50 + "\n"
            
            # Mostrar contenido (limitado)
            if len(lines) > 50:
                result += "\n".join(lines[:25])
                result += f"\n... ({len(lines) - 50} líneas omitidas) ...\n"
                result += "\n".join(lines[-25:])
            else:
                result += content
            
            return result
            
        except Exception as e:
            return f"❌ Error leyendo '{file_path}': {e}"
    
    def search_pattern(self, pattern: str, path: str = '.') -> str:
        """Buscar patrón en archivos"""
        try:
            target_path = Path(self.workspace_dir) / path
            
            if not target_path.exists():
                return f"❌ El directorio '{path}' no existe"
            
            matches = []
            
            # Buscar recursivamente
            for file_path in target_path.rglob('*'):
                if file_path.is_file() and self._should_search_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                if pattern.lower() in line.lower():
                                    rel_path = file_path.relative_to(self.workspace_dir)
                                    matches.append({
                                        'file': str(rel_path),
                                        'line': line_num,
                                        'content': line.strip()
                                    })
                    except (UnicodeDecodeError, PermissionError):
                        continue
            
            # Formatear resultados
            if not matches:
                return f"🔍 No se encontraron coincidencias para '{pattern}' en '{path}'"
            
            result = f"🔍 Encontradas {len(matches)} coincidencias para '{pattern}':\n"
            
            # Limitar resultados
            for match in matches[:20]:  # Máximo 20 resultados
                result += f"  📄 {match['file']}:{match['line']}: {match['content']}\n"
            
            if len(matches) > 20:
                result += f"  ... y {len(matches) - 20} coincidencias más\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error buscando '{pattern}': {e}"
    
    def show_tree(self, path: str = '.', max_depth: int = 3) -> str:
        """Mostrar estructura de directorios"""
        try:
            target_path = Path(self.workspace_dir) / path
            
            if not target_path.exists():
                return f"❌ El directorio '{path}' no existe"
            
            if not target_path.is_dir():
                return f"❌ '{path}' no es un directorio"
            
            result = f"🌳 Estructura de '{path}':\n"
            result += self._build_tree(target_path, "", max_depth)
            
            return result
            
        except Exception as e:
            return f"❌ Error mostrando árbol de '{path}': {e}"
    
    def find_files(self, pattern: str) -> str:
        """Buscar archivos por nombre"""
        try:
            matches = []
            
            for file_path in Path(self.workspace_dir).rglob('*'):
                if file_path.is_file() and pattern.lower() in file_path.name.lower():
                    if not self._should_ignore_file(file_path):
                        rel_path = file_path.relative_to(Path(self.workspace_dir))
                        matches.append(str(rel_path))
            
            if not matches:
                return f"🔍 No se encontraron archivos que coincidan con '{pattern}'"
            
            result = f"🔍 Encontrados {len(matches)} archivos que coinciden con '{pattern}':\n"
            
            for match in sorted(matches)[:20]:  # Máximo 20 resultados
                result += f"  📄 {match}\n"
            
            if len(matches) > 20:
                result += f"  ... y {len(matches) - 20} archivos más\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error buscando archivos: {e}"
    
    def _build_tree(self, path: Path, prefix: str, max_depth: int) -> str:
        """Construir representación en árbol"""
        if max_depth <= 0:
            return ""
        
        try:
            items = []
            for item in path.iterdir():
                if self._should_ignore_file(item):
                    continue
                items.append(item)
            
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            result = ""
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                
                if item.is_dir():
                    result += f"{prefix}{current_prefix}📂 {item.name}/\n"
                    
                    # Recursión para subdirectorios
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    result += self._build_tree(item, next_prefix, max_depth - 1)
                else:
                    file_type = self._get_file_type(item)
                    result += f"{prefix}{current_prefix}📄 {item.name} {file_type}\n"
            
            return result
            
        except PermissionError:
            return f"{prefix}└── (sin acceso)\n"
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Verificar si un archivo debe ser ignorado"""
        if file_path.name.startswith('.') and file_path.name not in {'.gitignore', '.env'}:
            return True
        
        if file_path.is_dir() and file_path.name in self.ignored_dirs:
            return True
        
        if file_path.suffix in {'.pyc', '.pyo', '.pyd'}:
            return True
        
        return False
    
    def _should_search_file(self, file_path: Path) -> bool:
        """Verificar si un archivo debe ser buscado"""
        if self._should_ignore_file(file_path):
            return False
        
        # Solo buscar archivos de texto
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and not mime_type.startswith('text/'):
            return False
        
        # Verificar tamaño
        if file_path.stat().st_size > 1024 * 1024:  # 1MB
            return False
        
        return True
    
    def _get_file_type(self, file_path: Path) -> str:
        """Obtener tipo de archivo"""
        suffix = file_path.suffix.lower()
        
        type_map = {
            '.py': '🐍 Python',
            '.js': '🟨 JavaScript',
            '.ts': '🔷 TypeScript',
            '.html': '🌐 HTML',
            '.css': '🎨 CSS',
            '.json': '📋 JSON',
            '.md': '📝 Markdown',
            '.txt': '📄 Texto',
            '.yml': '⚙️ YAML',
            '.yaml': '⚙️ YAML',
            '.xml': '📋 XML',
            '.sql': '🗃️ SQL',
            '.sh': '🔧 Shell',
            '.bat': '🔧 Batch',
            '.dockerfile': '🐳 Docker',
            '.gitignore': '🚫 Git',
            '.env': '🔑 Env'
        }
        
        return type_map.get(suffix, '📄')
    
    def _format_size(self, size: int) -> str:
        """Formatear tamaño de archivo"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size/(1024*1024):.1f}MB"