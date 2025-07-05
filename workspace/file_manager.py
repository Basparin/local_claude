"""
Gestor de archivos para creación y edición inteligente
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class FileManager:
    """Gestor de archivos con capacidades inteligentes"""
    
    def __init__(self, settings, ollama_interface):
        self.settings = settings
        self.ollama_interface = ollama_interface
        self.workspace_dir = settings.workspace_dir
        
        # Templates para diferentes tipos de archivos
        self.templates = {
            'python': self._get_python_template(),
            'javascript': self._get_javascript_template(),
            'html': self._get_html_template(),
            'css': self._get_css_template(),
            'markdown': self._get_markdown_template(),
            'json': self._get_json_template(),
            'yaml': self._get_yaml_template(),
            'dockerfile': self._get_dockerfile_template(),
            'gitignore': self._get_gitignore_template()
        }
    
    def create_file(self, file_path: str, content: str = None, file_type: str = None) -> str:
        """
        Crear un nuevo archivo con contenido inteligente
        
        Args:
            file_path: Ruta del archivo a crear
            content: Contenido específico (opcional)
            file_type: Tipo de archivo para usar template (opcional)
        
        Returns:
            Mensaje de resultado
        """
        try:
            target_path = Path(self.workspace_dir) / file_path
            
            # Verificar si el archivo ya existe
            if target_path.exists():
                return f"❌ El archivo '{file_path}' ya existe. Usa /edit para modificarlo."
            
            # Crear directorios padre si no existen
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determinar tipo de archivo si no se especifica
            if file_type is None:
                file_type = self._detect_file_type(target_path)
            
            # Generar contenido si no se proporciona
            if content is None:
                content = self._generate_file_content(file_path, file_type)
            
            # Escribir archivo
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Mensaje de éxito
            file_size = target_path.stat().st_size
            return f"✅ Archivo creado: {file_path} ({self._format_size(file_size)})\n📝 Tipo: {file_type}\n🔧 Template aplicado automáticamente"
            
        except PermissionError:
            return f"❌ Sin permisos para crear '{file_path}'"
        except Exception as e:
            return f"❌ Error creando '{file_path}': {e}"
    
    def edit_file(self, file_path: str, instructions: str) -> str:
        """
        Editar un archivo existente con instrucciones en lenguaje natural
        
        Args:
            file_path: Ruta del archivo a editar
            instructions: Instrucciones de qué cambiar
        
        Returns:
            Mensaje de resultado
        """
        try:
            target_path = Path(self.workspace_dir) / file_path
            
            if not target_path.exists():
                return f"❌ El archivo '{file_path}' no existe. Usa /create para crearlo."
            
            if not target_path.is_file():
                return f"❌ '{file_path}' no es un archivo."
            
            # Leer contenido actual
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
            except UnicodeDecodeError:
                return f"❌ '{file_path}' parece ser un archivo binario."
            
            # Generar nuevo contenido usando LLM
            new_content = self._generate_edited_content(current_content, instructions, file_path)
            
            if new_content is None:
                return f"❌ No se pudo procesar las instrucciones para '{file_path}'"
            
            # Crear backup
            backup_path = self._create_backup(target_path)
            
            # Escribir nuevo contenido
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Estadísticas
            old_lines = len(current_content.split('\n'))
            new_lines = len(new_content.split('\n'))
            change = new_lines - old_lines
            
            result = f"✅ Archivo editado: {file_path}\n"
            result += f"📊 Cambios: {old_lines} → {new_lines} líneas ({change:+d})\n"
            result += f"💾 Backup creado: {backup_path.name}"
            
            return result
            
        except Exception as e:
            return f"❌ Error editando '{file_path}': {e}"
    
    def build_project(self, project_type: str, project_name: str) -> str:
        """
        Construir un proyecto completo desde cero
        
        Args:
            project_type: Tipo de proyecto (python, web, api, etc.)
            project_name: Nombre del proyecto
        
        Returns:
            Mensaje de resultado
        """
        try:
            project_path = Path(self.workspace_dir) / project_name
            
            if project_path.exists():
                return f"❌ El directorio '{project_name}' ya existe."
            
            # Crear estructura según el tipo
            if project_type.lower() == 'python':
                return self._build_python_project(project_path, project_name)
            elif project_type.lower() == 'web':
                return self._build_web_project(project_path, project_name)
            elif project_type.lower() == 'api':
                return self._build_api_project(project_path, project_name)
            else:
                return f"❌ Tipo de proyecto no soportado: {project_type}. Usa: python, web, api"
            
        except Exception as e:
            return f"❌ Error construyendo proyecto: {e}"
    
    def generate_code(self, description: str, file_path: str = None) -> str:
        """
        Generar código basado en descripción natural
        
        Args:
            description: Descripción de lo que se quiere generar
            file_path: Archivo donde guardar (opcional)
        
        Returns:
            Código generado o mensaje de resultado
        """
        try:
            # Usar LLM para generar código
            prompt = f"""Genera código basado en esta descripción: {description}

