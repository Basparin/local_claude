"""
Sistema de memoria persistente para LocalClaude
"""

import sqlite3
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class MemoryStore:
    """Almacén de memoria persistente usando SQLite"""
    
    def __init__(self, settings):
        self.settings = settings
        self.db_path = settings.files['memory_db']
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar base de datos
        self._init_database()
    
    def _init_database(self):
        """Inicializar esquema de base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                -- Tabla de sesiones
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    workspace_path TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    total_messages INTEGER DEFAULT 0,
                    summary TEXT,
                    metadata TEXT, -- JSON
                    created_at REAL DEFAULT (julianday('now'))
                );
                
                -- Tabla de conversaciones
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    tokens_used INTEGER DEFAULT 0,
                    model_used TEXT,
                    metadata TEXT, -- JSON
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                );
                
                -- Tabla de proyectos
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT UNIQUE NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT,
                    last_accessed REAL NOT NULL,
                    files_count INTEGER DEFAULT 0,
                    languages TEXT, -- JSON array
                    description TEXT,
                    metadata TEXT, -- JSON
                    created_at REAL DEFAULT (julianday('now'))
                );
                
                -- Tabla de archivos trabajados
                CREATE TABLE IF NOT EXISTS files_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_path TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    action TEXT NOT NULL, -- 'read', 'create', 'edit', 'analyze'
                    timestamp REAL NOT NULL,
                    session_id TEXT,
                    details TEXT, -- JSON
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                );
                
                -- Tabla de configuraciones de usuario
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    type TEXT NOT NULL, -- 'string', 'number', 'boolean', 'json'
                    updated_at REAL DEFAULT (julianday('now'))
                );
                
                -- Tabla de comandos frecuentes
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 1,
                    last_used REAL NOT NULL,
                    session_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                );
                
                -- Índices para optimizar consultas
                CREATE INDEX IF NOT EXISTS idx_sessions_workspace ON sessions(workspace_path);
                CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_projects_accessed ON projects(last_accessed);
                CREATE INDEX IF NOT EXISTS idx_files_project ON files_history(project_path);
                CREATE INDEX IF NOT EXISTS idx_files_timestamp ON files_history(timestamp);
                CREATE INDEX IF NOT EXISTS idx_commands_usage ON command_usage(command, usage_count);
            ''')
    
    def create_session(self, workspace_path: str) -> str:
        """
        Crear nueva sesión
        
        Args:
            workspace_path: Ruta del workspace actual
            
        Returns:
            ID de la sesión creada
        """
        session_id = self._generate_session_id(workspace_path)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO sessions (session_id, workspace_path, start_time)
                VALUES (?, ?, ?)
            ''', (session_id, workspace_path, time.time()))
        
        return session_id
    
    def end_session(self, session_id: str, summary: str = None, metadata: Dict[str, Any] = None):
        """Finalizar sesión actual"""
        with sqlite3.connect(self.db_path) as conn:
            # Contar mensajes de la sesión
            cursor = conn.execute('''
                SELECT COUNT(*) FROM conversations WHERE session_id = ?
            ''', (session_id,))
            
            message_count = cursor.fetchone()[0]
            
            # Actualizar sesión
            conn.execute('''
                UPDATE sessions 
                SET end_time = ?, total_messages = ?, summary = ?, metadata = ?
                WHERE session_id = ?
            ''', (
                time.time(),
                message_count,
                summary,
                json.dumps(metadata) if metadata else None,
                session_id
            ))
    
    def save_message(self, session_id: str, role: str, content: str, 
                     model_used: str = None, tokens_used: int = 0, 
                     metadata: Dict[str, Any] = None):
        """Guardar mensaje de conversación"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO conversations 
                (session_id, role, content, timestamp, tokens_used, model_used, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                role,
                content,
                time.time(),
                tokens_used,
                model_used,
                json.dumps(metadata) if metadata else None
            ))
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Obtener historial de una sesión"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT role, content, timestamp, model_used, tokens_used, metadata
                FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp ASC
            ''', (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                message = {
                    'role': row['role'],
                    'content': row['content'],
                    'timestamp': row['timestamp'],
                    'model_used': row['model_used'],
                    'tokens_used': row['tokens_used']
                }
                
                if row['metadata']:
                    message['metadata'] = json.loads(row['metadata'])
                
                messages.append(message)
            
            return messages
    
    def get_recent_sessions(self, workspace_path: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener sesiones recientes"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if workspace_path:
                cursor = conn.execute('''
                    SELECT session_id, workspace_path, start_time, end_time, 
                           total_messages, summary
                    FROM sessions 
                    WHERE workspace_path = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                ''', (workspace_path, limit))
            else:
                cursor = conn.execute('''
                    SELECT session_id, workspace_path, start_time, end_time, 
                           total_messages, summary
                    FROM sessions 
                    ORDER BY start_time DESC
                    LIMIT ?
                ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                session = {
                    'session_id': row['session_id'],
                    'workspace_path': row['workspace_path'],
                    'start_time': row['start_time'],
                    'end_time': row['end_time'],
                    'total_messages': row['total_messages'],
                    'summary': row['summary']
                }
                sessions.append(session)
            
            return sessions
    
    def register_project(self, project_path: str, project_name: str, 
                        project_type: str = None, languages: List[str] = None,
                        description: str = None, metadata: Dict[str, Any] = None):
        """Registrar proyecto en la memoria"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO projects 
                (project_path, project_name, project_type, last_accessed, 
                 languages, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_path,
                project_name,
                project_type,
                time.time(),
                json.dumps(languages) if languages else None,
                description,
                json.dumps(metadata) if metadata else None
            ))
    
    def update_project_access(self, project_path: str, files_count: int = None):
        """Actualizar último acceso a proyecto"""
        with sqlite3.connect(self.db_path) as conn:
            if files_count is not None:
                conn.execute('''
                    UPDATE projects 
                    SET last_accessed = ?, files_count = ?
                    WHERE project_path = ?
                ''', (time.time(), files_count, project_path))
            else:
                conn.execute('''
                    UPDATE projects 
                    SET last_accessed = ?
                    WHERE project_path = ?
                ''', (time.time(), project_path))
    
    def get_recent_projects(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener proyectos recientes"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT project_path, project_name, project_type, last_accessed,
                       files_count, languages, description
                FROM projects 
                ORDER BY last_accessed DESC
                LIMIT ?
            ''', (limit,))
            
            projects = []
            for row in cursor.fetchall():
                project = {
                    'project_path': row['project_path'],
                    'project_name': row['project_name'],
                    'project_type': row['project_type'],
                    'last_accessed': row['last_accessed'],
                    'files_count': row['files_count'],
                    'description': row['description']
                }
                
                if row['languages']:
                    project['languages'] = json.loads(row['languages'])
                
                projects.append(project)
            
            return projects
    
    def log_file_action(self, project_path: str, file_path: str, action: str,
                       session_id: str = None, details: Dict[str, Any] = None):
        """Registrar acción en archivo"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO files_history 
                (project_path, file_path, action, timestamp, session_id, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                project_path,
                file_path,
                action,
                time.time(),
                session_id,
                json.dumps(details) if details else None
            ))
    
    def get_file_history(self, file_path: str = None, project_path: str = None,
                        limit: int = 20) -> List[Dict[str, Any]]:
        """Obtener historial de archivos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if file_path:
                cursor = conn.execute('''
                    SELECT project_path, file_path, action, timestamp, session_id, details
                    FROM files_history 
                    WHERE file_path = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (file_path, limit))
            elif project_path:
                cursor = conn.execute('''
                    SELECT project_path, file_path, action, timestamp, session_id, details
                    FROM files_history 
                    WHERE project_path = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (project_path, limit))
            else:
                cursor = conn.execute('''
                    SELECT project_path, file_path, action, timestamp, session_id, details
                    FROM files_history 
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                entry = {
                    'project_path': row['project_path'],
                    'file_path': row['file_path'],
                    'action': row['action'],
                    'timestamp': row['timestamp'],
                    'session_id': row['session_id']
                }
                
                if row['details']:
                    entry['details'] = json.loads(row['details'])
                
                history.append(entry)
            
            return history
    
    def record_command_usage(self, command: str, session_id: str = None):
        """Registrar uso de comando"""
        with sqlite3.connect(self.db_path) as conn:
            # Verificar si el comando ya existe
            cursor = conn.execute('''
                SELECT usage_count FROM command_usage WHERE command = ?
            ''', (command,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Incrementar contador
                conn.execute('''
                    UPDATE command_usage 
                    SET usage_count = usage_count + 1, last_used = ?, session_id = ?
                    WHERE command = ?
                ''', (time.time(), session_id, command))
            else:
                # Crear nuevo registro
                conn.execute('''
                    INSERT INTO command_usage (command, last_used, session_id)
                    VALUES (?, ?, ?)
                ''', (command, time.time(), session_id))
    
    def get_popular_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtener comandos más utilizados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT command, usage_count, last_used
                FROM command_usage 
                ORDER BY usage_count DESC, last_used DESC
                LIMIT ?
            ''', (limit,))
            
            commands = []
            for row in cursor.fetchall():
                commands.append({
                    'command': row['command'],
                    'usage_count': row['usage_count'],
                    'last_used': row['last_used']
                })
            
            return commands
    
    def set_preference(self, key: str, value: Any, value_type: str = None):
        """Guardar preferencia de usuario"""
        if value_type is None:
            if isinstance(value, bool):
                value_type = 'boolean'
                value = str(value).lower()
            elif isinstance(value, (int, float)):
                value_type = 'number'
                value = str(value)
            elif isinstance(value, (dict, list)):
                value_type = 'json'
                value = json.dumps(value)
            else:
                value_type = 'string'
                value = str(value)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO user_preferences (key, value, type, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (key, value, value_type, time.time()))
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Obtener preferencia de usuario"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT value, type FROM user_preferences WHERE key = ?
            ''', (key,))
            
            result = cursor.fetchone()
            
            if not result:
                return default
            
            value, value_type = result
            
            # Convertir según el tipo
            if value_type == 'boolean':
                return value.lower() == 'true'
            elif value_type == 'number':
                try:
                    return int(value) if '.' not in value else float(value)
                except ValueError:
                    return default
            elif value_type == 'json':
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return default
            else:
                return value
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Obtener todas las preferencias"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT key, value, type FROM user_preferences
            ''')
            
            preferences = {}
            for row in cursor.fetchall():
                key = row['key']
                value = row['value']
                value_type = row['type']
                
                # Convertir según el tipo
                if value_type == 'boolean':
                    preferences[key] = value.lower() == 'true'
                elif value_type == 'number':
                    try:
                        preferences[key] = int(value) if '.' not in value else float(value)
                    except ValueError:
                        preferences[key] = value
                elif value_type == 'json':
                    try:
                        preferences[key] = json.loads(value)
                    except json.JSONDecodeError:
                        preferences[key] = value
                else:
                    preferences[key] = value
            
            return preferences
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de memoria"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Contar sesiones
            cursor = conn.execute('SELECT COUNT(*) FROM sessions')
            stats['total_sessions'] = cursor.fetchone()[0]
            
            # Contar mensajes
            cursor = conn.execute('SELECT COUNT(*) FROM conversations')
            stats['total_messages'] = cursor.fetchone()[0]
            
            # Contar proyectos
            cursor = conn.execute('SELECT COUNT(*) FROM projects')
            stats['total_projects'] = cursor.fetchone()[0]
            
            # Contar archivos trabajados
            cursor = conn.execute('SELECT COUNT(DISTINCT file_path) FROM files_history')
            stats['unique_files'] = cursor.fetchone()[0]
            
            # Comando más usado
            cursor = conn.execute('''
                SELECT command, usage_count FROM command_usage 
                ORDER BY usage_count DESC LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                stats['most_used_command'] = {'command': result[0], 'count': result[1]}
            
            # Tamaño de base de datos
            stats['db_size'] = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return stats
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Limpiar datos antiguos"""
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            # Eliminar conversaciones antiguas
            conn.execute('''
                DELETE FROM conversations 
                WHERE timestamp < ?
            ''', (cutoff_time,))
            
            # Eliminar sesiones antiguas sin mensajes
            conn.execute('''
                DELETE FROM sessions 
                WHERE start_time < ? AND session_id NOT IN (
                    SELECT DISTINCT session_id FROM conversations
                )
            ''', (cutoff_time,))
            
            # Eliminar historial de archivos antiguo
            conn.execute('''
                DELETE FROM files_history 
                WHERE timestamp < ?
            ''', (cutoff_time,))
            
            # Vacuum para optimizar
            conn.execute('VACUUM')
    
    def _generate_session_id(self, workspace_path: str) -> str:
        """Generar ID único para sesión"""
        timestamp = str(time.time())
        content = f"{workspace_path}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def export_data(self, export_path: str, format: str = 'json'):
        """Exportar datos de memoria"""
        if format == 'json':
            self._export_json(export_path)
        else:
            raise ValueError(f"Formato no soportado: {format}")
    
    def _export_json(self, export_path: str):
        """Exportar datos en formato JSON"""
        data = {
            'sessions': [],
            'projects': self.get_recent_projects(limit=100),
            'preferences': self.get_all_preferences(),
            'stats': self.get_memory_stats(),
            'exported_at': time.time()
        }
        
        # Exportar sesiones recientes
        sessions = self.get_recent_sessions(limit=50)
        for session in sessions:
            session_data = session.copy()
            session_data['messages'] = self.get_session_history(session['session_id'])
            data['sessions'].append(session_data)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)