#!/usr/bin/env python3
"""
Herramienta de Auto-tracking de Changelogs - LocalClaude

Sistema determinístico que analiza automáticamente:
- READMEs sin CHANGELOG correspondiente
- Estados pendientes por prioridad  
- Branches sin mergear con changelogs
- Métricas de tiempo de implementación
- Roadmap basado en README.md
"""

import os
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import hashlib


class ChangelogTracker:
    """Auto-tracker inteligente para sistema de changelogs con estado persistente"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.changelog_dir = self.project_root / "changelog"
        self.readme_path = self.project_root / "README.md"
        self.project_map_path = self.project_root / "project_map.json"
        self.state_file = self.project_root / "changelog_state.json"
        
        # Initialize if needed
        self.changelog_dir.mkdir(exist_ok=True)
        self._load_state()
    
    def _load_state(self):
        """Carga el estado persistente del tracker"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
        else:
            self.state = {
                "current_focus": None,
                "areas": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_state()
    
    def _save_state(self):
        """Guarda el estado persistente"""
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def get_current_context(self) -> Dict[str, Any]:
        """Obtiene contexto actual para Claude - lo que necesita al empezar sesión"""
        if not self.state.get("current_focus"):
            return {"message": "No hay enfoque activo. Usar --focus [area] para comenzar."}
        
        focus = self.state["current_focus"]
        area_data = self.state["areas"].get(focus, {})
        
        return {
            "current_focus": focus,
            "status": area_data.get("status", "not_started"),
            "progress": area_data.get("progress", 0),
            "next_action": area_data.get("next_action", "Definir próxima acción"),
            "started": area_data.get("started"),
            "estimated_completion": area_data.get("estimated_completion")
        }
    
    def update_progress(self, area: str, progress: int, next_action: str = None):
        """Actualiza progreso de un área específica"""
        if area not in self.state["areas"]:
            self.state["areas"][area] = {
                "status": "not_started",
                "progress": 0,
                "started": None
            }
        
        area_data = self.state["areas"][area]
        area_data["progress"] = progress
        
        if next_action:
            area_data["next_action"] = next_action
        
        # Auto-update status based on progress
        if progress == 0:
            area_data["status"] = "not_started"
        elif progress == 100:
            area_data["status"] = "completed"
            area_data["completed"] = datetime.now().isoformat()
        else:
            area_data["status"] = "in_progress"
            if not area_data.get("started"):
                area_data["started"] = datetime.now().isoformat()
        
        self._save_state()
        print(f"✅ {area}: {progress}% completado")
        if next_action:
            print(f"🎯 Próxima acción: {next_action}")
    
    def set_focus(self, area: str):
        """Establece el área de enfoque actual"""
        self.state["current_focus"] = area
        if area not in self.state["areas"]:
            self.state["areas"][area] = {
                "status": "not_started",
                "progress": 0,
                "started": None
            }
        self._save_state()
        print(f"🎯 Enfoque establecido en: {area}")
    
    def mark_completed(self, area: str):
        """Marca un área como completada"""
        self.update_progress(area, 100)
        print(f"🎉 {area} completado!")
        
        # Si era el enfoque actual, limpiar enfoque
        if self.state.get("current_focus") == area:
            self.state["current_focus"] = None
            self._save_state()
    
    def sync_architecture_map(self):
        """Auto-genera project_map.json minimalista desde código real"""
        print("🔄 Escaneando arquitectura del proyecto...")
        
        architecture = {
            "generated_at": datetime.now().isoformat(),
            "generated_by": "changelog_tracker.py --sync",
            "project_root": str(self.project_root),
            "classes": {},
            "commands": {},
            "stats": {}
        }
        
        # Escanear clases principales
        classes_found = self._scan_python_classes()
        architecture["classes"] = classes_found
        
        # Escanear comandos CLI si existe
        commands_found = self._scan_cli_commands()
        architecture["commands"] = commands_found
        
        # Estadísticas básicas
        architecture["stats"] = {
            "total_classes": len(classes_found),
            "total_commands": len(commands_found),
            "python_files": self._count_python_files(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Guardar project_map.json
        with open(self.project_map_path, 'w', encoding='utf-8') as f:
            json.dump(architecture, f, indent=2, ensure_ascii=False)
        
        print(f"✅ project_map.json regenerado:")
        print(f"   📦 {len(classes_found)} clases encontradas")
        print(f"   🎯 {len(commands_found)} comandos CLI")
        print(f"   📄 {architecture['stats']['python_files']} archivos Python")
        
        return architecture
    
    def _scan_python_classes(self) -> Dict[str, Any]:
        """Escanea archivos .py y extrae clases principales"""
        classes = {}
        
        # Directorios principales a escanear
        scan_dirs = ['core', 'context', 'workspace', 'security', 'ui', 'config']
        
        for dir_name in scan_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
                
            for py_file in dir_path.glob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Buscar definiciones de clase
                    import re
                    class_matches = re.finditer(r'^class\s+(\w+).*?:', content, re.MULTILINE)
                    
                    for match in class_matches:
                        class_name = match.group(1)
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Extraer docstring si existe
                        docstring = self._extract_docstring(content, match.end())
                        
                        classes[class_name] = {
                            "file": str(py_file.relative_to(self.project_root)).replace('\\', '/'),
                            "line": line_num,
                            "description": docstring or f"Clase {class_name}",
                            "directory": dir_name
                        }
                        
                except Exception as e:
                    continue  # Skip files with issues
        
        return classes
    
    def _scan_cli_commands(self) -> Dict[str, Any]:
        """Escanea comandos CLI registrados"""
        commands = {}
        
        cli_engine_path = self.project_root / "core" / "cli_engine.py"
        if not cli_engine_path.exists():
            return commands
        
        try:
            content = cli_engine_path.read_text(encoding='utf-8')
            
            # Buscar register_command calls
            import re
            command_matches = re.finditer(r'register_command\([\'"]([^\'"]+)[\'"]', content)
            
            for match in command_matches:
                command_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                commands[command_name] = {
                    "file": "core/cli_engine.py",
                    "line": line_num,
                    "type": "cli_command"
                }
                
        except Exception:
            pass
        
        return commands
    
    def _extract_docstring(self, content: str, start_pos: int) -> Optional[str]:
        """Extrae docstring de una clase"""
        try:
            # Look for docstring after class definition
            remaining = content[start_pos:]
            lines = remaining.split('\n')
            
            for i, line in enumerate(lines[:5]):  # Check first 5 lines
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    quote = stripped[:3]
                    if stripped.endswith(quote) and len(stripped) > 6:
                        # Single line docstring
                        return stripped[3:-3].strip()
                    else:
                        # Multi-line docstring
                        for j, next_line in enumerate(lines[i+1:i+10]):
                            if quote in next_line:
                                docstring_lines = [stripped[3:]] + lines[i+1:i+1+j]
                                docstring_lines[-1] = docstring_lines[-1].split(quote)[0]
                                return ' '.join(line.strip() for line in docstring_lines if line.strip())
                        
        except Exception:
            pass
        
        return None
    
    def _count_python_files(self) -> int:
        """Cuenta archivos .py en el proyecto"""
        count = 0
        for py_file in self.project_root.rglob('*.py'):
            if '.git' not in str(py_file) and '__pycache__' not in str(py_file):
                count += 1
        return count
    
    def scan_changelog_status(self) -> Dict[str, Any]:
        """
        Analiza el estado completo del sistema de changelogs
        
        Returns:
            Dict con análisis completo del estado
        """
        status = {
            "scan_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "readme_files": self._scan_readme_files(),
            "changelog_files": self._scan_changelog_files(),
            "branches_status": self._scan_branches_status(),
            "pending_work": self._identify_pending_work(),
            "completion_metrics": self._calculate_completion_metrics(),
            "roadmap_analysis": self._analyze_roadmap(),
            "priority_alerts": self._generate_priority_alerts()
        }
        
        return status
    
    def _scan_readme_files(self) -> List[Dict[str, Any]]:
        """Escanear archivos README de changelogs"""
        readme_files = []
        
        for readme_file in self.changelog_dir.glob("*_readme_*"):
            info = self._parse_changelog_filename(readme_file.name)
            if info:
                content = self._parse_readme_content(readme_file)
                info.update(content)
                readme_files.append(info)
        
        return sorted(readme_files, key=lambda x: x['timestamp'], reverse=True)
    
    def _scan_changelog_files(self) -> List[Dict[str, Any]]:
        """Escanear archivos CHANGELOG de implementaciones"""
        changelog_files = []
        
        for changelog_file in self.changelog_dir.glob("*_changelog_*"):
            info = self._parse_changelog_filename(changelog_file.name)
            if info:
                content = self._parse_changelog_content(changelog_file)
                info.update(content)
                changelog_files.append(info)
        
        return sorted(changelog_files, key=lambda x: x['timestamp'], reverse=True)
    
    def _scan_branches_status(self) -> Dict[str, Any]:
        """Analizar estado de branches relacionadas con changelogs"""
        try:
            # Get all branches
            result = subprocess.run(
                ["git", "branch", "-a"], 
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode != 0:
                return {"error": "Git not available or not a git repo"}
            
            branches = []
            current_branch = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('* '):
                    current_branch = line[2:]
                    branches.append({"name": line[2:], "current": True})
                elif line.startswith('remotes/'):
                    branches.append({"name": line.replace('remotes/origin/', ''), "remote": True})
                else:
                    branches.append({"name": line, "current": False})
            
            # Analyze branch relationships with changelogs
            branch_analysis = self._analyze_branch_changelog_relationship(branches)
            
            return {
                "current_branch": current_branch,
                "all_branches": branches,
                "changelog_branches": branch_analysis,
                "orphaned_branches": self._identify_orphaned_branches(branches)
            }
            
        except Exception as e:
            return {"error": f"Failed to scan branches: {e}"}
    
    def _parse_changelog_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Parse changelog filename according to format:
        {timestamp}_{type}_{area}
        """
        try:
            parts = filename.split('_', 2)
            if len(parts) < 3:
                return None
                
            timestamp_str = parts[0]
            file_type = parts[1]
            area = parts[2]
            
            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d")
            
            return {
                "filename": filename,
                "timestamp": timestamp.isoformat(),
                "type": file_type,
                "area": area,
                "file_path": str(self.changelog_dir / filename)
            }
            
        except Exception:
            return None
    
    def _parse_readme_content(self, readme_path: Path) -> Dict[str, Any]:
        """Parse contenido de README para extraer información"""
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            # Extract key information using regex
            info = {
                "branch": self._extract_field(content, r"Branch.*?:\s*(.*?)$"),
                "area": self._extract_field(content, r"Área.*?:\s*(.*?)$"),
                "priority": self._extract_field(content, r"Prioridad.*?:\s*(.*?)$"),
                "status": self._extract_field(content, r"Estado.*?:\s*(.*?)$"),
                "problem": self._extract_field(content, r"Problema.*?:\s*(.*?)$"),
                "objectives": self._extract_list(content, r"Objetivos.*?:(.*?)(?=##|$)", r"[-*]\s*(.+)"),
                "success_criteria": self._extract_list(content, r"Criterios de éxito.*?:(.*?)(?=##|$)", r"[-*]\s*(.+)"),
                "content_size": len(content),
                "last_modified": datetime.fromtimestamp(readme_path.stat().st_mtime).isoformat()
            }
            
            return info
            
        except Exception as e:
            return {"parse_error": str(e)}
    
    def _parse_changelog_content(self, changelog_path: Path) -> Dict[str, Any]:
        """Parse contenido de CHANGELOG para extraer métricas"""
        try:
            content = changelog_path.read_text(encoding='utf-8')
            
            info = {
                "implementation_status": self._extract_field(content, r"Estado.*?:\s*(.*?)$"),
                "files_modified": len(re.findall(r"[*-]\s*\*\*(.+?)\*\*", content)),
                "performance_metrics": self._extract_performance_metrics(content),
                "tests_added": len(re.findall(r"test.*?implementad", content, re.IGNORECASE)),
                "breaking_changes": "breaking" in content.lower(),
                "content_size": len(content),
                "completion_date": self._extract_field(content, r"Fecha.*?finalización.*?:\s*(.*?)$"),
                "last_modified": datetime.fromtimestamp(changelog_path.stat().st_mtime).isoformat()
            }
            
            return info
            
        except Exception as e:
            return {"parse_error": str(e)}
    
    def _extract_field(self, content: str, pattern: str) -> Optional[str]:
        """Extract single field using regex"""
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_list(self, content: str, section_pattern: str, item_pattern: str) -> List[str]:
        """Extract list of items from section"""
        section_match = re.search(section_pattern, content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if not section_match:
            return []
            
        section_text = section_match.group(1)
        items = re.findall(item_pattern, section_text, re.MULTILINE)
        return [item.strip() for item in items]
    
    def _extract_performance_metrics(self, content: str) -> Dict[str, str]:
        """Extract performance metrics from changelog"""
        metrics = {}
        
        # Look for speedup patterns
        speedup_patterns = [
            r"(\w+)\s*:\s*([\d.]+)x\s*speedup",
            r"(\w+)\s*.*?([\d.]+)%\s*mejora",
            r"(\w+)\s*.*?([\d,]+)x\s*speedup"
        ]
        
        for pattern in speedup_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                metrics[match[0]] = match[1]
        
        return metrics
    
    def _identify_pending_work(self) -> List[Dict[str, Any]]:
        """Identificar trabajo pendiente basado en READMEs sin CHANGELOGs"""
        readmes = self._scan_readme_files()
        changelogs = self._scan_changelog_files()
        
        # Create mapping of areas with changelogs
        completed_areas = {cl['area'] for cl in changelogs}
        
        pending = []
        for readme in readmes:
            if readme['area'] not in completed_areas:
                # Calculate age
                readme_date = datetime.fromisoformat(readme['timestamp'])
                age_days = (datetime.now() - readme_date).days
                
                pending.append({
                    "area": readme['area'],
                    "priority": readme.get('priority', 'unknown'),
                    "status": readme.get('status', 'unknown'),
                    "branch": readme.get('branch'),
                    "age_days": age_days,
                    "objectives": readme.get('objectives', []),
                    "urgency_score": self._calculate_urgency_score(readme, age_days)
                })
        
        return sorted(pending, key=lambda x: x['urgency_score'], reverse=True)
    
    def _calculate_urgency_score(self, readme: Dict, age_days: int) -> float:
        """Calcular score de urgencia basado en prioridad y edad"""
        priority_weights = {
            'crítica': 10,
            'critica': 10,
            'critical': 10,
            'alta': 7,
            'high': 7,
            'media': 4,
            'medium': 4,
            'baja': 1,
            'low': 1
        }
        
        priority = readme.get('priority', '').lower()
        base_score = priority_weights.get(priority, 2)
        
        # Age factor: +0.1 per day
        age_factor = min(age_days * 0.1, 5)  # Cap at 5 points
        
        # Status factor
        status_weights = {
            'bloqueado': 3,
            'blocked': 3,
            'en-progreso': 1,
            'in_progress': 1,
            'in-progress': 1,
            'planificado': 0,
            'planned': 0
        }
        
        status = readme.get('status', '').lower()
        status_factor = status_weights.get(status, 0)
        
        return base_score + age_factor + status_factor
    
    def _calculate_completion_metrics(self) -> Dict[str, Any]:
        """Calcular métricas de completación del proyecto"""
        readmes = self._scan_readme_files()
        changelogs = self._scan_changelog_files()
        
        total_work_items = len(readmes)
        completed_items = len(changelogs)
        
        completion_rate = (completed_items / total_work_items * 100) if total_work_items > 0 else 100
        
        # Calculate average implementation time
        implementation_times = []
        for changelog in changelogs:
            area = changelog['area']
            matching_readme = next((r for r in readmes if r['area'] == area), None)
            
            if matching_readme:
                readme_date = datetime.fromisoformat(matching_readme['timestamp'])
                changelog_date = datetime.fromisoformat(changelog['last_modified'])
                impl_time = (changelog_date - readme_date).days
                implementation_times.append(impl_time)
        
        avg_implementation_days = sum(implementation_times) / len(implementation_times) if implementation_times else 0
        
        return {
            "total_work_items": total_work_items,
            "completed_items": completed_items,
            "completion_rate_percent": round(completion_rate, 1),
            "pending_items": total_work_items - completed_items,
            "avg_implementation_days": round(avg_implementation_days, 1),
            "velocity_items_per_week": round(len(implementation_times) / 4, 1) if implementation_times else 0  # Assuming 4 weeks of data
        }
    
    def _analyze_roadmap(self) -> Dict[str, Any]:
        """Analizar roadmap desde README.md y identificar próximas tareas"""
        try:
            if not self.readme_path.exists():
                return {"error": "README.md not found"}
            
            content = self.readme_path.read_text(encoding='utf-8')
            
            # Extract roadmap sections
            roadmap_match = re.search(r"## 🚀 \*\*Roadmap:.*?\*\*.*?(.*?)(?=##|$)", content, re.DOTALL | re.IGNORECASE)
            
            if not roadmap_match:
                return {"error": "Roadmap section not found in README.md"}
            
            roadmap_text = roadmap_match.group(1)
            
            # Parse priorities
            priorities = {
                "alta": self._extract_priority_items(roadmap_text, r"⚡.*?Prioridad Alta.*?:(.*?)(?=###|$)"),
                "media": self._extract_priority_items(roadmap_text, r"🎯.*?Mediano Plazo.*?:(.*?)(?=###|$)"),
                "baja": self._extract_priority_items(roadmap_text, r"🚀.*?Largo Plazo.*?:(.*?)(?=###|$)")
            }
            
            # Extract specific items that should become changelogs
            next_changelog_candidates = []
            
            for priority, items in priorities.items():
                for item in items:
                    # Check if this item already has a changelog
                    area_name = self._generate_area_name(item)
                    has_changelog = any(area_name in cl['area'] for cl in self._scan_changelog_files())
                    
                    if not has_changelog:
                        next_changelog_candidates.append({
                            "item": item,
                            "priority": priority,
                            "suggested_area_name": area_name,
                            "suggested_branch": f"feature/{area_name}",
                            "estimated_complexity": self._estimate_complexity(item)
                        })
            
            return {
                "roadmap_sections": priorities,
                "next_changelog_candidates": sorted(
                    next_changelog_candidates, 
                    key=lambda x: (
                        {"alta": 3, "media": 2, "baja": 1}[x["priority"]], 
                        x["estimated_complexity"]
                    ), 
                    reverse=True
                )
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze roadmap: {e}"}
    
    def _generate_updated_roadmap(self):
        """Generar roadmap actualizado basado en el estado actual del tracker"""
        roadmap_path = self.project_root / "ROADMAP_DETERMINISTICO.md"
        planning_path = self.project_root / "ROADMAP_PLANNING.md"
        
        # Verificar si existe ROADMAP_PLANNING.md
        has_planning = planning_path.exists()
        
        # Analizar estado actual
        completed_areas = []
        in_progress_areas = []
        pending_areas = []
        
        for area_name, area_data in self.state["areas"].items():
            status = area_data.get("status", "not_started")
            progress = area_data.get("progress", 0)
            
            if status == "completed":
                completed_areas.append({
                    "name": area_name,
                    "progress": progress,
                    "completed": area_data.get("completed")
                })
            elif status == "in_progress":
                in_progress_areas.append({
                    "name": area_name,
                    "progress": progress,
                    "next_action": area_data.get("next_action", "")
                })
            else:
                pending_areas.append({
                    "name": area_name,
                    "progress": progress
                })
        
        # Generar contenido del roadmap
        content = f"""# 🎯 ROADMAP ACTUALIZADO - LocalClaude

**Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Base**: Estado actual del tracker (changelog_state.json)  
**Sistema**: Memoria persistente distribuida

---

## 📊 ESTADO ACTUAL

### **✅ COMPLETADO ({len(completed_areas)} tareas)**
"""
        
        for area in completed_areas:
            completed_date = area["completed"][:10] if area["completed"] else "Unknown"
            content += f"- **{area['name'].replace('-', ' ').title()}** ✅ ({completed_date})\n"
        
        if in_progress_areas:
            content += f"""
### **🔄 EN PROGRESO ({len(in_progress_areas)} tareas)**
"""
            for area in in_progress_areas:
                content += f"- **{area['name'].replace('-', ' ').title()}**: {area['progress']}% - {area['next_action']}\n"
        
        if pending_areas:
            content += f"""
### **📋 PENDIENTES ({len(pending_areas)} tareas)**
"""
            for area in pending_areas:
                content += f"- **{area['name'].replace('-', ' ').title()}**: Planificado\n"
        
        # Estadísticas
        total_areas = len(completed_areas) + len(in_progress_areas) + len(pending_areas)
        completion_rate = (len(completed_areas) / max(1, total_areas)) * 100
        
        content += f"""
---

## 📊 MÉTRICAS DE PROYECTO

### **Estado de Completación:**
- **Total work items**: {total_areas}
- **Completados**: {len(completed_areas)} ({completion_rate:.0f}%)
- **En progreso**: {len(in_progress_areas)}
- **Pendientes**: {len(pending_areas)}

### **Próximas Acciones Sugeridas:**
"""
        
        # Sugerir próximas acciones
        if not in_progress_areas and pending_areas:
            content += f"1. **Iniciar**: {pending_areas[0]['name'].replace('-', ' ').title()}\n"
        elif in_progress_areas:
            for area in in_progress_areas:
                content += f"1. **Continuar**: {area['name'].replace('-', ' ').title()} ({area['progress']}%)\n"
        
        if completion_rate >= 75:
            content += "\n🎉 **¡Excelente progreso!** Considera definir nuevas funcionalidades.\n"
        
        content += f"""
---

## 🔧 HERRAMIENTAS DE TRACKING

### **Comandos de Monitoreo:**
```bash
# Ver estado actual
python3 changelog/changelog_tracker.py --context

# Establecer enfoque en área
python3 changelog/changelog_tracker.py --focus [area]

# Actualizar progreso
python3 changelog/changelog_tracker.py --progress [area] [%] --next "acción"

# Marcar como completado
python3 changelog/changelog_tracker.py --complete [area]
```

---

**ROADMAP ACTUALIZADO v2.0**  
**Sistema de tracking**: changelog_state.json + Auto-tracker  
**Próxima revisión**: Automática con cada cambio de estado  
**Mantenido por**: ChangelogTracker System
"""
        
        # Escribir archivo
        with open(roadmap_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Roadmap actualizado: {roadmap_path}")
        if has_planning:
            print(f"📋 Planificación persistente: {planning_path} (NO modificado)")
        print(f"📊 Estado: {len(completed_areas)} completadas, {len(in_progress_areas)} en progreso, {len(pending_areas)} pendientes")
        print(f"🎯 Completación: {completion_rate:.0f}%")
    
    def _extract_priority_items(self, text: str, pattern: str) -> List[str]:
        """Extract items from priority section"""
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if not match:
            return []
        
        section = match.group(1)
        items = re.findall(r"[-*]\s*\*\*(.+?)\*\*(?:\s*-\s*(.+?))?(?=\n|$)", section)
        
        result = []
        for item in items:
            title = item[0].strip()
            description = item[1].strip() if item[1] else ""
            full_item = f"{title} - {description}" if description else title
            result.append(full_item)
        
        return result
    
    def _generate_area_name(self, item: str) -> str:
        """Generate consistent area name from roadmap item"""
        # Extract key terms and normalize
        key_terms = re.findall(r"\b\w+\b", item.lower())
        meaningful_terms = [term for term in key_terms if len(term) > 3 and term not in ['para', 'con', 'los', 'las', 'del', 'una', 'the', 'and', 'for', 'with']]
        
        if len(meaningful_terms) >= 2:
            return f"{meaningful_terms[0]}-{meaningful_terms[1]}"
        elif meaningful_terms:
            return meaningful_terms[0]
        else:
            return "feature-" + hashlib.md5(item.encode()).hexdigest()[:8]
    
    def _estimate_complexity(self, item: str) -> int:
        """Estimate complexity of roadmap item (1-10)"""
        complexity_indicators = {
            'optimiz': 3, 'optim': 3,
            'switch': 2, 'switching': 2,
            'test': 2, 'testing': 2,
            'integr': 4, 'integration': 4,
            'memoria': 4, 'memory': 4,
            'analisis': 3, 'analysis': 3,
            'dashboard': 4,
            'distributed': 8,
            'autonomous': 9,
            'self-improving': 10,
            'multi-agent': 7,
            'rag': 5,
            'embeddings': 5
        }
        
        item_lower = item.lower()
        complexity = 1
        
        for indicator, score in complexity_indicators.items():
            if indicator in item_lower:
                complexity = max(complexity, score)
        
        return complexity
    
    def _analyze_branch_changelog_relationship(self, branches: List[Dict]) -> List[Dict[str, Any]]:
        """Analizar relación entre branches y changelogs"""
        changelog_branches = []
        readmes = self._scan_readme_files()
        changelogs = self._scan_changelog_files()
        
        # Check each branch for changelog relationship
        for branch in branches:
            if branch.get('remote'):
                continue
                
            branch_name = branch['name']
            
            # Find related changelogs
            related_readmes = [r for r in readmes if r.get('branch') == branch_name]
            related_changelogs = [c for c in changelogs if any(r['area'] == c['area'] for r in related_readmes)]
            
            if related_readmes or 'feature/' in branch_name or 'fix/' in branch_name:
                changelog_branches.append({
                    "branch": branch_name,
                    "is_current": branch.get('current', False),
                    "related_readmes": len(related_readmes),
                    "related_changelogs": len(related_changelogs),
                    "has_documentation": len(related_readmes) > 0,
                    "is_completed": len(related_changelogs) > 0,
                    "needs_changelog": len(related_readmes) > 0 and len(related_changelogs) == 0
                })
        
        return changelog_branches
    
    def _identify_orphaned_branches(self, branches: List[Dict]) -> List[str]:
        """Identificar branches sin documentación de changelog"""
        orphaned = []
        readmes = self._scan_readme_files()
        documented_branches = {r.get('branch') for r in readmes if r.get('branch')}
        
        for branch in branches:
            if branch.get('remote'):
                continue
                
            branch_name = branch['name']
            if ('feature/' in branch_name or 'fix/' in branch_name) and branch_name not in documented_branches:
                orphaned.append(branch_name)
        
        return orphaned
    
    def _generate_priority_alerts(self) -> List[Dict[str, Any]]:
        """Generar alertas de prioridad basadas en el análisis"""
        alerts = []
        pending_work = self._identify_pending_work()
        
        # Critical alerts
        critical_pending = [w for w in pending_work if w['priority'] in ['crítica', 'critica', 'critical']]
        if critical_pending:
            alerts.append({
                "type": "critical",
                "message": f"{len(critical_pending)} tareas críticas pendientes",
                "items": [w['area'] for w in critical_pending],
                "action": "Requires immediate attention"
            })
        
        # Stale work alerts
        stale_work = [w for w in pending_work if w['age_days'] > 7]
        if stale_work:
            alerts.append({
                "type": "warning",
                "message": f"{len(stale_work)} tareas con más de 7 días sin progreso",
                "items": [f"{w['area']} ({w['age_days']} días)" for w in stale_work],
                "action": "Review status and prioritize"
            })
        
        # Orphaned branches
        branches_status = self._scan_branches_status()
        orphaned = branches_status.get('orphaned_branches', [])
        if orphaned:
            alerts.append({
                "type": "info",
                "message": f"{len(orphaned)} branches sin documentación de changelog",
                "items": orphaned,
                "action": "Create changelog READMEs or cleanup branches"
            })
        
        return alerts
    
    def generate_next_changelog_readme(self, area: str, priority: str = "high", description: str = "") -> str:
        """
        Generar template para próximo changelog README
        
        Args:
            area: Nombre del área/feature
            priority: Prioridad (critical/high/medium/low)
            description: Descripción del trabajo
            
        Returns:
            Contenido del README template
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_readme_{area}"
        
        branch_name = f"feature/{area}"
        
        template = f"""# 📖 README - {area.replace('-', ' ').title()}

**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Branch**: `{branch_name}`  
**Área**: {area}  
**Estado**: planificado  
**Prioridad**: {priority}

## 🎯 Problema

{description or 'Descripción del problema a resolver...'}

## 🎯 Objetivos

- [ ] Objetivo específico 1
- [ ] Objetivo específico 2  
- [ ] Objetivo específico 3

## ✅ Criterios de Éxito

- [ ] Métrica verificable 1
- [ ] Métrica verificable 2
- [ ] Tests implementados y pasando
- [ ] Documentación actualizada

## 🔧 Implementación Planificada

### **Archivos a Modificar:**
- `archivo1.py` - Descripción de cambios
- `archivo2.py` - Descripción de cambios

### **Tests a Implementar:**
- `test_feature.py` - Tests unitarios
- `test_integration.py` - Tests de integración

### **Performance Esperada:**
- Métrica objetivo 1: X% mejora
- Métrica objetivo 2: Xms tiempo de respuesta

## 📋 Próximos Pasos

1. [ ] Crear branch `{branch_name}`
2. [ ] Implementar funcionalidad core
3. [ ] Añadir tests
4. [ ] Actualizar documentación
5. [ ] Crear changelog de completación

---

**Creado por**: Auto-tracker de Changelogs  
**Template generado**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Archivo**: `changelog/{filename}`
"""
        
        return template
    
    def save_tracking_report(self, output_path: Optional[str] = None) -> str:
        """
        Guardar reporte completo de tracking
        
        Args:
            output_path: Ruta donde guardar el reporte (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        status = self.scan_changelog_status()
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.changelog_dir / f"tracking_report_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        
        return str(output_path)


def main():
    """CLI interface for changelog tracker con estado persistente"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LocalClaude Changelog Auto-Tracker")
    
    # Estado persistente - comandos principales para Claude
    parser.add_argument('--context', action='store_true', help='Ver contexto actual (para Claude)')
    parser.add_argument('--focus', help='Establecer área de enfoque actual')
    parser.add_argument('--progress', nargs=2, metavar=('AREA', 'PERCENT'), 
                       help='Actualizar progreso: --progress testing-fixes 60')
    parser.add_argument('--next', help='Definir próxima acción (usar con --progress)')
    parser.add_argument('--complete', help='Marcar área como completada')
    parser.add_argument('--sync', action='store_true', help='Auto-generar project_map.json desde código')
    
    # Análisis y reportes
    parser.add_argument('--scan', action='store_true', help='Escanear estado completo')
    parser.add_argument('--report', action='store_true', help='Generar reporte detallado')
    parser.add_argument('--roadmap', action='store_true', help='Generar roadmap determinístico')
    
    # Creación de changelogs
    parser.add_argument('--create', help='Crear nuevo changelog README para área')
    parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'], 
                       default='high', help='Prioridad del changelog')
    parser.add_argument('--description', help='Descripción del trabajo')
    
    args = parser.parse_args()
    
    tracker = ChangelogTracker()
    
    # Comandos de estado persistente
    if args.context:
        context = tracker.get_current_context()
        if "message" in context:
            print(context["message"])
        else:
            print(f"🎯 Enfoque actual: {context['current_focus']}")
            print(f"📊 Estado: {context['status']} ({context['progress']}%)")
            if context.get('next_action'):
                print(f"➡️  Próxima acción: {context['next_action']}")
                
    elif args.focus:
        tracker.set_focus(args.focus)
        
    elif args.progress:
        area, percent = args.progress
        tracker.update_progress(area, int(percent), args.next)
        
    elif args.complete:
        tracker.mark_completed(args.complete)
        
    elif args.sync:
        tracker.sync_architecture_map()
        
    # Comandos existentes
    elif args.scan:
        status = tracker.scan_changelog_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
    elif args.report:
        report_path = tracker.save_tracking_report()
        print(f"Tracking report saved to: {report_path}")
        
    elif args.create:
        content = tracker.generate_next_changelog_readme(
            args.create, args.priority, args.description or ""
        )
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_readme_{args.create}"
        file_path = tracker.changelog_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Changelog README creado: {file_path}")
        
    elif args.roadmap:
        print("🔄 Generando roadmap actualizado desde estado del tracker...")
        tracker._generate_updated_roadmap()
        
    else:
        print("📋 Comandos principales para Claude:")
        print("  --context                 Ver enfoque y progreso actual")
        print("  --focus [area]            Establecer enfoque")
        print("  --progress [area] [%]     Actualizar progreso")
        print("  --complete [area]         Marcar como completado")
        print("  --sync                    Auto-generar project_map.json")
        print("\n📊 Análisis y gestión:")
        print("  --scan                    Estado completo")
        print("  --roadmap                 Generar roadmap")
        print("  --create [area]           Crear changelog README")


if __name__ == "__main__":
    main()