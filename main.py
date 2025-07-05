#!/usr/bin/env python3
"""
LocalClaude - CLI Inteligente con Ollama
Una CLI que replica las capacidades de Claude Code usando Ollama localmente
"""

import sys
import os
import asyncio
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from core.cli_engine import CLIEngine
from config.settings import Settings

def main():
    """Punto de entrada principal"""
    try:
        # Inicializar configuración
        settings = Settings()
        
        # Crear motor de CLI
        cli = CLIEngine(settings)
        
        # Ejecutar CLI
        cli.run()
        
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()