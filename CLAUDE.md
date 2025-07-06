# 🧠 CLAUDE.md - Contexto Principal para Claude

## 📋 Proyecto Actual

**LocalClaude** - CLI inteligente que aspira a ser **colaborador IA avanzado** para proyectos complejos.

### 🎯 Objetivo de Evolución
- **Estado Actual**: CLI funcional con base sólida (70% implementado)
- **Objetivo**: Colaborador autónomo para AGI, sistemas complejos, research de IA
- **Arquitectura**: 14 clases principales, 20+ comandos, memoria persistente

### 🏗️ Arquitectura Core
```
core/                    # Motor central - CLI engine + Ollama interface
context/                 # Memoria persistente - SQLite + compresión
workspace/               # Análisis y manipulación - código + proyectos  
security/                # Controles activos - validación + logs
ui/                      # Interfaz profesional - colores + formateo
```

## 📊 Estado Actual del Desarrollo

### ✅ Completado
- **Performance Optimization** (71,722x speedup con cache)
- **Arquitectura sólida** (14 clases mapeadas)
- **CLI funcional** (20+ comandos funcionando)
- **Memoria persistente** (SQLite + contexto)
- **Seguridad activa** (validación completa)

### 🔄 En Progreso
Ver estado actual con: `python3 changelog/changelog_tracker.py --context`

## 🧠 Sistema de Memoria Persistente

LocalClaude usa **memoria distribuida** optimizada para colaboración con Claude:

### 📁 Documentos Estáticos (cambios solo en saltos grandes)
- **CLAUDE.md** (este archivo) - Contexto principal
- **README.md** - Documentación pública
- **CLAUDE_WORKFLOW.md** - Protocolos de trabajo estables
- **changelog/README** - Sistema de tracking

### 📊 Documentos Dinámicos (actualizaciones constantes)
- **project_map.json** - Arquitectura + estado de clases
- **changelog_state.json** - Estado actual + progreso
- **changelog/{timestamps}** - Tracking granular de implementaciones

## 🔄 Workflow para Claude

### 1. Inicio de Sesión
```bash
# Ver contexto actual
python3 changelog/changelog_tracker.py --context

# Ver protocolos de trabajo
cat CLAUDE_WORKFLOW.md
```

### 2. Durante Desarrollo
```bash
# Actualizar progreso
python3 changelog/changelog_tracker.py --progress [area] [%] --next "acción"

# Cambiar enfoque
python3 changelog/changelog_tracker.py --focus [nueva-area]

# Consultar arquitectura
jq '.classes' project_map.json
```

### 3. Al Completar Trabajo
```bash
# Marcar completado
python3 changelog/changelog_tracker.py --complete [area]

# Actualizar project_map.json si hay cambios arquitecturales
# Crear changelog detallado si es implementación importante
```

## 🎯 Prioridades de Desarrollo

Las prioridades actuales se mantienen dinámicamente en:
- `changelog_state.json` - Enfoque actual + progreso
- `changelog/` - READMEs de planificación + CHANGELOGs de implementación
- Roadmap auto-generado: `python3 changelog/changelog_tracker.py --roadmap`

## 📋 Reglas de Trabajo Estables

### ✅ Siempre
- Actualizar estado en `changelog_tracker.py` al avanzar
- Documentar cambios arquitecturales en `project_map.json`
- Seguir protocolos definidos en `CLAUDE_WORKFLOW.md`
- Mantener memoria persistente actualizada

### ❌ Nunca
- Modificar documentos estáticos sin justificación
- Trabajar sin consultar contexto actual
- Hacer cambios sin actualizar tracking
- Perder trazabilidad de decisiones

## 🧬 Evolución del Sistema

### Fase Actual: CLI Inteligente
- ✅ Arquitectura robusta
- ✅ Performance optimizada
- 🔄 Testing infrastructure
- 📋 Model switching planificado

### Próxima Fase: Colaborador IA
- 🎯 Switching automático inteligente
- 🎯 Memoria semántica avanzada
- 🎯 Integración con herramientas externas
- 🎯 Análisis profundo de proyectos

### Visión Final: Colaborador AGI
- 🌟 Autonomía en tareas complejas
- 🌟 Multi-agente colaborativo
- 🌟 Self-improving capabilities
- 🌟 Distributed compute

## 🔧 Herramientas Disponibles

### Análisis Inmediato
```bash
# Estado del tracker
python3 changelog/changelog_tracker.py --context

# Arquitectura actual  
jq '.classes | keys' project_map.json

# Testing status
jq '.testing.total_tests, .testing.passing_tests' project_map.json
```

### Navegación de Código
```bash
# Buscar clases
jq '.classes["NombreClase"]' project_map.json

# Ver métodos de una clase
jq '.classes["CodeAnalyzer"].methods' project_map.json

# Performance status
jq '.analysis.performance_improvements' project_map.json
```

---

**Este archivo proporciona el contexto esencial que Claude necesita para trabajar eficientemente en LocalClaude, manteniendo trazabilidad perfecta entre sesiones.**

---

**Última actualización**: Sistema de memoria distribuida implementado  
**Mantenido por**: Sistema de tracking automático  
**Versión**: 1.0 (estática)