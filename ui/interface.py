"""
Interfaz de usuario para la CLI
"""

import sys
from typing import Optional

class UserInterface:
    """Interfaz de usuario de la CLI"""
    
    def __init__(self, settings):
        self.settings = settings
        self.colors_enabled = settings.cli['colors']
        
        # Códigos de color ANSI
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'gray': '\033[90m'
        }
    
    def _colorize(self, text: str, color: str) -> str:
        """Aplicar color al texto si está habilitado"""
        if not self.colors_enabled:
            return text
        
        color_code = self.colors.get(color, '')
        reset_code = self.colors['reset']
        
        return f"{color_code}{text}{reset_code}"
    
    def show_welcome(self):
        """Mostrar mensaje de bienvenida"""
        welcome_text = f"""
{self._colorize('🧠 LocalClaude v1.0', 'cyan')} {self._colorize('[Fase 1]', 'yellow')}
{self._colorize('CLI Inteligente con Ollama', 'gray')}

{self._colorize('Modelo:', 'blue')} {self.settings.models['current']}
{self._colorize('Workspace:', 'blue')} {self.settings.workspace_dir}

{self._colorize('Comandos disponibles:', 'green')}
  • {self._colorize('/help', 'cyan')} - Mostrar ayuda
  • {self._colorize('/ls [path]', 'cyan')} - Listar archivos
  • {self._colorize('/cat <file>', 'cyan')} - Mostrar archivo
  • {self._colorize('/grep <pattern>', 'cyan')} - Buscar en archivos
  • {self._colorize('/status', 'cyan')} - Estado del sistema
  • {self._colorize('/exit', 'cyan')} - Salir

{self._colorize('Escribe cualquier pregunta o usa un comando con /', 'gray')}
{self._colorize('─' * 60, 'gray')}
"""
        print(welcome_text)
    
    def get_user_input(self) -> str:
        """Obtener entrada del usuario"""
        prompt = self._colorize(self.settings.cli['prompt'], 'green')
        
        try:
            return input(prompt).strip()
        except EOFError:
            print()  # Nueva línea
            return '/exit'
    
    def show_response(self, response: str):
        """Mostrar respuesta del asistente"""
        prefix = self._colorize(self.settings.cli['response_prefix'], 'blue')
        
        # Formatear respuesta con indentación
        lines = response.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            if i == 0:
                formatted_lines.append(f"{prefix}{line}")
            else:
                # Indentar líneas adicionales
                indent = ' ' * len(self.settings.cli['response_prefix'])
                formatted_lines.append(f"{indent}{line}")
        
        print('\n'.join(formatted_lines))
        print()  # Línea en blanco después de la respuesta
    
    def show_message(self, message: str):
        """Mostrar mensaje general"""
        print(self._colorize(message, 'white'))
        print()
    
    def show_error(self, error: str):
        """Mostrar mensaje de error"""
        print(self._colorize(f"❌ {error}", 'red'))
        print()
    
    def show_warning(self, warning: str):
        """Mostrar mensaje de advertencia"""
        print(self._colorize(f"⚠️  {warning}", 'yellow'))
        print()
    
    def show_success(self, success: str):
        """Mostrar mensaje de éxito"""
        print(self._colorize(f"✅ {success}", 'green'))
        print()
    
    def show_thinking(self):
        """Mostrar indicador de procesamiento"""
        print(self._colorize("🤔 Pensando...", 'gray'), end='', flush=True)
        
        # Limpiar línea después (se llama desde donde se muestra la respuesta)
        print('\r' + ' ' * 20 + '\r', end='', flush=True)
    
    def show_status_info(self, status: dict):
        """Mostrar información de estado formateada"""
        print(self._colorize("📊 Estado del sistema:", 'blue'))
        
        for key, value in status.items():
            formatted_key = key.replace('_', ' ').title()
            print(f"  • {self._colorize(formatted_key, 'cyan')}: {value}")
        
        print()
    
    def get_help_text(self) -> str:
        """Obtener texto de ayuda"""
        help_text = f"""
{self._colorize('📋 Ayuda de LocalClaude', 'cyan')}

{self._colorize('COMANDOS DE EXPLORACIÓN:', 'green')}
  {self._colorize('/ls [path]', 'cyan')}        - Listar archivos y directorios
  {self._colorize('/cat <file>', 'cyan')}       - Mostrar contenido de archivo
  {self._colorize('/grep <pattern>', 'cyan')}   - Buscar patrón en archivos
  {self._colorize('/tree [path]', 'cyan')}      - Mostrar estructura de directorios
  {self._colorize('/find <pattern>', 'cyan')}   - Buscar archivos por nombre

{self._colorize('COMANDOS DE CONTEXTO:', 'green')}
  {self._colorize('/context', 'cyan')}          - Mostrar información del contexto
  {self._colorize('/clear', 'cyan')}            - Limpiar contexto de conversación
  {self._colorize('/compress', 'cyan')}         - Comprimir contexto manualmente

{self._colorize('COMANDOS DEL SISTEMA:', 'green')}
  {self._colorize('/status', 'cyan')}           - Mostrar estado del sistema
  {self._colorize('/model [name]', 'cyan')}     - Cambiar modelo actual
  {self._colorize('/help', 'cyan')}             - Mostrar esta ayuda
  {self._colorize('/exit', 'cyan')}             - Salir de LocalClaude

{self._colorize('COMANDOS DE CONSTRUCCIÓN:', 'green')}
  {self._colorize('/create <file> [tipo]', 'cyan')}    - Crear nuevo archivo con template
  {self._colorize('/edit <file> <inst>', 'cyan')}      - Editar archivo con instrucciones
  {self._colorize('/build <tipo> <nombre>', 'cyan')}   - Construir proyecto completo
  {self._colorize('/generate <desc> [file]', 'cyan')}  - Generar código automáticamente

{self._colorize('COMANDOS DE ANÁLISIS:', 'green')}
  {self._colorize('/analyze [path]', 'cyan')}          - Analizar proyecto o archivo
  {self._colorize('/issues [path]', 'cyan')}           - Encontrar problemas en código
  {self._colorize('/suggest <file>', 'cyan')}          - Sugerir mejoras
  {self._colorize('/complexity <file.py>', 'cyan')}    - Calcular complejidad

{self._colorize('COMANDOS AVANZADOS:', 'green')}
  {self._colorize('/compress', 'cyan')}                - Comprimir contexto manualmente
  {self._colorize('/summary', 'cyan')}                 - Resumen de la sesión

{self._colorize('COMANDOS DE MEMORIA:', 'green')}
  {self._colorize('/history [commands]', 'cyan')}      - Historial de archivos o comandos
  {self._colorize('/sessions [N]', 'cyan')}            - Mostrar sesiones recientes
  {self._colorize('/projects', 'cyan')}                - Mostrar proyectos recientes
  {self._colorize('/stats', 'cyan')}                   - Estadísticas de uso

{self._colorize('EJEMPLOS:', 'green')}
  • {self._colorize('Hola, ¿cómo estás?', 'white')} - Conversación normal
  • {self._colorize('/ls src', 'white')} - Listar archivos en directorio src
  • {self._colorize('/cat main.py', 'white')} - Mostrar contenido de main.py
  • {self._colorize('/create utils.py python', 'white')} - Crear archivo Python con template
  • {self._colorize('/edit main.py "agregar logging"', 'white')} - Editar con instrucciones
  • {self._colorize('/build python mi_proyecto', 'white')} - Crear proyecto Python completo
  • {self._colorize('/analyze', 'white')} - Analizar proyecto actual
  • {self._colorize('/generate "función para ordenar lista" sort.py', 'white')} - Generar código
  • {self._colorize('analiza este código', 'white')} - Pedirle que analice código

{self._colorize('TIPS:', 'magenta')}
  • Usa lenguaje natural para hacer preguntas
  • Los comandos con / son para operaciones específicas
  • El contexto se comprime automáticamente al llenarse
  • Puedes cambiar entre modelos según la tarea

{self._colorize('¿Más preguntas? Solo pregúntamelo directamente!', 'gray')}
"""
        return help_text
    
    def confirm_action(self, message: str) -> bool:
        """Solicitar confirmación del usuario"""
        prompt = f"{self._colorize(message, 'yellow')} (s/n): "
        
        while True:
            response = input(prompt).strip().lower()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Por favor responde 's' o 'n'")
    
    def show_progress(self, message: str, percentage: Optional[int] = None):
        """Mostrar progreso de operación"""
        if percentage is not None:
            progress_bar = '█' * (percentage // 5) + '░' * (20 - percentage // 5)
            print(f"\r{self._colorize(message, 'cyan')} [{progress_bar}] {percentage}%", end='', flush=True)
        else:
            print(f"\r{self._colorize(message, 'cyan')}...", end='', flush=True)