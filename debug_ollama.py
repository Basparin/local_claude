#!/usr/bin/env python3
"""
Script de debug para conexión Ollama
"""

import subprocess
import platform
import sys

def test_ollama_connection():
    """Probar diferentes formas de conectar a Ollama"""
    
    print(f"🖥️  Sistema: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Dir: {sys.path[0]}")
    print("=" * 50)
    
    # Test 1: Ollama directo
    print("🧪 Test 1: ollama directo")
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        print(f"   Return code: {result.returncode}")
        if result.returncode == 0:
            print(f"   ✅ Funciona! Modelos: {len(result.stdout.splitlines())-1}")
        else:
            print(f"   ❌ Error: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Test 2: WSL + ollama (si estamos en Windows)
    if platform.system() == 'Windows':
        print("\n🧪 Test 2: wsl ollama")
        try:
            result = subprocess.run(['wsl', 'ollama', 'list'], capture_output=True, text=True, timeout=10)
            print(f"   Return code: {result.returncode}")
            if result.returncode == 0:
                print(f"   ✅ WSL funciona! Modelos: {len(result.stdout.splitlines())-1}")
            else:
                print(f"   ❌ Error: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
    
    # Test 3: API HTTP
    print("\n🧪 Test 3: HTTP API localhost:11434")
    try:
        import urllib.request
        response = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=5)
        print(f"   ✅ HTTP API funciona! Status: {response.status}")
    except Exception as e:
        print(f"   ❌ HTTP API error: {e}")
    
    # Test 4: LocalClaude interface
    print("\n🧪 Test 4: LocalClaude OllamaInterface")
    try:
        sys.path.insert(0, '.')
        from config.settings import Settings
        from core.ollama_interface import OllamaInterface
        
        settings = Settings()
        ollama = OllamaInterface(settings)
        
        print(f"   Comando detectado: {ollama.ollama_cmd}")
        print(f"   ¿Es Windows?: {ollama.is_windows}")
        print(f"   Test connection: {ollama.test_connection()}")
        print(f"   Test model: {ollama.test_model('deepseek-r1:8b')}")
        
    except Exception as e:
        print(f"   ❌ LocalClaude error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ollama_connection()