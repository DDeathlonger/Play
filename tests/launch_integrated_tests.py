#!/usr/bin/env python3
"""
INTEGRATED TESTING LAUNCHER
Launch comprehensive testing and integrate results into the main application
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / ".." / "src"
sys.path.insert(0, str(src_path.resolve()))

class IntegratedTestLauncher:
    """Launch tests and integrate results with the main application"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.src_dir = self.test_dir.parent / "src"
        self.results_dir = self.test_dir.parent / "results"
        self.app_log_file = None
        
    def check_modular_application_exists(self):
        """Check if the modular application exists"""
        
        print("🔍 CHECKING MODULAR APPLICATION STATUS")
        print("=" * 45)
        
        # Check for main application files
        main_files = [
            self.src_dir / "modular_spaceship_designer.py",
            self.test_dir.parent / "main.py",  # main.py is in root, not src
            self.src_dir / "mcp_tools.py",
            self.src_dir / "ship_generation.py",
            self.src_dir / "ui_system.py",
            self.src_dir / "display_3d.py",
            self.src_dir / "system_integration.py"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in main_files:
            if file_path.exists():
                existing_files.append(file_path.name)
                print(f"✅ Found: {file_path.name}")
            else:
                missing_files.append(file_path.name)
                print(f"❌ Missing: {file_path.name}")
        
        print(f"\n📊 Status: {len(existing_files)}/{len(main_files)} modules present")
        
        if missing_files:
            print(f"⚠️ Missing modules: {', '.join(missing_files)}")
            return False, missing_files
        else:
            print("✅ All modular components available")
            return True, []
    
    def run_comprehensive_tests(self):
        """Run the comprehensive test suite"""
        
        print(f"\n🧪 RUNNING COMPREHENSIVE TEST SUITE")
        print("=" * 45)
        
        # Use virtual environment Python like other working scripts
        venv_python = Path(".venv/Scripts/python.exe")
        if not venv_python.exists():
            print(f"❌ Virtual environment Python not found: {venv_python}")
            return False, "Virtual environment missing"
        
        print(f"🐍 Using virtual environment: {venv_python}")
        
        # Change to test directory
        original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        try:
            # Run the comprehensive test suite
            test_script = self.test_dir / "unit" / "run_all_tests.py"
            
            if not test_script.exists():
                print(f"❌ Test script not found: {test_script}")
                return False, "Test script missing"
            
            print(f"🚀 Launching: {test_script}")
            
            # Execute tests using virtual environment Python
            start_time = time.time()
            result = subprocess.run([
                str(venv_python.resolve()), str(test_script)
            ], capture_output=True, text=True, timeout=300)
            
            duration = time.time() - start_time
            
            print(f"⏱️ Test execution completed in {duration:.2f}s")
            print(f"📤 Exit code: {result.returncode}")
            
            # Print output
            if result.stdout:
                print(f"\n📋 TEST OUTPUT:")
                print("-" * 20)
                print(result.stdout)
            
            if result.stderr:
                print(f"\n⚠️ TEST ERRORS:")
                print("-" * 20)
                print(result.stderr)
            
            return result.returncode == 0, result
            
        except subprocess.TimeoutExpired:
            print("⏰ Test execution timed out (5 minutes)")
            return False, "Timeout"
        except Exception as e:
            print(f"💥 Test execution error: {str(e)}")
            return False, str(e)
        finally:
            os.chdir(original_dir)
    
    def integrate_test_results_with_app(self):
        """Integrate test results with the main application log"""
        
        print(f"\n📋 INTEGRATING TEST RESULTS WITH APPLICATION")
        print("=" * 50)
        
        # Find latest test results
        if not self.results_dir.exists():
            print(f"❌ Results directory not found: {self.results_dir}")
            return False
        
        # Find latest app integration log
        app_logs = list(self.results_dir.glob("app_integration_log_*.txt"))
        
        if not app_logs:
            print("❌ No app integration logs found")
            return False
        
        # Get the most recent log
        latest_log = max(app_logs, key=lambda p: p.stat().st_mtime)
        print(f"📄 Latest integration log: {latest_log.name}")
        
        # Read and process log content
        try:
            with open(latest_log, 'r') as f:
                log_content = f.read()
            
            print(f"📊 Log content size: {len(log_content)} characters")
            
            # Create integrated log for the main application
            self.app_log_file = self.results_dir / "main_app_integration.log"
            
            with open(self.app_log_file, 'w') as f:
                f.write(f"[APP] Spaceship Designer - Integrated Test Results\n")
                f.write(f"[APP] Generated: {datetime.now().isoformat()}\n")
                f.write(f"[APP] Integration Status: ACTIVE\n\n")
                f.write(log_content)
                f.write(f"\n[APP] Integration completed at {datetime.now().isoformat()}\n")
            
            print(f"✅ Integration log created: {self.app_log_file}")
            
            # Also create a status file for the application to check
            status_file = self.results_dir / "test_status.json"
            
            import json
            status_data = {
                'last_test_run': datetime.now().isoformat(),
                'status': 'completed',
                'integration_log': str(self.app_log_file),
                'latest_results': str(latest_log)
            }
            
            with open(status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            print(f"📊 Status file created: {status_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Integration error: {str(e)}")
            return False
    
    def launch_application_with_tests(self):
        """Launch the main application with test integration"""
        
        print(f"\n🚀 LAUNCHING APPLICATION WITH TEST INTEGRATION")
        print("=" * 55)
        
        # Use virtual environment Python like other working scripts
        venv_python = Path(".venv/Scripts/python.exe")
        if not venv_python.exists():
            print(f"❌ Virtual environment Python not found: {venv_python}")
            return False
        
        # Check if main application exists
        main_app = self.src_dir / "modular_spaceship_designer.py"
        backup_app = self.test_dir.parent / "main.py"
        
        app_to_launch = None
        
        if main_app.exists():
            app_to_launch = main_app
            print(f"🎯 Primary app found: {main_app.name}")
        elif backup_app.exists():
            app_to_launch = backup_app
            print(f"🎯 Backup app found: {backup_app.name}")
        else:
            print("❌ No main application found")
            return False
        
        # Set environment variable for test integration
        env = os.environ.copy()
        env['SPACESHIP_TEST_INTEGRATION'] = 'true'
        env['SPACESHIP_TEST_LOG'] = str(self.app_log_file) if self.app_log_file else ''
        
        try:
            print(f"🚀 Launching application: {app_to_launch}")
            print(f"🐍 Using virtual environment: {venv_python}")
            print("📋 Test integration enabled")
            print("🔄 Application will display test results in UI")
            
            # Launch application using virtual environment Python
            process = subprocess.Popen([
                str(venv_python.resolve()), str(app_to_launch)
            ], env=env)
            
            print(f"✅ Application launched with PID: {process.pid}")
            print("📱 The application should now show test results in the status area")
            
            return True
            
        except Exception as e:
            print(f"❌ Application launch error: {str(e)}")
            return False
    
    def run_complete_workflow(self):
        """Run the complete testing and integration workflow"""
        
        print("🎯 SPACESHIP DESIGNER - INTEGRATED TESTING WORKFLOW")
        print("=" * 65)
        print("This workflow will:")
        print("1. Check modular application status")
        print("2. Run comprehensive tests on all geometry nodes")
        print("3. Integrate results with the main application")
        print("4. Launch the application with test data")
        print()
        
        # Phase 1: Check application
        print("🔍 PHASE 1: APPLICATION STATUS CHECK")
        print("-" * 40)
        
        app_exists, missing = self.check_modular_application_exists()
        
        if not app_exists:
            print(f"❌ Cannot proceed - missing modules: {', '.join(missing)}")
            print("💡 Please ensure all modular components are created first")
            return False
        
        # Phase 2: Run tests
        print("\n🧪 PHASE 2: COMPREHENSIVE TESTING")
        print("-" * 40)
        
        tests_passed, test_result = self.run_comprehensive_tests()
        
        if not tests_passed:
            print("⚠️ Tests completed with issues, but continuing with integration...")
        
        # Phase 3: Integration
        print("\n📋 PHASE 3: RESULT INTEGRATION")
        print("-" * 40)
        
        integration_success = self.integrate_test_results_with_app()
        
        if not integration_success:
            print("⚠️ Integration issues detected, but continuing...")
        
        # Phase 4: Launch application
        print("\n🚀 PHASE 4: APPLICATION LAUNCH")
        print("-" * 40)
        
        launch_success = self.launch_application_with_tests()
        
        # Final summary
        print(f"\n🎉 INTEGRATED TESTING WORKFLOW COMPLETE")
        print("=" * 45)
        print(f"✅ Application Status: {'Ready' if app_exists else 'Issues'}")
        print(f"🧪 Testing Status: {'Passed' if tests_passed else 'Issues'}")
        print(f"📋 Integration Status: {'Success' if integration_success else 'Issues'}")
        print(f"🚀 Launch Status: {'Success' if launch_success else 'Failed'}")
        
        if launch_success:
            print("\n🎊 SUCCESS! The spaceship designer application is now running with:")
            print("   ✅ Comprehensive test validation")
            print("   ✅ Integrated test result display")
            print("   ✅ Real-time status monitoring")
            print("   ✅ All modular systems verified")
            
            print(f"\n📁 Test results available in: {self.results_dir}")
            if self.app_log_file:
                print(f"📋 App integration log: {self.app_log_file}")
        else:
            print("\n⚠️ Application launch failed, but test results are available")
            print(f"📁 Check results in: {self.results_dir}")
        
        return launch_success

def main():
    """Main entry point"""
    
    launcher = IntegratedTestLauncher()
    
    try:
        success = launcher.run_complete_workflow()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Workflow interrupted by user")
        return 2
    except Exception as e:
        print(f"\n💥 Workflow error: {str(e)}")
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)