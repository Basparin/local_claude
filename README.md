# LocalClaude 🧠

CLI inteligente que aspira a ser tu **compañero colaborativo de IA** para proyectos complejos de AGI, sistemas avanzados y research de IA.

## 🎯 Visión y Objetivo

**Evolución**: De CLI básica → **Colaborador IA Avanzado**

LocalClaude está diseñado para convertirse en tu compañero inteligente para:
- **🤖 Proyectos de AGI/AI Research** - Análisis de modelos, experimentos, evaluación
- **🏗️ Sistemas Distribuidos Complejos** - Microservicios, arquitecturas avanzadas  
- **🔬 Research Collaboration** - Papers, implementaciones, benchmarks
- **⚡ Desarrollo de Alto Rendimiento** - Optimización, profiling, escalabilidad

**Estado Actual**: CLI conversacional con inteligencia contextual  
**Objetivo**: Colaborador IA que entiende lenguaje natural y contexto complejo  
**Filosofía**: Conversación natural > Comandos rígidos

## 🚀 Instalación Rápida

### Requisitos del Sistema
- **Python 3.8+**
- **Ollama** instalado y funcionando  
- **8GB RAM** mínimo (recomendado 16GB)
- **5GB espacio libre** para modelos

### Instalación
```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Modelos recomendados
ollama pull deepseek-r1:8b      # Razonamiento complejo
ollama pull qwen2.5-coder:1.5b  # Tareas rápidas

# 3. Clonar y ejecutar
git clone https://github.com/Basparin/local_claude.git
cd local_claude
python main.py
```

## 🧠 Interacción Conversacional

LocalClaude combina **comandos básicos** con **conversación natural inteligente** para máxima flexibilidad.

### 🔍 Exploración Básica
```bash
/ls [path]              # Listar archivos y directorios
/cat <file>             # Mostrar contenido
/tree [path]            # Estructura de directorios
/find <pattern>         # Búsqueda de archivos
```

### 🤖 Conversación Inteligente
```bash
# En lugar de comandos rígidos, usa lenguaje natural:
localclaude> "Analiza este proyecto y dime qué problemas tiene"
localclaude> "Crea un microservicio con CQRS y event sourcing"
localclaude> "Optimiza el performance de esta función"
localclaude> "Genera un experimento PyTorch para transformers"
```

### 📊 Sistema y Métricas
```bash
/status                # Estado del sistema
/metrics               # Métricas de performance y uso
/context               # Estado del contexto actual
/help                  # Ayuda y comandos disponibles
```

### 🧠 Inteligencia Contextual
- **Memoria persistente**: Recuerda conversaciones y patrones
- **Model switching**: Automático según complejidad de tarea
- **Cache inteligente**: Optimiza respuestas repetitivas
- **Análisis proactivo**: Sugiere mejoras automáticamente

## 📁 Arquitectura del Proyecto

```
local_claude/
├── core/                      # Motor central
│   ├── cli_engine.py         # Procesamiento de comandos
│   ├── ollama_interface.py   # Comunicación con modelos
│   └── command_processor.py  # Lógica de comandos
├── context/                   # Gestión de memoria
│   ├── context_manager.py    # Memoria de conversación
│   ├── memory_store.py       # Persistencia SQLite
│   └── compression.py        # Compresión inteligente
├── workspace/                 # Análisis y manipulación
│   ├── explorer.py           # Exploración inteligente
│   ├── file_manager.py       # Gestión de archivos
│   └── code_analyzer.py      # Análisis de código
├── security/                  # Controles de seguridad
└── ui/                        # Interfaz profesional
```

## 📋 Sistema de Tracking Determinístico

LocalClaude mantiene estado persistente para optimizar trabajo entre sesiones:

### Para Claude (inicio de sesión):
```bash
# Ver contexto actual
python3 changelog/changelog_tracker.py --context
# → "Enfoque actual: testing-fixes (60% completado)"
# → "Próxima acción: Fix API mismatch in test_cli_engine.py"

# Ver roadmap completo  
python3 changelog/changelog_tracker.py --roadmap
```

### Durante desarrollo:
```bash
# Actualizar progreso
python3 changelog/changelog_tracker.py --progress testing-fixes 80 --next "Update E2E tests"

# Cambiar enfoque
python3 changelog/changelog_tracker.py --focus model-switching

# Marcar completado
python3 changelog/changelog_tracker.py --complete testing-fixes
```

### Estado se mantiene en:
- `changelog_state.json` - Estado actual y progreso
- `changelog/` - Documentación detallada de implementaciones

## 🔒 Seguridad Implementada

### Validaciones Activas
- **Extensiones permitidas**: `.py`, `.js`, `.html`, `.css`, `.md`, `.txt`, `.json`
- **Rutas protegidas**: Bloqueo de `/etc`, `/usr`, `C:/Windows`
- **Límites**: 10MB por archivo, 50 archivos por sesión
- **Detección**: Patrones peligrosos, secrets, API keys

### Ejemplo de Seguridad
```bash
/create ../../../etc/passwd     # ❌ Bloqueado - fuera del workspace
/create malware.exe            # ❌ Bloqueado - extensión peligrosa
/create api_key.py "key='sk-'"  # ❌ Bloqueado - detecta API key
/create script.py              # ✅ Permitido - extensión segura
```

## 📊 Ejemplos de Uso

### 🏗️ Construcción de Proyecto
```bash
💬 Tú: /build python mi_api "API REST con autenticación"

✅ Proyecto Python 'mi_api' creado exitosamente!
📁 Estructura completa con FastAPI, JWT, tests
```

### 🤖 Casos de Uso Conversacionales

**AGI/AI Research**
```bash
localclaude> "Analiza mi modelo transformer, necesito optimizar la atención"
localclaude> "Crea un experimento para probar una variante del mecanismo de atención"
localclaude> "Evalúa este dataset, me preocupa el bias y la complejidad"
```

**Sistemas Distribuidos**
```bash
localclaude> "Diseña un microservicio de usuarios con CQRS y event sourcing"
localclaude> "Analiza las dependencias entre mis microservicios"
localclaude> "Genera docker-compose con observabilidad completa"
```

**Research Collaboration**
```bash
localclaude> "Compara estas implementaciones con los baselines del paper"
localclaude> "Crea un framework de benchmarking para comparar modelos"
localclaude> "Revisa este código, enfócate en performance y correctness"
```

## 🛠️ Desarrollo y Contribución

### Setup para Desarrolladores
```bash
git clone https://github.com/Basparin/local_claude.git
cd local_claude
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Cómo Contribuir
```bash
git checkout -b feature/your-feature
# Desarrollo
git commit -m "feat: descripción del cambio"
git push origin feature/your-feature
# Crear PR
```

## 🚨 Troubleshooting

**Comandos lentos**
```bash
/model qwen2.5-coder:1.5b  # Cambiar a modelo rápido
/clear                     # Limpiar contexto
```

**Ollama no responde**
```bash
wsl ollama serve           # En Windows con WSL
ollama list                # Verificar modelos
```

## 📝 Licencia y Soporte

- **Licencia**: MIT License
- **Issues**: [GitHub Issues](https://github.com/Basparin/local_claude/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/Basparin/local_claude/discussions)
- **Documentación**: Ver `CLAUDE_WORKFLOW.md` para desarrollo

---

**LocalClaude** - Tu futuro compañero de IA para proyectos complejos 🚀

*"De CLI básica a colaborador AGI - construyendo el futuro del desarrollo asistido por IA"*