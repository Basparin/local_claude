# **Claude Workflow - Instrucciones de Trabajo Organizadas**

## **📋 ESTRUCTURA DE MEMORIA PERSISTENTE**

### **🗂️ Organización por Proyectos**

Cada proyecto tiene **3 archivos principales** que constituyen la **memoria persistente**:

```
proyecto/
├── project_map.json    # 🧠 MEMORIA PERSISTENTE CENTRAL
├── README.md           # 📖 Documentación pública 
└── PLAN_IMPLEMENTACION.md # 🎯 Roadmap y objetivos
```

#### **🧠 project_map.json - FUENTE DE VERDAD**
- **Memoria persistente central** del proyecto
- Contiene toda la información técnica: clases, métodos, tests, dependencies
- **SE ACTUALIZA CON CADA CAMBIO** - Sin excepciones
- Permite navegación instantánea del codebase
- Es el "Claude persistente" que vive en el proyecto

#### **📖 README.md - Documentación Pública**
- Estado actual del proyecto con gaps identificados  
- Capacidades implementadas vs planificadas
- Ejemplos de uso y troubleshooting
- Información para usuarios externos

#### **🎯 PLAN_IMPLEMENTACION.md - Roadmap**
- Fases de desarrollo con objetivos específicos
- Tareas priorizadas con timeframes
- Métricas de éxito y entregables
- Evolución hacia objetivos a largo plazo

---

## **🌳 WORKFLOW DE BRANCHES**

### **📏 Regla de Oro**: 
**TODO CAMBIO DEBE ACTUALIZARSE EN project_map.json**

### **🔄 Flujo de Trabajo Estándar**

#### **1. 🎯 Seleccionar Tarea**
```bash
# Ver branches disponibles
git branch -a

# Trabajar en branch específica según prioridad
git checkout feature/performance-optimization  # o la branch correspondiente
```

#### **2. 🛠️ Desarrollar Cambios**
```bash
# Hacer cambios en el código
# Ejemplo: optimizar función en core/ollama_interface.py
```

#### **3. 📝 ACTUALIZAR MEMORIA PERSISTENTE (OBLIGATORIO)**
```bash
# Cada cambio DEBE reflejarse en project_map.json
# Actualizar:
# - Métodos modificados (performance status, etc.)
# - Tests añadidos/modificados
# - Dependencies cambiadas
# - Nuevas funcionalidades
```

#### **4. ✅ Commit Estructurado**
```bash
git add . 
git commit -m "feat/fix: descripción del cambio

📝 Cambios en project_map.json:
- Actualizado performance status de ollama_interface.chat
- Añadido test coverage para nueva función
- Modificado dependency graph

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### **5. 🔄 Merge a Main**
```bash
# Solo cuando feature esté completa
git checkout main
git merge feature/performance-optimization
git push origin main
```

---

## **🎯 PROYECTOS ACTIVOS**

### **📁 LocalClaude** 
```
Path: /mnt/c/Users/basti/Desktop/Basparin AI/local_claude/
Status: ✅ Activo - FASE 4 implementación
```

**🔑 Archivos principales:**
- **project_map.json** - 731 líneas, 14 clases mapeadas
- **README.md** - Estado actual con gaps y roadmap
- **PLAN_IMPLEMENTACION.md** - FASE 4 objetivos de prioridad alta

**🌳 Branches activas:**
- `feature/performance-optimization` - Parallel processing, model caching
- `feature/model-switching` - Switching automático de modelos  
- `fix/testing-infrastructure` - Arreglar 28 failing tests
- `feature/metrics-monitoring` - Dashboard de métricas

**🎯 Prioridades actuales:**
1. **Testing infrastructure** (crítico) - Base sólida
2. **Performance optimization** (alto impacto) - UX dramática
3. **Model switching** (UX) - Switching inteligente
4. **Metrics monitoring** (observability) - Data-driven decisions

---

## **📋 PROTOCOLO DE ACTUALIZACIÓN DE MEMORIA**

### **🧠 project_map.json - Actualización Obligatoria**

#### **Cuándo actualizar:**
- ✅ **Siempre** - Con cada commit que modifique código
- ✅ Nuevas funciones/clases añadidas
- ✅ Tests implementados o modificados  
- ✅ Dependencies cambiadas
- ✅ Performance mejorada/degradada
- ✅ Status de implementación cambiado

#### **Qué actualizar:**

```json
{
  "classes": {
    "ClaseModificada": {
      "methods": [
        {
          "name": "metodo_optimizado",
          "performance": "improved",  // ← ACTUALIZAR
          "line": 45,                 // ← VERIFICAR
          "tested": true              // ← ACTUALIZAR si se añadió test
        }
      ]
    }
  },
  "analysis": {
    "last_updated": "2024-12-06",    // ← ACTUALIZAR FECHA
    "optimization_status": {
      "ollama_interface": "optimized" // ← NUEVO STATUS
    }
  }
}
```

#### **🔍 Verificación antes de commit:**
```bash
# Checklist obligatorio:
□ project_map.json actualizado con cambios
□ Performance status reflejado si aplica  
□ Test coverage actualizado si aplica
□ Dependencies actualizadas si aplica
□ Fecha de last_updated cambiada
```

---

## **🎯 METODOLOGÍA DE TRABAJO**

### **📊 Proceso Orientado a Datos**

#### **1. 📋 Consultar Memoria Persistente**
- Leer project_map.json para entender estado actual
- Identificar gaps en testing/performance
- Revisar next_steps y prioridades

#### **2. 🎯 Seleccionar Branch/Tarea**
- Usar prioridades del PLAN_IMPLEMENTACION.md
- Trabajar en branch específica
- Un objetivo por branch

#### **3. 🛠️ Implementar con Context**
- Usar project_map.json para navegación rápida
- Mantener consistencia con arquitectura existente
- Seguir patrones establecidos

#### **4. 📝 Actualizar Memoria (CRÍTICO)**
- project_map.json refleja el cambio
- README.md si afecta capacidades públicas
- PLAN_IMPLEMENTACION.md si cambian objetivos

#### **5. ✅ Validar Integridad**
- Tests pasan (cuando estén arreglados)
- No hay regressions
- Memoria persistente está actualizada

---

## **🔄 COMANDOS FRECUENTES**

### **📁 Navegación de Proyecto**
```bash
# Ver estado actual
cd "/mnt/c/Users/basti/Desktop/Basparin AI/local_claude"
git status
git branch

# Consultar memoria persistente
cat project_map.json | jq '.analysis.next_steps.critical'

# Ver cobertura de tests actual  
cat project_map.json | jq '.testing.coverage_gaps'
```

### **🌳 Gestión de Branches**
```bash
# Trabajar en feature específica
git checkout feature/performance-optimization

# Ver todas las branches
git branch -a

# Merge cuando feature completa
git checkout main && git merge feature/performance-optimization
```

### **📝 Actualizar Memoria**
```bash
# Verificar que project_map.json está actualizado
git diff project_map.json

# Template de commit con memoria actualizada
git commit -m "feat: descripción

📝 project_map.json actualizado:
- [Cambios específicos]

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## **⚠️ REGLAS CRÍTICAS**

### **🚫 NUNCA:**
- Hacer commit sin actualizar project_map.json
- Trabajar directamente en main para features
- Perder track de cambios en la memoria persistente
- Mergear branches con tests failing (cuando estén arreglados)

### **✅ SIEMPRE:**
- Actualizar project_map.json con cada cambio
- Trabajar en branches específicas por tarea
- Mantener main estable y funcionando
- Documentar decisiones de arquitectura en memoria persistente

---

## **🎯 OBJETIVOS DE ESTE WORKFLOW**

1. **🧠 Memoria perfecta** - project_map.json como fuente de verdad
2. **🌳 Desarrollo organizado** - Branches por feature/objetivo
3. **📊 Trazabilidad completa** - Cada cambio documentado
4. **⚡ Navegación instantánea** - Context switching rápido entre tareas
5. **🔄 Escalabilidad** - Sistema que crece con el proyecto

---

**🎉 Este workflow transforma el desarrollo en un proceso estructurado, trazable y escalable, con memoria persistente perfecta del proyecto.**

---

**Versión**: 1.0  
**Fecha**: 2024-12-06  
**Proyecto**: LocalClaude  
**Claude Persistente**: project_map.json