#!/usr/bin/env python3
"""
UNIVERSAL TEST FRAMEWORK
Comprehensive testing infrastructure for all modular systems
"""

import sys
import os
import time
import traceback
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import unittest
from io import StringIO

# Add src to path for module imports
current_dir = Path(__file__).parent.parent.parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

class TestResult:
    """Enhanced test result with detailed logging"""
    
    def __init__(self, test_name: str, module: str):
        self.test_name = test_name
        self.module = module
        self.start_time = time.time()
        self.end_time = None
        self.duration = 0.0
        self.status = "RUNNING"
        self.message = ""
        self.details = []
        self.exception = None
        
    def complete(self, status: str, message: str = "", exception: Exception = None):
        """Complete the test with results"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        self.message = message
        self.exception = exception
        
    def add_detail(self, detail: str):
        """Add detail to test result"""
        self.details.append(detail)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            'test_name': self.test_name,
            'module': self.module,
            'duration': self.duration,
            'status': self.status,
            'message': self.message,
            'details': self.details,
            'exception': str(self.exception) if self.exception else None,
            'timestamp': datetime.now().isoformat()
        }

class TestLogger:
    """Advanced test logging with multiple outputs"""
    
    def __init__(self):
        self.results = []
        self.console_output = []
        self.app_log_output = []
        self.start_time = time.time()
        
    def log_test_start(self, test_name: str, module: str) -> TestResult:
        """Start a new test"""
        result = TestResult(test_name, module)
        self.results.append(result)
        
        msg = f"🧪 Starting {module}.{test_name}..."
        self.console_output.append(msg)
        self.app_log_output.append(f"[TEST] {msg}")
        print(msg)
        
        return result
        
    def log_test_complete(self, result: TestResult):
        """Complete a test with results"""
        status_icons = {
            "PASS": "✅",
            "FAIL": "❌", 
            "SKIP": "⏭️",
            "ERROR": "💥"
        }
        
        icon = status_icons.get(result.status, "❓")
        msg = f"{icon} {result.module}.{result.test_name}: {result.status} ({result.duration:.3f}s)"
        if result.message:
            msg += f" - {result.message}"
            
        self.console_output.append(msg)
        self.app_log_output.append(f"[TEST] {msg}")
        print(msg)
        
        # Log details
        for detail in result.details:
            detail_msg = f"    ℹ️ {detail}"
            self.console_output.append(detail_msg)
            self.app_log_output.append(f"[TEST] {detail_msg}")
            print(detail_msg)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary statistics"""
        total_time = time.time() - self.start_time
        
        status_counts = {}
        for result in self.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
            
        return {
            'total_tests': len(self.results),
            'total_time': total_time,
            'status_counts': status_counts,
            'pass_rate': status_counts.get('PASS', 0) / max(len(self.results), 1) * 100
        }
    
    def save_results(self, filepath: Path):
        """Save detailed results to JSON file"""
        test_data = {
            'summary': self.get_summary(),
            'results': [result.to_dict() for result in self.results],
            'console_output': self.console_output,
            'app_log_output': self.app_log_output,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)

class DependencyManager:
    """Manages and installs dependencies automatically"""
    
    REQUIRED_DEPENDENCIES = {
        'numpy': 'numpy',
        'trimesh': 'trimesh',
        'requests': 'requests',
        'PyQt6': 'PyQt6',
        'OpenGL': 'PyOpenGL PyOpenGL_accelerate'
    }
    
    @staticmethod
    def check_dependency(package_name: str) -> bool:
        """Check if a dependency is available"""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def install_dependency(package_name: str, install_command: str) -> bool:
        """Install a dependency using pip"""
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install'
            ] + install_command.split(), 
            capture_output=True, text=True, timeout=300)
            
            return result.returncode == 0
        except Exception as e:
            print(f"Failed to install {package_name}: {e}")
            return False
    
    @classmethod
    def ensure_all_dependencies(cls) -> Dict[str, bool]:
        """Ensure all dependencies are installed"""
        results = {}
        
        print("🔍 Checking and installing dependencies...")
        
        for package, install_cmd in cls.REQUIRED_DEPENDENCIES.items():
            print(f"📦 Checking {package}...")
            
            if cls.check_dependency(package):
                print(f"✅ {package} already available")
                results[package] = True
            else:
                print(f"📥 Installing {package}...")
                success = cls.install_dependency(package, install_cmd)
                results[package] = success
                
                if success:
                    print(f"✅ {package} installed successfully")
                else:
                    print(f"❌ Failed to install {package}")
        
        return results

