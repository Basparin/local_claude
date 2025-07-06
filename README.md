# LocalClaude 🧠

CLI inteligente que aspira a ser tu **compañero colaborativo de IA** para proyectos complejos de AGI, sistemas avanzados y research de IA.

## 🎯 Visión y Objetivo

**Evolución**: De CLI básica → **Colaborador IA Avanzado**

LocalClaude está diseñado para convertirse en tu compañero inteligente para:
- **🤖 Proyectos de AGI/AI Research** - Análisis de modelos, experimentos, evaluación
- **🏗️ Sistemas Distribuidos Complejos** - Microservicios, arquitecturas avanzadas  
- **🔬 Research Collaboration** - Papers, implementaciones, benchmarks
- **⚡ Desarrollo de Alto Rendimiento** - Optimización, profiling, escalabilidad

**Estado Actual**: CLI funcional con base sólida  
**Objetivo**: Colaborador autónomo que entiende contexto complejo

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

## 🎯 Comandos Principales

### 🔍 Exploración Inteligente
```bash
/ls [path]              # Listar con contexto inteligente
/cat <file>             # Mostrar contenido con resumen
/tree [path]            # Estructura de directorios
/find <pattern>         # Búsqueda inteligente
```

### 🏗️ Construcción de Proyectos
```bash
/build <type> <name>    # Construir proyecto completo
/create <file>          # Crear con template inteligente
/generate <type>        # Generar código específico
```

### 📊 Análisis Avanzado
```bash
/analyze [path]         # Análisis completo de proyectos
/issues [path]          # Detectar problemas
/complexity [path]      # Métricas de complejidad
/suggest [path]         # Sugerencias de mejora
```

### 🧠 Memoria y Contexto
```bash
/context               # Estado del contexto
/memory                # Memoria persistente
/history [limit]       # Historial de comandos
```

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

### 🤖 Casos de Uso Avanzados

**AGI/AI Research**
```bash
/analyze transformer_model/ 
/generate pytorch_experiment "attention mechanism variant"
/analyze datasets/ --metrics complexity,bias,coverage
```

**Sistemas Distribuidos**
```bash
/build microservice user_service "with CQRS and event sourcing"
/analyze microservices/ --graph dependencies
/generate docker_compose "multi-service with observability"
```

**Research Collaboration**
```bash
/analyze paper_implementations/ --compare baselines
/generate benchmark "model comparison framework"
/review codebase/ --focus performance,correctness
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