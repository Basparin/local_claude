#!/usr/bin/env python3
"""
Test runner script for LocalClaude
"""

import sys
import unittest
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Ejecutando tests unitarios...")
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test(test_name):
    """Run a specific test file or test case"""
    print(f"🎯 Ejecutando test específico: {test_name}")
    
    if test_name.endswith('.py'):
        test_name = test_name[:-3]  # Remove .py extension
    
    try:
        # Import and run specific test
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(f'tests.{test_name}')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    except Exception as e:
        print(f"❌ Error ejecutando test {test_name}: {e}")
        return False


def run_e2e_tests():
    """Run end-to-end tests"""
    print("🚀 Ejecutando tests end-to-end...")
    return run_specific_test('test_e2e')


def print_help():
    """Print help information"""
    print("""
📋 LocalClaude Test Runner

Uso:
    python run_tests.py [opción]

Opciones:
    (sin argumentos)  - Ejecutar todos los tests unitarios
    e2e              - Ejecutar tests end-to-end
    <test_name>      - Ejecutar test específico (ej: test_cli_engine)
    help             - Mostrar esta ayuda

Ejemplos:
    python run_tests.py                    # Todos los tests
    python run_tests.py e2e               # Solo tests E2E
    python run_tests.py test_cli_engine   # Test específico
    python run_tests.py help              # Esta ayuda
    """)


def main():
    """Main test runner function"""
    if len(sys.argv) == 1:
        # Run all unit tests
        success = run_unit_tests()
        sys.exit(0 if success else 1)
    
    arg = sys.argv[1].lower()
    
    if arg == 'help':
        print_help()
        sys.exit(0)
    elif arg == 'e2e':
        success = run_e2e_tests()
        sys.exit(0 if success else 1)
    else:
        # Run specific test
        success = run_specific_test(arg)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()