class ModuleTestSuite:
    """Base class for module test suites"""
    
    def __init__(self, module_name: str, logger: TestLogger):
        self.module_name = module_name
        self.logger = logger
        self.module = None
        self.setup_complete = False
        
    def setup_module(self) -> bool:
        """Setup the module for testing"""
        result = self.logger.log_test_start("setup_module", self.module_name)
        
        try:
            # Attempt to import the module
            self.module = __import__(self.module_name)
            result.add_detail(f"Module {self.module_name} imported successfully")
            
            # Run module-specific setup
            if hasattr(self, '_setup_module_specific'):
                self._setup_module_specific()
                
            self.setup_complete = True
            result.complete("PASS", "Module setup completed")
            self.logger.log_test_complete(result)
            return True
            
        except Exception as e:
            result.complete("FAIL", f"Module setup failed: {str(e)}", e)
            self.logger.log_test_complete(result)
            return False
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all tests in the suite"""
        if not self.setup_complete:
            if not self.setup_module():
                return []
        
        test_methods = [method for method in dir(self) if method.startswith('test_')]
        results = []
        
        for test_method_name in test_methods:
            test_method = getattr(self, test_method_name)
            result = self.logger.log_test_start(test_method_name, self.module_name)
            
            try:
                test_method(result)
                if result.status == "RUNNING":  # Test didn't set status
                    result.complete("PASS", "Test completed successfully")
            except AssertionError as e:
                result.complete("FAIL", f"Assertion failed: {str(e)}", e)
            except Exception as e:
                result.complete("ERROR", f"Unexpected error: {str(e)}", e)
            
            self.logger.log_test_complete(result)
            results.append(result)
        
        return results

class UniversalTestRunner:
    """Main test runner for all modules"""
    
    def __init__(self):
        self.logger = TestLogger()
        self.test_suites = []
        self.dependency_results = {}
        
    def add_test_suite(self, suite: ModuleTestSuite):
        """Add a test suite to run"""
        self.test_suites.append(suite)
    
    def run_dependency_check(self) -> bool:
        """Run dependency check and installation"""
        print("🔧 UNIVERSAL DEPENDENCY MANAGEMENT")
        print("=" * 50)
        
        self.dependency_results = DependencyManager.ensure_all_dependencies()
        
        # Check if critical dependencies are available
        critical_deps = ['numpy', 'requests']  # Core dependencies
        critical_available = all(self.dependency_results.get(dep, False) for dep in critical_deps)
        
        print(f"\n📊 Dependency Status:")
        for dep, available in self.dependency_results.items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"   {dep}: {status}")
        
        return critical_available
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        print(f"\n🧪 RUNNING COMPREHENSIVE MODULE TESTS")
        print("=" * 50)
        
        all_results = []
        
        for suite in self.test_suites:
            print(f"\n🔍 Testing {suite.module_name} module...")
            suite_results = suite.run_all_tests()
            all_results.extend(suite_results)
        
        # Generate summary
        summary = self.logger.get_summary()
        
        print(f"\n📊 TEST SUMMARY")
        print("=" * 30)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Total Time: {summary['total_time']:.2f}s")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        
        for status, count in summary['status_counts'].items():
            print(f"{status}: {count}")
        
        return {
            'summary': summary,
            'results': all_results,
            'dependencies': self.dependency_results
        }
    
    def save_results(self, output_dir: Path):
        """Save test results to files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed JSON results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = output_dir / f"test_results_{timestamp}.json"
        self.logger.save_results(json_file)
        
        # Save console output
        console_file = output_dir / f"console_output_{timestamp}.txt"
        with open(console_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.logger.console_output))
        
        # Save app log format
        app_log_file = output_dir / f"app_log_{timestamp}.txt"
        with open(app_log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.logger.app_log_output))
        
        print(f"\n💾 Results saved to {output_dir}")
        print(f"   📄 Detailed results: {json_file}")
        print(f"   📝 Console output: {console_file}")
        print(f"   📋 App log format: {app_log_file}")

