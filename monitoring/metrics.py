"""
Core del sistema de métricas - Logging silencioso
"""

import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

class MetricsCollector:
    """Recolector silencioso de métricas del sistema"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Base de datos para métricas históricas
        self.db_path = self.data_dir / "metrics.db"
        self.current_metrics_path = self.data_dir / "metrics_current.json"
        
        # Estado en memoria para session actual
        self.session_start = datetime.now()
        self.session_metrics = {
            'commands_executed': 0,
            'models_used': {},
            'errors_count': 0,
            'total_response_time': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Thread-safe logging
        self._lock = threading.Lock()
        
        # Configurar logging
        self._setup_logging()
        
        # Inicializar DB
        self._init_database()
    
    def _setup_logging(self):
        """Configurar logging silencioso"""
        log_file = self.data_dir / "monitoring.log"
        
        # Logger específico para métricas
        self.logger = logging.getLogger('localclaude.metrics')
        self.logger.setLevel(logging.INFO)
        
        # Handler para archivo
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # Formato simple
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        
        # No propagar al root logger (silencioso)
        self.logger.propagate = False
    
    def _init_database(self):
        """Inicializar base de datos SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    commands_total INTEGER DEFAULT 0,
                    errors_total INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0
                )
            ''')
    
    def log_command(self, command: str, execution_time: float, success: bool = True):
        """Registrar ejecución de comando"""
        with self._lock:
            self.session_metrics['commands_executed'] += 1
            self.session_metrics['total_response_time'] += execution_time
            
            if not success:
                self.session_metrics['errors_count'] += 1
            
            # Log silencioso
            self.logger.info(f"CMD:{command}|TIME:{execution_time:.3f}|SUCCESS:{success}")
            
            # Persistir en DB
            self._store_metric('performance', 'command_execution', execution_time, {
                'command': command,
                'success': success
            })
    
    def log_model_usage(self, model_name: str, task_type: str, response_time: float):
        """Registrar uso de modelo"""
        with self._lock:
            if model_name not in self.session_metrics['models_used']:
                self.session_metrics['models_used'][model_name] = 0
            self.session_metrics['models_used'][model_name] += 1
            
            self.logger.info(f"MODEL:{model_name}|TASK:{task_type}|TIME:{response_time:.3f}")
            
            self._store_metric('usage', 'model_usage', response_time, {
                'model': model_name,
                'task_type': task_type
            })
    
    def log_cache_hit(self, cache_type: str, hit: bool):
        """Registrar cache hit/miss"""
        with self._lock:
            if hit:
                self.session_metrics['cache_hits'] += 1
            else:
                self.session_metrics['cache_misses'] += 1
            
            self.logger.info(f"CACHE:{cache_type}|HIT:{hit}")
            
            self._store_metric('performance', 'cache_hit', 1 if hit else 0, {
                'cache_type': cache_type
            })
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None):
        """Registrar error"""
        with self._lock:
            self.session_metrics['errors_count'] += 1
            
            self.logger.error(f"ERROR:{error_type}|MSG:{error_message}")
            
            self._store_metric('errors', error_type, 1, {
                'message': error_message,
                'context': context or {}
            })
    
    def _store_metric(self, metric_type: str, metric_name: str, value: float, metadata: Dict = None):
        """Almacenar métrica en DB"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO metrics (metric_type, metric_name, value, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (metric_type, metric_name, value, json.dumps(metadata or {})))
        except Exception as e:
            # Fallo silencioso en logging
            pass
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Obtener resumen de sesión actual"""
        with self._lock:
            avg_time = (self.session_metrics['total_response_time'] / 
                       max(1, self.session_metrics['commands_executed']))
            
            cache_total = self.session_metrics['cache_hits'] + self.session_metrics['cache_misses']
            hit_rate = (self.session_metrics['cache_hits'] / max(1, cache_total)) * 100
            
            return {
                'session_duration': (datetime.now() - self.session_start).total_seconds(),
                'commands_executed': self.session_metrics['commands_executed'],
                'avg_response_time': avg_time,
                'models_used': self.session_metrics['models_used'],
                'errors_count': self.session_metrics['errors_count'],
                'cache_hit_rate': hit_rate
            }
    
    def save_current_state(self):
        """Guardar estado actual en JSON"""
        try:
            with open(self.current_metrics_path, 'w') as f:
                json.dump(self.get_session_summary(), f, indent=2, default=str)
        except Exception:
            pass


# Instancia global - singleton
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Obtener instancia global del collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector