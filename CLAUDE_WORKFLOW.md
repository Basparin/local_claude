# **Claude Workflow - Principios Permanentes de Trabajo**

## **📋 ESTRUCTURA DE MEMORIA PERSISTENTE**

### **🗂️ Sistema Distribuido**

LocalClaude utiliza **memoria persistente distribuida** para optimizar trabajo entre sesiones:

```
proyecto/
├── CLAUDE.md               # 🧠 Contexto principal para Claude
├── README.md               # 📖 Documentación pública
├── CLAUDE_WORKFLOW.md      # 🔄 Protocolos de trabajo (este archivo)
├── project_map.json        # 🏗️ Arquitectura de clases y métodos
├── changelog_state.json    # 📊 Estado actual y progreso
└── changelog/              # 📋 Tracking granular de implementaciones
    ├── README              # Sistema de changelogs
    ├── {timestamp}_readme_{area}     # Planificación específica
    └── {timestamp}_changelog_{area}  # Implementación detallada
```

### **🎯 Principios de Organización**

#### **📚 Documentos Estáticos** (cambios solo en saltos grandes)
- **CLAUDE.md** - Contexto y estado del proyecto
- **README.md** - Documentación pública permanente
- **CLAUDE_WORKFLOW.md** - Protocolos de trabajo estables
- **changelog/README** - Instrucciones del sistema

#### **📊 Documentos Dinámicos** (actualizaciones constantes)
- **project_map.json** - Arquitectura + estado de clases
- **changelog_state.json** - Progreso + enfoque actual
- **changelog/{timestamps}** - Tracking detallado

---

## **🌳 WORKFLOW DE BRANCHES**

### **📏 Reglas de Oro**
1. **Cambios arquitecturales** → Actualizar `project_map.json`
2. **Progreso específico** → Actualizar `changelog_state.json`
3. **Implementaciones complejas** → Documentar en `changelog/`
4. **Todo cambio** → Seguir workflow estructurado

### **🔄 Flujo de Trabajo Estándar**

#### **1. 🎯 Inicio de Sesión**
```bash
# Consultar contexto actual
python3 changelog/changelog_tracker.py --context

# Ver protocolos si es necesario
cat CLAUDE_WORKFLOW.md
```

#### **2. 🛠️ Seleccionar Tarea**
```bash
# Cambiar enfoque si es necesario
python3 changelog/changelog_tracker.py --focus [area]

# Consultar estado específico del área
jq '.areas["[area]"]' changelog_state.json
```

#### **3. 🔄 Desarrollar Cambios**
```bash
# Trabajar en el código
# Usar branch específica si es feature grande
git checkout -b feature/[area]
```

#### **4. 📝 Actualizar Estado (OBLIGATORIO)**
```bash
# Actualizar progreso mientras trabajas
python3 changelog/changelog_tracker.py --progress [area] [%] --next "descripción"

# Para cambios arquitecturales: actualizar project_map.json
# Para detalles específicos: actualizar en tiempo real
```

#### **5. ✅ Commit Estructurado**
```bash
git add .
git commit -m "feat/fix: descripción del cambio

📝 Estado actualizado:
- changelog_state.json: [area] al [%]%
- project_map.json: [cambios arquitecturales si aplica]
- Próxima acción: [definida]

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### **6. 🎉 Al Completar Área**
```bash
# Marcar como completada
python3 changelog/changelog_tracker.py --complete [area]

# Merge a main si era branch
git checkout main && git merge feature/[area]
git branch -D feature/[area]
```

---

## **📋 PROTOCOLO DE ACTUALIZACIÓN DE MEMORIA**

### **🧠 Cuándo Actualizar Cada Documento**

#### **project_map.json** (Solo cambios arquitecturales)
- ✅ Nuevas clases/métodos añadidos
- ✅ Estructura de dependencias cambiada
- ✅ Estado de testing de componentes
- ✅ Performance de clases mejorado/degradado

#### **changelog_state.json** (Progreso en tiempo real)
- ✅ Todo progreso en área activa
- ✅ Cambio de enfoque
- ✅ Completación de tareas
- ✅ Definición de próximas acciones

#### **changelog/** (Implementaciones específicas)
- ✅ Features complejas que requieren planificación
- ✅ Fixes críticos con múltiples pasos
- ✅ Optimizaciones con métricas específicas
- ✅ Refactorings significativos

---

## **🛠️ COMANDOS ESENCIALES**

### **📊 Consulta de Estado**
```bash
# Estado actual del trabajo
python3 changelog/changelog_tracker.py --context

# Arquitectura específica
jq '.classes["ClaseName"]' project_map.json

# Estado del repositorio
git status && git branch
```

### **🔄 Actualización de Progreso**
```bash
# Progreso en área actual
python3 changelog/changelog_tracker.py --progress [area] [%] --next "acción"

# Cambio de enfoque
python3 changelog/changelog_tracker.py --focus [nueva-area]

# Completar trabajo
python3 changelog/changelog_tracker.py --complete [area]
```

### **📋 Gestión de Documentación**
```bash
# Crear changelog para feature compleja
python3 changelog/changelog_tracker.py --create [area] --priority [level]

# Verificar estado de branches
git branch -a

# Ver roadmap general
python3 changelog/changelog_tracker.py --roadmap
```

---

## **⚠️ REGLAS CRÍTICAS**

### **🚫 NUNCA**
- Trabajar sin consultar contexto actual (`--context`)
- Hacer cambios sin actualizar estado correspondiente
- Perder trazabilidad de decisiones tomadas
- Modificar documentos estáticos sin justificación
- Mergear branches con tests failing

### **✅ SIEMPRE**
- Consultar contexto al inicio de sesión
- Actualizar progreso mientras trabajas
- Documentar cambios arquitecturales en `project_map.json`
- Mantener `changelog_state.json` actualizado
- Seguir estructura de commits establecida
- Completar tareas antes de cambiar enfoque

---

## **🎯 OBJETIVOS DE ESTE WORKFLOW**

1. **🧠 Memoria perfecta** - Estado persistente entre sesiones
2. **🔄 Continuidad eficiente** - Claude puede retomar trabajo inmediatamente
3. **📊 Trazabilidad completa** - Todo cambio documentado apropiadamente
4. **⚡ Navegación rápida** - Context switching optimizado
5. **🎯 Enfoque determinístico** - Trabajo organizado por prioridades
6. **📈 Escalabilidad inteligente** - Sistema que crece sin sobrecargar

---

**🎉 Este workflow está diseñado específicamente para maximizar la eficiencia de Claude en el desarrollo de LocalClaude, manteniendo memoria perfecta y trazabilidad completa entre sesiones.**

---

**Principios Estables - Versión 2.0**  
**Sistema**: Memoria distribuida con estado persistente  
**Optimizado para**: Colaboración eficiente Claude + LocalClaude