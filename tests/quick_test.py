#!/usr/bin/env python3
"""
QUICK TEST RUNNER
Fast execution of unit tests with immediate feedback
"""

import sys
import time
from pathlib import Path

# Add test directory to path
test_dir = Path(__file__).parent / "unit"
sys.path.insert(0, str(test_dir))

# Also add the unit test directory directly
unit_test_dir = Path(__file__).parent / "unit"
if str(unit_test_dir) not in sys.path:
    sys.path.insert(0, str(unit_test_dir))

def run_quick_test():
    """Run a quick test to verify the testing framework works"""
    
    print("⚡ QUICK TEST EXECUTION")
    print("=" * 30)
    
    try:
        # Import and run framework test
        from test_framework import UniversalTestRunner, DependencyManager
        
        print("✅ Test framework imported successfully")
        
        # Quick dependency check
        print("\n📦 Quick dependency check...")
        deps = DependencyManager.ensure_all_dependencies()
        
        available_count = sum(1 for available in deps.values() if available)
        total_count = len(deps)
        
        print(f"📊 Dependencies: {available_count}/{total_count} available")
        
        for dep, available in deps.items():
            status = "✅" if available else "❌"
            print(f"   {status} {dep}")
        
        # Quick framework test
        print("\n🧪 Testing framework capabilities...")
        
        runner = UniversalTestRunner()
        print("✅ Test runner created")
        
        # Test logger
        test_result = runner.logger.log_test_start("quick_test", "framework")
        test_result.add_detail("Framework validation test")
        test_result.complete("PASS", "Quick test successful")
        runner.logger.log_test_complete(test_result)
        
        print("✅ Test logging works")
        
        # Test result saving
        results_dir = Path(__file__).parent / "results"
        runner.logger.save_results(results_dir / "quick_test_results.json")
        
        print(f"✅ Results saved to {results_dir}")
        
        summary = runner.logger.get_summary()
        print(f"\n📊 Quick Test Summary:")
        print(f"   Tests: {summary['total_tests']}")
        print(f"   Time: {summary['total_time']:.3f}s")
        print(f"   Pass Rate: {summary['pass_rate']:.1f}%")
        
        print(f"\n🎉 QUICK TEST SUCCESSFUL!")
        print("🚀 Ready to run comprehensive tests")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    
    start_time = time.time()
    
    print("🎯 SPACESHIP DESIGNER - QUICK TEST")
    print("Testing framework readiness and basic functionality")
    print()
    
    success = run_quick_test()
    
    duration = time.time() - start_time
    
    print(f"\n⏱️ Quick test completed in {duration:.2f}s")
    
    if success:
        print("✅ System ready for comprehensive testing!")
        print("\nNext steps:")
        print("  python tests/unit/run_all_tests.py    # Run all module tests")
        print("  python tests/launch_integrated_tests.py  # Full integration")
        return 0
    else:
        print("❌ Issues detected - check error messages above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)