"""
Formateo avanzado y utilidades de presentación
"""

import re
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class AdvancedFormatter:
    """Formateador avanzado para mejorar la presentación"""
    
    def __init__(self, settings):
        self.settings = settings
        self.colors_enabled = settings.cli['colors']
        
        # Códigos de color ANSI extendidos
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'italic': '\033[3m',
            'underline': '\033[4m',
            'blink': '\033[5m',
            'reverse': '\033[7m',
            'strikethrough': '\033[9m',
            
            # Colores básicos
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'gray': '\033[90m',
            
            # Colores brillantes
            'bright_red': '\033[91m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_blue': '\033[94m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
            'bright_white': '\033[97m',
            
            # Fondos
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_magenta': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_white': '\033[47m',
        }
        
        # Emojis para diferentes contextos
        self.emojis = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'thinking': '🤔',
            'robot': '🤖',
            'user': '💬',
            'file': '📄',
            'folder': '📁',
            'code': '💻',
            'search': '🔍',
            'build': '🔨',
            'stats': '📊',
            'memory': '🧠',
            'time': '⏰',
            'rocket': '🚀',
            'fire': '🔥',
            'star': '⭐',
            'point_right': '👉',
            'check': '✓',
            'cross': '✗',
            'arrow_right': '→',
            'arrow_down': '↓',
            'gear': '⚙️',
            'magic': '✨',
            'trophy': '🏆'
        }
    
    def colorize(self, text: str, color: str, style: str = None) -> str:
        """Aplicar color y estilo al texto"""
        if not self.colors_enabled:
            return text
        
        color_code = self.colors.get(color, '')
        style_code = self.colors.get(style, '') if style else ''
        reset_code = self.colors['reset']
        
        return f"{style_code}{color_code}{text}{reset_code}"
    
    def format_title(self, title: str, level: int = 1) -> str:
        """Formatear título con decoración"""
        decorations = {
            1: ('═', 'bright_cyan', 'bold'),
            2: ('─', 'cyan', 'bold'),
            3: ('·', 'blue', None)
        }
        
        char, color, style = decorations.get(level, decorations[3])
        
        if level == 1:
            line = char * len(title)
            return f"\n{self.colorize(line, color)}\n{self.colorize(title, color, style)}\n{self.colorize(line, color)}\n"
        elif level == 2:
            line = char * len(title)
            return f"\n{self.colorize(title, color, style)}\n{self.colorize(line, color)}\n"
        else:
            return f"\n{self.colorize(f'{char} {title}', color, style)}\n"
    
    def format_list(self, items: List[str], style: str = 'bullet') -> str:
        """Formatear lista con diferentes estilos"""
        if not items:
            return ""
        
        formatted_items = []
        
        for i, item in enumerate(items):
            if style == 'bullet':
                prefix = f"{self.colorize('•', 'cyan')} "
            elif style == 'numbered':
                prefix = f"{self.colorize(f'{i+1}.', 'cyan')} "
            elif style == 'arrow':
                prefix = f"{self.colorize('→', 'green')} "
            elif style == 'check':
                prefix = f"{self.emojis['check']} "
            else:
                prefix = "  "
            
            formatted_items.append(f"{prefix}{item}")
        
        return '\n'.join(formatted_items)
    
    def format_table(self, headers: List[str], rows: List[List[str]], 
                    max_width: int = 80) -> str:
        """Formatear tabla simple"""
        if not headers or not rows:
            return ""
        
        # Calcular anchos de columna
        col_widths = []
        for i, header in enumerate(headers):
            max_width_col = len(header)
            for row in rows:
                if i < len(row):
                    max_width_col = max(max_width_col, len(str(row[i])))
            col_widths.append(min(max_width_col, max_width // len(headers)))
        
        # Formatear encabezados
        header_row = " | ".join(
            self.colorize(header.ljust(col_widths[i]), 'bright_cyan', 'bold')
            for i, header in enumerate(headers)
        )
        
        # Línea separadora
        separator = "─" * (sum(col_widths) + 3 * (len(headers) - 1))
        separator_colored = self.colorize(separator, 'gray')
        
        # Formatear filas
        formatted_rows = []
        for row in rows:
            formatted_row = " | ".join(
                str(row[i]).ljust(col_widths[i]) if i < len(row) else " " * col_widths[i]
                for i in range(len(headers))
            )
            formatted_rows.append(formatted_row)
        
        return f"{header_row}\n{separator_colored}\n" + "\n".join(formatted_rows)
    
    def format_code_block(self, code: str, language: str = None) -> str:
        """Formatear bloque de código"""
        lang_colors = {
            'python': 'green',
            'javascript': 'yellow',
            'html': 'red',
            'css': 'blue',
            'json': 'cyan',
            'bash': 'gray'
        }
        
        color = lang_colors.get(language, 'white')
        
        # Encabezado del bloque
        header = f"```{language or 'code'}"
        footer = "```"
        
        formatted_header = self.colorize(header, 'gray', 'dim')
        formatted_footer = self.colorize(footer, 'gray', 'dim')
        formatted_code = self.colorize(code, color)
        
        return f"{formatted_header}\n{formatted_code}\n{formatted_footer}"
    
    def format_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """Formatear barra de progreso"""
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100
        
        filled = int((current / total) * width) if total > 0 else 0
        empty = width - filled
        
        bar = self.colorize('█' * filled, 'green') + self.colorize('░' * empty, 'gray')
        percentage_text = self.colorize(f"{percentage:.1f}%", 'cyan')
        
        return f"[{bar}] {percentage_text}"
    
    def format_file_size(self, size_bytes: int) -> str:
        """Formatear tamaño de archivo"""
        units = [
            (1024**3, 'GB', 'red'),
            (1024**2, 'MB', 'yellow'),
            (1024, 'KB', 'green'),
            (1, 'B', 'gray')
        ]
        
        for threshold, unit, color in units:
            if size_bytes >= threshold:
                value = size_bytes / threshold
                if unit == 'B':
                    return self.colorize(f"{value:.0f}{unit}", color)
                else:
                    return self.colorize(f"{value:.1f}{unit}", color)
        
        return self.colorize("0B", 'gray')
    
    def format_timestamp(self, timestamp: float, format_type: str = 'relative') -> str:
        """Formatear timestamp"""
        if format_type == 'relative':
            return self._format_relative_time(timestamp)
        elif format_type == 'absolute':
            dt = datetime.fromtimestamp(timestamp)
            return self.colorize(dt.strftime('%Y-%m-%d %H:%M:%S'), 'gray')
        elif format_type == 'time_only':
            dt = datetime.fromtimestamp(timestamp)
            return self.colorize(dt.strftime('%H:%M:%S'), 'cyan')
        else:
            return str(timestamp)
    
    def _format_relative_time(self, timestamp: float) -> str:
        """Formatear tiempo relativo"""
        now = time.time()
        diff = now - timestamp
        
        if diff < 60:
            return self.colorize("ahora mismo", 'green')
        elif diff < 3600:
            minutes = int(diff / 60)
            return self.colorize(f"hace {minutes}m", 'yellow')
        elif diff < 86400:
            hours = int(diff / 3600)
            return self.colorize(f"hace {hours}h", 'orange' if 'orange' in self.colors else 'yellow')
        else:
            days = int(diff / 86400)
            return self.colorize(f"hace {days}d", 'red')
    
    def format_status_indicator(self, status: str) -> str:
        """Formatear indicador de estado"""
        status_formats = {
            'success': (self.emojis['success'], 'green'),
            'error': (self.emojis['error'], 'red'),
            'warning': (self.emojis['warning'], 'yellow'),
            'info': (self.emojis['info'], 'blue'),
            'pending': ('⏳', 'yellow'),
            'running': ('🔄', 'blue'),
            'completed': (self.emojis['check'], 'green'),
            'failed': (self.emojis['cross'], 'red')
        }
        
        emoji, color = status_formats.get(status.lower(), ('•', 'gray'))
        return f"{emoji} {self.colorize(status.title(), color)}"
    
    def format_command_help(self, command: str, description: str, 
                           usage: str = None, examples: List[str] = None) -> str:
        """Formatear ayuda de comando"""
        result = f"{self.colorize(command, 'cyan', 'bold')}\n"
        result += f"  {description}\n"
        
        if usage:
            result += f"\n  {self.colorize('Uso:', 'yellow')} {usage}\n"
        
        if examples:
            result += f"\n  {self.colorize('Ejemplos:', 'yellow')}\n"
            for example in examples:
                result += f"    {self.colorize(example, 'gray')}\n"
        
        return result
    
    def format_error_message(self, error: str, context: str = None, 
                           suggestions: List[str] = None) -> str:
        """Formatear mensaje de error detallado"""
        result = f"{self.emojis['error']} {self.colorize('Error:', 'red', 'bold')} {error}\n"
        
        if context:
            result += f"\n{self.colorize('Contexto:', 'yellow')} {context}\n"
        
        if suggestions:
            result += f"\n{self.colorize('Sugerencias:', 'cyan')}\n"
            result += self.format_list(suggestions, 'bullet')
        
        return result
    
    def format_success_message(self, message: str, details: Dict[str, Any] = None) -> str:
        """Formatear mensaje de éxito"""
        result = f"{self.emojis['success']} {self.colorize(message, 'green', 'bold')}\n"
        
        if details:
            result += "\n"
            for key, value in details.items():
                formatted_key = self.colorize(f"{key}:", 'cyan')
                result += f"  {formatted_key} {value}\n"
        
        return result
    
    def format_info_box(self, title: str, content: str, 
                       box_type: str = 'info') -> str:
        """Formatear caja de información"""
        box_styles = {
            'info': ('ℹ️', 'blue', '─'),
            'warning': ('⚠️', 'yellow', '─'),
            'error': ('❌', 'red', '─'),
            'success': ('✅', 'green', '─'),
            'tip': ('💡', 'cyan', '·')
        }
        
        emoji, color, char = box_styles.get(box_type, box_styles['info'])
        
        # Calcular ancho
        lines = content.split('\n')
        max_width = max(len(title) + 4, max(len(line) for line in lines) + 4, 40)
        
        # Crear caja
        top_line = self.colorize(char * max_width, color)
        title_line = f"{emoji} {self.colorize(title, color, 'bold')}"
        bottom_line = self.colorize(char * max_width, color)
        
        # Formatear contenido
        formatted_content = []
        for line in lines:
            formatted_content.append(f"  {line}")
        
        return f"{top_line}\n{title_line}\n\n" + "\n".join(formatted_content) + f"\n\n{bottom_line}"
    
    def format_diff(self, old_text: str, new_text: str) -> str:
        """Formatear diferencias entre textos"""
        old_lines = old_text.split('\n')
        new_lines = new_text.split('\n')
        
        result = []
        
        # Comparación simple línea por línea
        max_lines = max(len(old_lines), len(new_lines))
        
        for i in range(max_lines):
            old_line = old_lines[i] if i < len(old_lines) else ""
            new_line = new_lines[i] if i < len(new_lines) else ""
            
            if old_line == new_line:
                result.append(f"  {old_line}")
            elif old_line and not new_line:
                result.append(f"{self.colorize('-', 'red')} {self.colorize(old_line, 'red')}")
            elif new_line and not old_line:
                result.append(f"{self.colorize('+', 'green')} {self.colorize(new_line, 'green')}")
            else:
                result.append(f"{self.colorize('-', 'red')} {self.colorize(old_line, 'red')}")
                result.append(f"{self.colorize('+', 'green')} {self.colorize(new_line, 'green')}")
        
        return '\n'.join(result)
    
    def highlight_syntax(self, code: str, language: str) -> str:
        """Resaltado básico de sintaxis"""
        if not self.colors_enabled:
            return code
        
        if language == 'python':
            return self._highlight_python(code)
        elif language == 'javascript':
            return self._highlight_javascript(code)
        else:
            return code
    
    def _highlight_python(self, code: str) -> str:
        """Resaltado básico para Python"""
        # Palabras clave
        keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'import', 'from', 'return']
        
        for keyword in keywords:
            pattern = rf'\b{keyword}\b'
            replacement = self.colorize(keyword, 'blue', 'bold')
            code = re.sub(pattern, replacement, code)
        
        # Strings
        code = re.sub(r'"([^"]*)"', lambda m: self.colorize(f'"{m.group(1)}"', 'green'), code)
        code = re.sub(r"'([^']*)'", lambda m: self.colorize(f"'{m.group(1)}'", 'green'), code)
        
        # Comentarios
        code = re.sub(r'#.*$', lambda m: self.colorize(m.group(0), 'gray'), code, flags=re.MULTILINE)
        
        return code
    
    def _highlight_javascript(self, code: str) -> str:
        """Resaltado básico para JavaScript"""
        keywords = ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'return', 'class']
        
        for keyword in keywords:
            pattern = rf'\b{keyword}\b'
            replacement = self.colorize(keyword, 'blue', 'bold')
            code = re.sub(pattern, replacement, code)
        
        return code
    
    def strip_colors(self, text: str) -> str:
        """Remover códigos de color del texto"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)