# Utility functions for tests
def assert_module_function_exists(module, function_name: str):
    """Assert that a module has a specific function"""
    assert hasattr(module, function_name), f"Module missing function: {function_name}"

def assert_class_has_method(cls, method_name: str):
    """Assert that a class has a specific method"""
    assert hasattr(cls, method_name), f"Class {cls.__name__} missing method: {method_name}"

def assert_instance_created(factory_func: Callable, expected_type: type = None):
    """Assert that a factory function creates an instance"""
    instance = factory_func()
    assert instance is not None, "Factory function returned None"
    if expected_type:
        assert isinstance(instance, expected_type), f"Expected {expected_type}, got {type(instance)}"
    return instance

def run_all_test_suites():
    """Run all available test suites"""
    import importlib.util
    import glob
    import os
    import sys
    
    # Add current directory to path for imports
    current_dir = os.path.dirname(__file__)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    test_files = glob.glob(os.path.join(current_dir, "test_*.py"))
    test_suites = []
    
    for test_file in test_files:
        if "test_framework.py" in test_file:
            continue
        
        module_name = os.path.basename(test_file)[:-3]  # Remove .py
        try:
            # Load module from file path
            spec = importlib.util.spec_from_file_location(module_name, test_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Find test suite classes
            for attr_name in dir(test_module):
                attr = getattr(test_module, attr_name)
                if isinstance(attr, type) and issubclass(attr, ModuleTestSuite) and attr != ModuleTestSuite:
                    test_suites.append((attr, module_name))
        except Exception as e:
            print(f"⚠️ Could not import {module_name}: {e}")
    
    print(f"\n🚀 Running {len(test_suites)} test suites...")
    
    total_tests = 0
    total_passed = 0
    
    for suite_class, module_name in test_suites:
        print(f"\n📋 {suite_class.__name__} ({module_name})")
        print("-" * 50)
        
        try:
            suite = suite_class()
            results = suite.run_all_tests()
            
            suite_passed = sum(1 for r in results if r.status == "PASS")
            total_tests += len(results)
            total_passed += suite_passed
            
            if len(results) > 0:
                print(f"   Results: {suite_passed}/{len(results)} passed ({suite_passed/len(results)*100:.1f}%)")
            else:
                print("   No tests found")
                
            # Show individual test results for debugging
            for result in results:
                status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⚠️"
                print(f"   {status_icon} {result.test_name}: {result.status}")
            
        except Exception as e:
            print(f"   ❌ Suite failed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    if total_tests > 0:
        pass_rate = (total_passed / total_tests) * 100
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 80:
            print("🎉 EXCELLENT! High pass rate achieved")
        elif pass_rate >= 60:
            print("✅ GOOD! Majority of tests passing")
        elif pass_rate >= 40:
            print("⚠️ MODERATE: Many tests need attention")
        else:
            print("❌ LOW: Significant issues need resolution")

if __name__ == "__main__":
    import sys
    
    print("🧪 UNIVERSAL TEST FRAMEWORK")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "run_all":
        run_all_test_suites()
    else:
        print("✅ Test infrastructure ready")
        print("✅ Dependency manager available") 
        print("✅ Logging system configured")
        print("✅ Ready to run module tests")
        print("\nUsage: python test_framework.py run_all")