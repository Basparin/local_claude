# 🧠 CLAUDE.md - Instrucciones de Workflow para Claude

## 🎯 INICIO DE SESIÓN RÁPIDO

**SIEMPRE ejecutar al inicio de cada sesión:**
```bash
# Ver estado actual del proyecto
python3 changelog/changelog_tracker.py --context

# Ver roadmap actualizado
python3 changelog/changelog_tracker.py --roadmap
```

**El proyecto es LocalClaude** - CLI conversacional en evolución hacia colaborador IA.

## 📋 DOCUMENTACIÓN CLAVE A CONSULTAR

### **🔍 Estado del Proyecto (Consultar SIEMPRE)**
1. **`changelog_state.json`** - Estado actual + progreso en tiempo real
2. **`project_map.json`** - Arquitectura + 15 clases + métricas  
3. **`ROADMAP_DETERMINISTICO.md`** - Estado completación (auto-generado)
4. **`ROADMAP_PLANNING.md`** - Próximas 4 funcionalidades (persistente)

### **📖 Documentación de Referencia**
1. **`README.md`** (root) - Visión conversacional del proyecto
2. **`changelog/README`** - Workflow de desarrollo y branches
3. **`CLAUDE_WORKFLOW.md`** - Protocolos estables de trabajo
4. **`changelog/{timestamp}_readme_{area}`** - Specs de funcionalidades específicas

## 🔄 WORKFLOW OPERATIVO

### **⚡ Al Iniciar Trabajo en Funcionalidad**
1. **Focus**: `python3 changelog/changelog_tracker.py --focus [area]`
2. **Branch**: `git checkout -b feature/[area]` (si no existe)
3. **README**: Leer `changelog/{timestamp}_readme_{area}` para objetivos

### **📊 Durante Desarrollo**
1. **Progreso**: `python3 changelog/changelog_tracker.py --progress [area] [%] --next "acción"`
2. **Commits**: Usar conventional commits (feat:, fix:, refactor:)
3. **Tests**: Verificar que pasan - `python -m pytest tests/`

### **✅ Al Completar**
1. **Complete**: `python3 changelog/changelog_tracker.py --complete [area]`
2. **Changelog**: Crear `changelog/{timestamp}_changelog_{area}` con detalles
3. **Tests**: Asegurar 100% passing
4. **Merge**: Solo después de testing completo

## 🎯 COMANDOS ESENCIALES

### **Estado Actual**
```bash
python3 changelog/changelog_tracker.py --context     # Estado + progreso
python3 changelog/changelog_tracker.py --roadmap     # Roadmap actualizado
cat changelog_state.json                             # Estado raw
```

### **Arquitectura** 
```bash
cat project_map.json                                 # Arquitectura completa
python3 -c "import json; print('\n'.join(json.load(open('project_map.json'))['classes'].keys()))"
```

### **Testing**
```bash
python -m pytest tests/ -v                          # Run all tests
python -m pytest tests/test_specific.py             # Run specific test
```

## 📋 REGLAS CRÍTICAS

### **✅ SIEMPRE**
- **Actualizar tracker** con cada avance significativo
- **Leer README de changelog** antes de trabajar en área
- **Crear branch** para cada funcionalidad nueva
- **Tests passing** antes de completar área

### **❌ NUNCA**
- Trabajar sin consultar `changelog_state.json`
- Modificar `ROADMAP_PLANNING.md` (es persistente)
- Saltarse el workflow de branches
- Completar área con tests fallando

## 🧠 MEMORIA INTELIGENTE

### **Sistema de Documentos**
- **Dinámicos**: `changelog_state.json`, `ROADMAP_DETERMINISTICO.md`
- **Persistentes**: `ROADMAP_PLANNING.md`, `changelog/README`
- **Por Área**: `changelog/{timestamp}_readme_{area}`

### **Filosofía**
- **Conversación natural** > Comandos rígidos
- **Chunks de 4 funcionalidades** para progreso constante  
- **Memory persistente** entre sesiones Claude
- **Trazabilidad completa** de decisiones

## 🎯 OBTENER ESTADO ACTUAL

**SIEMPRE consultar antes de trabajar:**
```bash
# Estado completo + progreso actual
python3 changelog/changelog_tracker.py --context

# Ver qué branch usar y objetivos
cat changelog/{timestamp}_readme_{area}

# Tests status
python -m pytest tests/ -v --tb=short
```

---

**CLAUDE.md v2.0** - Instrucciones operativas persistentes para Claude  
**Tipo**: Documentación estática de workflow  
**Mantenido por**: Equipo LocalClaude