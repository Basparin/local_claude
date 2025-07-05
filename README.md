# LocalClaude

Una CLI inteligente que replica las capacidades de Claude Code usando Ollama localmente.

## 🚀 Características

- **Exploración inteligente** del workspace
- **Gestión automática de contexto** con compresión
- **Comunicación natural** con modelos locales
- **Comandos especializados** para desarrollo
- **Memoria persistente** entre sesiones

## 📋 Requisitos

- Python 3.8+
- Ollama instalado y corriendo
- Modelos recomendados:
  - `deepseek-r1:8b` (principal)
  - `qwen2.5-coder:1.5b` (rápido)

## 🛠️ Instalación

1. Clona/descarga este proyecto
2. Instala Ollama: https://ollama.ai/
3. Descarga los modelos recomendados:
   ```bash
   ollama pull deepseek-r1:8b
   ollama pull qwen2.5-coder:1.5b
   ```

## 🎯 Uso

```bash
cd local_claude
python main.py
```

## 📚 Comandos Disponibles

### Exploración
- `/ls [path]` - Listar archivos
- `/cat <file>` - Mostrar contenido
- `/grep <pattern>` - Buscar en archivos
- `/tree [path]` - Estructura de directorios
- `/find <pattern>` - Buscar archivos

### Sistema
- `/status` - Estado del sistema
- `/context` - Información del contexto
- `/clear` - Limpiar contexto
- `/model [name]` - Cambiar modelo
- `/help` - Ayuda completa
- `/exit` - Salir

### Conversación Natural
Simplemente escribe cualquier pregunta o solicitud.

## 🏗️ Arquitectura

```
local_claude/
├── main.py                    # Punto de entrada
├── core/                      # Motor principal
│   ├── cli_engine.py         # Motor de la CLI
│   ├── ollama_interface.py   # Comunicación con Ollama
│   └── command_processor.py  # Procesamiento de comandos
├── context/                   # Gestión de contexto
│   └── context_manager.py    # Memoria y compresión
├── workspace/                 # Exploración
│   └── explorer.py           # Navegación inteligente
├── ui/                        # Interfaz de usuario
│   └── interface.py          # Presentación
└── config/                    # Configuración
    ├── settings.py           # Configuración general
    └── models.py             # Gestión de modelos
```

## 🔧 Configuración

El sistema se configura automáticamente, pero puedes personalizar:

- **Modelos**: Edita `config/settings.py`
- **Contexto**: Ajusta límites de tokens
- **Interfaz**: Habilita/deshabilita colores

## 🚦 Estado del Proyecto

### ✅ Fase 1: Fundamentos (Completada)
- [x] Motor base de CLI
- [x] Integración con Ollama
- [x] Exploración de workspace
- [x] Gestión de contexto básica

### ⏳ Fase 2: Inteligencia (Pendiente)
- [ ] Capacidades de construcción
- [ ] Análisis de código avanzado
- [ ] Generación automática

### ⏳ Fase 3: Experiencia (Pendiente)
- [ ] Memoria persistente
- [ ] Interfaz pulida
- [ ] Comandos avanzados

## 🤖 Modelos Soportados

- **deepseek-r1:8b**: Razonamiento complejo, análisis profundo
- **qwen2.5-coder:1.5b**: Tareas rápidas, código simple
- **qwen2.5:7b**: Propósito general
- **codellama:7b**: Especializado en código

## 📊 Performance

- **Tiempo de respuesta**: < 3 segundos (tareas simples)
- **Uso de memoria**: < 2GB total
- **Contexto**: 32k tokens con compresión automática

## 🔍 Ejemplos de Uso

```bash
# Conversación natural
💬 Tú: Hola, ¿puedes ayudarme con Python?
🤖 Claude: ¡Por supuesto! Soy experto en Python...

# Exploración
💬 Tú: /ls src
📁 Contenido de 'src':
  📂 components/ (5 archivos)
  📄 main.py (2.1KB) 🐍 Python

# Análisis
💬 Tú: /cat main.py
📄 Archivo: main.py
📊 Tamaño: 2.1KB | Líneas: 67 | Tipo: 🐍 Python
```

## 🐛 Troubleshooting

### Problema: "No se pudo conectar con Ollama"
**Solución**: Verifica que Ollama esté corriendo:
```bash
ollama list
```

### Problema: "Modelo no disponible"
**Solución**: Descarga el modelo:
```bash
ollama pull deepseek-r1:8b
```

### Problema: Respuestas lentas
**Solución**: 
- Usa el modelo rápido para tareas simples
- Aumenta RAM asignada a GPU integrada en BIOS

## 🤝 Contribuciones

Este es un proyecto personal, pero las sugerencias son bienvenidas.

## 📄 Licencia

MIT License - Usa libremente.

---

**LocalClaude v1.0** - Tu asistente local inteligente 🧠