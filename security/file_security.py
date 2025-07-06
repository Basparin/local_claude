#!/usr/bin/env python3
"""
File Security Manager for LocalClaude
Provides security controls for file creation and editing operations
"""

import os
import re
from pathlib import Path
from typing import Dict, Set, List, Optional, Tuple
from datetime import datetime


class FileSecurityManager:
    """Manages security policies for file operations"""
    
    # Allowed file extensions for creation
    ALLOWED_EXTENSIONS = {
        '.py', '.js', '.html', '.css', '.md', '.txt', '.json', '.yaml', '.yml',
        '.xml', '.csv', '.sql', '.sh', '.bat', '.ps1', '.dockerfile', '.env',
        '.gitignore', '.cfg', '.ini', '.conf', '.toml', '.lock', '.log'
    }
    
    # Forbidden paths (case-insensitive)
    FORBIDDEN_PATHS = {
        # System directories
        '/etc', '/usr', '/bin', '/sbin', '/boot', '/sys', '/proc', '/dev',
        '/var', '/opt', '/root', '/lib', '/lib32', '/lib64',
        # Windows system directories
        'c:/windows', 'c:/program files', 'c:/program files (x86)',
        'c:/system32', 'c:/users/all users', 'c:/users/default',
        # Common sensitive directories
        '/home/.ssh', '/home/.aws', '/home/.kube', '/.ssh', '/.aws', '/.kube'
    }
    
    # Dangerous file patterns
    DANGEROUS_PATTERNS = {
        # Executable extensions
        '.exe', '.com', '.scr', '.bat', '.cmd', '.pif', '.vbs', '.js',
        '.jar', '.app', '.deb', '.rpm', '.msi', '.dmg',
        # Script extensions that could be dangerous
        '.ps1', '.vbs', '.wsf', '.wsh'
    }
    
    # Maximum file size (in bytes) - 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Maximum files per session
    MAX_FILES_PER_SESSION = 50
    
    def __init__(self, workspace_dir: str, data_dir: str):
        """
        Initialize security manager
        
        Args:
            workspace_dir: Base workspace directory
            data_dir: Data directory for logging
        """
        self.workspace_dir = Path(workspace_dir).resolve()
        self.data_dir = Path(data_dir).resolve()
        self.session_files_created = []
        self.session_start = datetime.now()
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Load or create security log
        self.security_log_path = self.data_dir / "security.log"
        self._log_security_event("session_start", f"Security manager initialized for {workspace_dir}")
    
    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate if a file path is safe for creation/editing
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Convert to Path object and resolve
            path = Path(file_path)
            
            # Check if path is absolute and starts outside workspace
            if path.is_absolute():
                resolved_path = path.resolve()
            else:
                resolved_path = (self.workspace_dir / path).resolve()
            
            # Ensure path is within workspace directory
            try:
                resolved_path.relative_to(self.workspace_dir)
            except ValueError:
                self._log_security_event("path_traversal_attempt", f"Attempted access outside workspace: {file_path}")
                return False, f"❌ Acceso denegado: La ruta '{file_path}' está fuera del workspace permitido"
            
            # Check forbidden paths
            resolved_str = str(resolved_path).lower()
            for forbidden in self.FORBIDDEN_PATHS:
                if resolved_str.startswith(forbidden.lower()):
                    self._log_security_event("forbidden_path_access", f"Attempted access to forbidden path: {file_path}")
                    return False, f"❌ Acceso denegado: Ruta del sistema protegida '{file_path}'"
            
            # Check file extension
            extension = path.suffix.lower()
            if extension and extension not in self.ALLOWED_EXTENSIONS:
                # Special handling for dangerous extensions
                if extension in self.DANGEROUS_PATTERNS:
                    self._log_security_event("dangerous_extension", f"Attempted creation of dangerous file: {file_path}")
                    return False, f"❌ Extensión peligrosa: '{extension}' no está permitida por seguridad"
                else:
                    self._log_security_event("unknown_extension", f"Attempted creation of unknown extension: {file_path}")
                    return False, f"⚠️ Extensión '{extension}' no reconocida. Extensiones permitidas: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            
            # Check filename for dangerous patterns
            filename = path.name.lower()
            dangerous_names = ['passwd', 'shadow', 'hosts', 'sudoers', 'authorized_keys', 'known_hosts']
            if any(dangerous in filename for dangerous in dangerous_names):
                self._log_security_event("dangerous_filename", f"Attempted creation of sensitive file: {file_path}")
                return False, f"❌ Nombre de archivo sensible: '{path.name}' no está permitido"
            
            # Check session limits
            if len(self.session_files_created) >= self.MAX_FILES_PER_SESSION:
                self._log_security_event("session_limit_exceeded", f"Session file limit exceeded: {len(self.session_files_created)}")
                return False, f"❌ Límite de archivos por sesión alcanzado ({self.MAX_FILES_PER_SESSION}). Reinicia la sesión."
            
            return True, ""
            
        except Exception as e:
            self._log_security_event("validation_error", f"Error validating path {file_path}: {e}")
            return False, f"❌ Error validando ruta: {e}"
    
    def validate_file_content(self, content: str, file_path: str) -> Tuple[bool, str]:
        """
        Validate file content for security issues
        
        Args:
            content: File content to validate
            file_path: Path of the file (for context)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size
            content_size = len(content.encode('utf-8'))
            if content_size > self.MAX_FILE_SIZE:
                self._log_security_event("oversized_file", f"Attempted creation of oversized file: {file_path} ({content_size} bytes)")
                return False, f"❌ Archivo demasiado grande: {self._format_size(content_size)} > {self._format_size(self.MAX_FILE_SIZE)}"
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'rm\s+-rf\s+/',
                r'sudo\s+rm',
                r'format\s+c:',
                r'del\s+/[qsf]',
                r'exec\s*\(',
                r'eval\s*\(',
                r'__import__\s*\(',
                r'subprocess\s*\.',
                r'os\.system',
                r'os\.popen',
                r'shell=True',
            ]
            
            content_lower = content.lower()
            for pattern in suspicious_patterns:
                if re.search(pattern, content_lower):
                    self._log_security_event("suspicious_content", f"Suspicious pattern '{pattern}' found in {file_path}")
                    return False, f"⚠️ Contenido sospechoso detectado: patrón '{pattern}' no permitido"
            
            # Check for secrets/keys (basic patterns)
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'-----BEGIN\s+PRIVATE\s+KEY-----',
                r'sk-[a-zA-Z0-9]{48}',  # OpenAI API key pattern
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self._log_security_event("potential_secret", f"Potential secret detected in {file_path}")
                    return False, f"🔐 Posible secreto detectado: no incluyas claves o passwords en el código"
            
            return True, ""
            
        except Exception as e:
            self._log_security_event("content_validation_error", f"Error validating content for {file_path}: {e}")
            return False, f"❌ Error validando contenido: {e}"
    
    def register_file_creation(self, file_path: str, file_size: int) -> None:
        """
        Register a file creation for tracking
        
        Args:
            file_path: Path of created file
            file_size: Size of created file
        """
        creation_info = {
            'path': file_path,
            'size': file_size,
            'timestamp': datetime.now().isoformat(),
            'session_start': self.session_start.isoformat()
        }
        
        self.session_files_created.append(creation_info)
        self._log_security_event("file_created", f"File created: {file_path} ({self._format_size(file_size)})")
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of current session
        
        Returns:
            Dictionary with session statistics
        """
        total_size = sum(file_info['size'] for file_info in self.session_files_created)
        
        return {
            'session_start': self.session_start.isoformat(),
            'files_created': len(self.session_files_created),
            'total_size': total_size,
            'total_size_formatted': self._format_size(total_size),
            'files_remaining': max(0, self.MAX_FILES_PER_SESSION - len(self.session_files_created)),
            'created_files': [f['path'] for f in self.session_files_created]
        }
    
    def cleanup_session(self) -> None:
        """Reset session tracking"""
        self.session_files_created = []
        self.session_start = datetime.now()
        self._log_security_event("session_reset", "Session tracking reset")
    
    def _log_security_event(self, event_type: str, message: str) -> None:
        """
        Log a security event
        
        Args:
            event_type: Type of security event
            message: Event message
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {event_type.upper()}: {message}\n"
            
            with open(self.security_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            # Fail silently for logging errors
            pass
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def get_allowed_extensions(self) -> Set[str]:
        """Get set of allowed file extensions"""
        return self.ALLOWED_EXTENSIONS.copy()
    
    def add_allowed_extension(self, extension: str) -> None:
        """
        Add a new allowed extension (for customization)
        
        Args:
            extension: File extension to allow (with dot)
        """
        if extension.startswith('.'):
            self.ALLOWED_EXTENSIONS.add(extension.lower())
            self._log_security_event("extension_added", f"Added allowed extension: {extension}")
    
    def remove_allowed_extension(self, extension: str) -> None:
        """
        Remove an allowed extension (for customization)
        
        Args:
            extension: File extension to remove (with dot)
        """
        if extension.startswith('.') and extension.lower() in self.ALLOWED_EXTENSIONS:
            self.ALLOWED_EXTENSIONS.remove(extension.lower())
            self._log_security_event("extension_removed", f"Removed allowed extension: {extension}")