Requisitos:
- Código limpio y bien documentado
- Incluir comentarios explicativos
- Seguir buenas prácticas
- Código funcional y completo

Descripción: {description}"""

            # Determinar modelo a usar (rápido para código simple)
            model = self.settings.models['fast'] if len(description) < 100 else self.settings.models['primary']
            
            messages = [{'role': 'user', 'content': prompt}]
            generated_code = self.ollama_interface.chat(messages, model)
            
            if not generated_code:
                return "❌ No se pudo generar el código solicitado"
            
            # Si se especifica archivo, guardar
            if file_path:
                result = self.create_file(file_path, generated_code)
                return f"🚀 Código generado y guardado:\n{result}"
            else:
                return f"🚀 Código generado:\n\n```\n{generated_code}\n```"
            
        except Exception as e:
            return f"❌ Error generando código: {e}"
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detectar tipo de archivo por extensión"""
        suffix = file_path.suffix.lower()
        
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.dockerfile': 'dockerfile',
            '.gitignore': 'gitignore',
            '.txt': 'text',
            '.sh': 'bash',
            '.sql': 'sql'
        }
        
        return type_map.get(suffix, 'text')
    
    def _generate_file_content(self, file_path: str, file_type: str) -> str:
        """Generar contenido inicial para un archivo"""
        template = self.templates.get(file_type, "")
        
        if template:
            # Personalizar template con información del archivo
            file_name = Path(file_path).stem
            template = template.replace('{{FILE_NAME}}', file_name)
            template = template.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d'))
            template = template.replace('{{YEAR}}', str(datetime.now().year))
        
        return template
    
    def _generate_edited_content(self, current_content: str, instructions: str, file_path: str) -> Optional[str]:
        """Generar contenido editado usando LLM"""
        try:
            prompt = f"""Edita el siguiente archivo según las instrucciones proporcionadas.

ARCHIVO: {file_path}

CONTENIDO ACTUAL:
```
{current_content}
```

INSTRUCCIONES: {instructions}

REQUISITOS:
- Mantén la estructura y estilo existente
- Solo modifica lo necesario según las instrucciones
- Preserva comentarios y documentación existente
- Asegúrate de que el código siga funcionando
- Retorna SOLO el contenido editado, sin explicaciones adicionales

CONTENIDO EDITADO:"""

            messages = [{'role': 'user', 'content': prompt}]
            return self.ollama_interface.chat(messages, self.settings.models['primary'])
            
        except Exception as e:
            print(f"Error generando contenido editado: {e}")
            return None
    
    def _create_backup(self, file_path: Path) -> Path:
        """Crear backup de un archivo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = file_path.with_suffix(f'{file_path.suffix}.backup_{timestamp}')
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _format_size(self, size: int) -> str:
        """Formatear tamaño de archivo"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size/(1024*1024):.1f}MB"
    
    # Templates para diferentes tipos de archivos
    def _get_python_template(self) -> str:
        return '''#!/usr/bin/env python3
"""
{{FILE_NAME}}.py

Descripción del módulo

Autor: LocalClaude
Fecha: {{DATE}}
"""


def main():
    """Función principal"""
    pass


if __name__ == "__main__":
    main()
'''
    
    def _get_javascript_template(self) -> str:
        return '''/**
 * {{FILE_NAME}}.js
 * 
 * Descripción del módulo
 * 
 * @author LocalClaude
 * @date {{DATE}}
 */

'use strict';

/**
 * Función principal
 */
function main() {
    // Código aquí
}

// Ejecutar si es el archivo principal
if (require.main === module) {
    main();
}
'''
    
    def _get_html_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{FILE_NAME}}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{FILE_NAME}}</h1>
        <p>Página creada el {{DATE}}</p>
    </div>
</body>
</html>
'''
    
    def _get_css_template(self) -> str:
        return '''/*
 * {{FILE_NAME}}.css
 * 
 * Estilos para {{FILE_NAME}}
 * 
 * Creado: {{DATE}}
 */

/* Reset básico */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
}

/* Contenedor principal */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}
'''
    
    def _get_markdown_template(self) -> str:
        return '''# {{FILE_NAME}}

Descripción del proyecto/documento.

## Características

