"""
Procesador de comandos especiales
"""

from typing import Dict, Callable, List, Any, Optional

class CommandProcessor:
    """Procesador de comandos especiales de la CLI"""
    
    def __init__(self, settings):
        self.settings = settings
        self.commands: Dict[str, Callable] = {}
        self.command_prefix = settings.cli['command_prefix']
    
    def register_command(self, command_name: str, handler: Callable):
        """Registrar un nuevo comando"""
        self.commands[command_name] = handler
    
    def process_command(self, user_input: str) -> Optional[str]:
        """
        Procesar un comando especial
        
        Args:
            user_input: Entrada del usuario que comienza con el prefijo de comando
            
        Returns:
            Resultado del comando o None si no es válido
        """
        # Remover prefijo y parsear
        if not user_input.startswith(self.command_prefix):
            return None
        
        command_text = user_input[len(self.command_prefix):].strip()
        
        if not command_text:
            return self._show_available_commands()
        
        # Parsear comando y argumentos
        parts = command_text.split()
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Ejecutar comando
        if command_name in self.commands:
            try:
                return self.commands[command_name](args)
            except Exception as e:
                return f"❌ Error ejecutando comando '{command_name}': {e}"
        else:
            return f"❌ Comando desconocido: '{command_name}'. Usa /help para ver comandos disponibles."
    
    def _show_available_commands(self) -> str:
        """Mostrar comandos disponibles"""
        if not self.commands:
            return "No hay comandos disponibles"
        
        result = "📋 Comandos disponibles:\n"
        for command_name in sorted(self.commands.keys()):
            result += f"  • /{command_name}\n"
        
        result += "\nUsa /help para más información"
        return result
    
    def get_command_list(self) -> List[str]:
        """Obtener lista de comandos registrados"""
        return list(self.commands.keys())
    
    def has_command(self, command_name: str) -> bool:
        """Verificar si un comando existe"""
        return command_name in self.commands