- Característica 1
- Característica 2
- Característica 3

## Instalación

```bash
# Comandos de instalación
```

## Uso

```bash
# Ejemplos de uso
```

## Contribuciones

Las contribuciones son bienvenidas.

## Licencia

MIT License - {{YEAR}}
'''
    
    def _get_json_template(self) -> str:
        return '''{
  "name": "{{FILE_NAME}}",
  "version": "1.0.0",
  "description": "Descripción del proyecto",
  "created": "{{DATE}}",
  "author": "LocalClaude",
  "config": {
    "environment": "development",
    "debug": true
  }
}
'''
    
    def _get_yaml_template(self) -> str:
        return '''# {{FILE_NAME}}.yaml
# Configuración creada el {{DATE}}

name: {{FILE_NAME}}
version: "1.0.0"
description: "Descripción de la configuración"

config:
  environment: development
  debug: true
  
settings:
  # Configuraciones específicas aquí
'''
    
    def _get_dockerfile_template(self) -> str:
        return '''# {{FILE_NAME}} Dockerfile
# Creado el {{DATE}}

FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "main.py"]
'''
    
    def _get_gitignore_template(self) -> str:
        return '''# {{FILE_NAME}} - Archivos a ignorar
# Creado el {{DATE}}

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment variables
.env
'''
    
    def _build_python_project(self, project_path: Path, project_name: str) -> str:
        """Construir proyecto Python completo"""
        try:
            # Crear estructura de directorios
            directories = [
                project_path,
                project_path / 'src' / project_name,
                project_path / 'tests',
                project_path / 'docs',
                project_path / 'scripts'
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Crear archivos principales
            files_to_create = {
                'README.md': self._get_project_readme(project_name, 'python'),
                'requirements.txt': '# Dependencias del proyecto\n',
                'setup.py': self._get_setup_py(project_name),
                '.gitignore': self.templates['gitignore'].replace('{{FILE_NAME}}', project_name),
                f'src/{project_name}/__init__.py': f'"""Paquete {project_name}"""\n__version__ = "0.1.0"\n',
                f'src/{project_name}/main.py': self.templates['python'].replace('{{FILE_NAME}}', 'main'),
                'tests/__init__.py': '',
                'tests/test_main.py': self._get_test_template(project_name)
            }
            
            created_files = []
            for file_path, content in files_to_create.items():
                full_path = project_path / file_path
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d')))
                created_files.append(file_path)
            
            result = f"🎉 Proyecto Python '{project_name}' creado exitosamente!\n\n"
            result += "📁 Estructura creada:\n"
            for file_path in created_files:
                result += f"  ✅ {file_path}\n"
            
            result += f"\n📋 Siguiente paso:\n"
            result += f"  cd {project_name}\n"
            result += f"  python -m venv venv\n"
            result += f"  source venv/bin/activate  # o venv\\Scripts\\activate en Windows\n"
            result += f"  pip install -r requirements.txt\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error construyendo proyecto Python: {e}"
    
    def _build_web_project(self, project_path: Path, project_name: str) -> str:
        """Construir proyecto web completo"""
        # Similar estructura pero para proyecto web
        pass
    
    def _build_api_project(self, project_path: Path, project_name: str) -> str:
        """Construir proyecto API completo"""
        # Similar estructura pero para API
        pass
    
    def _get_project_readme(self, project_name: str, project_type: str) -> str:
        return f'''# {project_name}

Proyecto {project_type} creado con LocalClaude.

## Descripción

Describe aquí tu proyecto.

## Instalación

```bash
git clone <repository>
cd {project_name}
# Instrucciones específicas de instalación
```

## Uso

```bash
# Ejemplos de uso
```

## Estructura del Proyecto

```
{project_name}/
├── src/
├── tests/
├── docs/
└── scripts/
```

## Desarrollo

Instrucciones para desarrolladores.

## Licencia

MIT License
'''
    
    def _get_setup_py(self, project_name: str) -> str:
        return f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    description="Descripción del proyecto",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    python_requires=">=3.8",
    install_requires=[
        # Dependencias aquí
    ],
    extras_require={{
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ]
    }},
    entry_points={{
        "console_scripts": [
            "{project_name}=src.{project_name}.main:main",
        ],
    }},
)
'''
    
    def _get_test_template(self, project_name: str) -> str:
        return f'''"""
Tests para {project_name}
"""

import pytest
from src.{project_name}.main import main


def test_main():
    """Test básico para la función main"""
    # TODO: Implementar tests reales
    assert main is not None


def test_example():
    """Test de ejemplo"""
    assert 1 + 1 == 2
'''