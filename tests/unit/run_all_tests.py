#!/usr/bin/env python3
"""
UNIVERSAL TEST RUNNER
Master test orchestrator for all modular systems with automatic dependency management
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import test framework and all test suites
from test_framework import UniversalTestRunner, DependencyManager
from test_mcp_tools import MCPToolsTestSuite
from test_ship_generation import ShipGenerationTestSuite
from test_ui_system import UISystemTestSuite
from test_display_3d import Display3DTestSuite
from test_system_integration import SystemIntegrationTestSuite

class MasterTestOrchestrator:
    """Master orchestrator for comprehensive system testing"""
    
    def __init__(self):
        self.runner = UniversalTestRunner()
        self.start_time = None
        self.results_summary = {}
        
    def setup_test_suites(self):
        """Setup all test suites for comprehensive testing"""
        
        print("🧪 SETTING UP COMPREHENSIVE TEST SUITE")
        print("=" * 50)
        
        # Add all test suites
        test_suites = [
            ('MCP Tools', MCPToolsTestSuite("mcp_tools", self.runner.logger)),
            ('Ship Generation', ShipGenerationTestSuite("ship_generation", self.runner.logger)),
            ('UI System', UISystemTestSuite("ui_system", self.runner.logger)),
            ('3D Display', Display3DTestSuite("display_3d", self.runner.logger)),
            ('System Integration', SystemIntegrationTestSuite("system_integration", self.runner.logger))
        ]
        
        for name, suite in test_suites:
            self.runner.add_test_suite(suite)
            print(f"✅ {name} test suite added")
        
        print(f"\n📊 Total test suites: {len(test_suites)}")
        
    def run_comprehensive_tests(self):
        """Run all tests with full dependency management and reporting"""
        
        self.start_time = time.time()
        
        print(f"\n🚀 STARTING COMPREHENSIVE TESTING")
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Phase 1: Dependency Management
        print(f"\n📦 PHASE 1: DEPENDENCY MANAGEMENT")
        print("-" * 40)
        
        deps_available = self.runner.run_dependency_check()
        
        if not deps_available:
            print("⚠️ Critical dependencies missing - some tests may be skipped")
        else:
            print("✅ All critical dependencies available")
        
        # Phase 2: Comprehensive Testing
        print(f"\n🧪 PHASE 2: COMPREHENSIVE MODULE TESTING")
        print("-" * 40)
        
        results = self.runner.run_all_tests()
        
        # Phase 3: Results Analysis
        print(f"\n📊 PHASE 3: RESULTS ANALYSIS")
        print("-" * 40)
        
        self.analyze_results(results)
        
        # Phase 4: Save Results
        print(f"\n💾 PHASE 4: SAVING RESULTS")
        print("-" * 40)
        
        self.save_comprehensive_results(results)
        
        return results
    
    def analyze_results(self, results):
        """Analyze test results and provide insights"""
        
        summary = results['summary']
        
        print(f"📈 TEST EXECUTION SUMMARY")
        print("=" * 30)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Total Time: {summary['total_time']:.2f} seconds")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print()
        
        # Status breakdown
        print(f"📋 STATUS BREAKDOWN")
        print("-" * 20)
        for status, count in summary['status_counts'].items():
            percentage = (count / summary['total_tests']) * 100
            icon = self.get_status_icon(status)
            print(f"{icon} {status}: {count} ({percentage:.1f}%)")
        
        # Performance analysis
        print(f"\n⚡ PERFORMANCE ANALYSIS")
        print("-" * 25)
        
        avg_test_time = summary['total_time'] / max(summary['total_tests'], 1)
        print(f"Average test time: {avg_test_time:.3f}s")
        
        if summary['total_time'] < 30:
            performance_rating = "🚀 Excellent"
        elif summary['total_time'] < 60:
            performance_rating = "✅ Good"
        elif summary['total_time'] < 120:
            performance_rating = "⚠️ Acceptable"
        else:
            performance_rating = "🐌 Needs Optimization"
        
        print(f"Performance rating: {performance_rating}")
        
        # Module analysis
        self.analyze_module_results(results['results'])
        
        # Recommendations
        self.generate_recommendations(results)
    
    def analyze_module_results(self, results):
        """Analyze results by module"""
        
        print(f"\n🔍 MODULE ANALYSIS")
        print("-" * 20)
        
        module_stats = {}
        
        for result in results:
            module = result.module
            if module not in module_stats:
                module_stats[module] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'errors': 0,
                    'skipped': 0,
                    'total_time': 0
                }
            
            stats = module_stats[module]
            stats['total'] += 1
            stats['total_time'] += result.duration
            
            if result.status == 'PASS':
                stats['passed'] += 1
            elif result.status == 'FAIL':
                stats['failed'] += 1
            elif result.status == 'ERROR':
                stats['errors'] += 1
            elif result.status == 'SKIP':
                stats['skipped'] += 1
        
        for module, stats in module_stats.items():
            pass_rate = (stats['passed'] / max(stats['total'], 1)) * 100
            icon = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 60 else "❌"
            
            print(f"{icon} {module}:")
            print(f"   Pass Rate: {pass_rate:.1f}% ({stats['passed']}/{stats['total']})")
            print(f"   Avg Time: {stats['total_time']/max(stats['total'], 1):.3f}s")
            
            if stats['failed'] > 0:
                print(f"   ❌ Failures: {stats['failed']}")
            if stats['errors'] > 0:
                print(f"   💥 Errors: {stats['errors']}")
            if stats['skipped'] > 0:
                print(f"   ⏭️ Skipped: {stats['skipped']}")
            print()
    
    def generate_recommendations(self, results):
        """Generate recommendations based on test results"""
        
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 20)
        
        summary = results['summary']
        
        # Performance recommendations
        if summary['total_time'] > 60:
            print("⚡ Consider optimizing slow tests or running them in parallel")
        
        # Pass rate recommendations
        if summary['pass_rate'] < 80:
            print("🔧 Focus on fixing failing tests to improve reliability")
        
        # Dependency recommendations
        if 'dependencies' in results:
            missing_deps = [dep for dep, available in results['dependencies'].items() if not available]
            if missing_deps:
                print(f"📦 Install missing dependencies: {', '.join(missing_deps)}")
        
        # Module-specific recommendations
        failed_modules = []
        for result in results['results']:
            if result.status in ['FAIL', 'ERROR'] and result.module not in failed_modules:
                failed_modules.append(result.module)
        
        if failed_modules:
            print(f"🎯 Priority modules for debugging: {', '.join(failed_modules)}")
        
        # Integration recommendations
        integration_tests = [r for r in results['results'] if r.module == 'system_integration']
        if integration_tests:
            integration_pass_rate = sum(1 for r in integration_tests if r.status == 'PASS') / len(integration_tests) * 100
            if integration_pass_rate < 90:
                print("🔗 Review inter-module communication and dependencies")
        
        print("✨ Run tests regularly to maintain code quality")
    
    def save_comprehensive_results(self, results):
        """Save comprehensive test results with multiple formats"""
        
        # Create results directory
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        self.runner.save_results(results_dir)
        
        # Save executive summary
        summary_file = results_dir / f"executive_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("SPACESHIP DESIGNER - COMPREHENSIVE TEST RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Test Date: {datetime.now().isoformat()}\n")
            f.write(f"Total Duration: {results['summary']['total_time']:.2f}s\n")
            f.write(f"Total Tests: {results['summary']['total_tests']}\n")
            f.write(f"Pass Rate: {results['summary']['pass_rate']:.1f}%\n\n")
            
            f.write("STATUS BREAKDOWN:\n")
            for status, count in results['summary']['status_counts'].items():
                f.write(f"  {status}: {count}\n")
            
            f.write(f"\nDEPENDENCY STATUS:\n")
            if 'dependencies' in results:
                for dep, available in results['dependencies'].items():
                    status = "✅ Available" if available else "❌ Missing"
                    f.write(f"  {dep}: {status}\n")
        
        # Save app log format for integration
        app_log_file = results_dir / f"app_integration_log_{timestamp}.txt"
        with open(app_log_file, 'w') as f:
            f.write("[SYSTEM] Comprehensive testing initiated\n")
            f.write(f"[SYSTEM] Total tests: {results['summary']['total_tests']}\n")
            f.write(f"[SYSTEM] Pass rate: {results['summary']['pass_rate']:.1f}%\n")
            
            for result in results['results']:
                status_icon = self.get_status_icon(result.status)
                f.write(f"[TEST] {status_icon} {result.module}.{result.test_name}: {result.status}\n")
                
                if result.message:
                    f.write(f"[TEST]     Message: {result.message}\n")
                
                for detail in result.details:
                    f.write(f"[TEST]     Detail: {detail}\n")
            
            f.write("[SYSTEM] Comprehensive testing completed\n")
        
        print(f"📄 Executive summary: {summary_file}")
        print(f"📋 App integration log: {app_log_file}")
        print(f"📁 Full results directory: {results_dir}")
    
    def get_status_icon(self, status):
        """Get icon for test status"""
        icons = {
            "PASS": "✅",
            "FAIL": "❌",
            "SKIP": "⏭️",
            "ERROR": "💥"
        }
        return icons.get(status, "❓")

def main():
    """Main entry point for comprehensive testing"""
    
    print("🎯 SPACESHIP DESIGNER - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print("Testing all modular systems with automatic dependency management")
    print()
    
    # Create master orchestrator
    orchestrator = MasterTestOrchestrator()
    
    try:
        # Setup test suites
        orchestrator.setup_test_suites()
        
        # Run comprehensive tests
        results = orchestrator.run_comprehensive_tests()
        
        # Final summary
        total_time = time.time() - orchestrator.start_time
        
        print(f"\n🎉 COMPREHENSIVE TESTING COMPLETE!")
        print(f"📊 Final Results: {results['summary']['pass_rate']:.1f}% pass rate")
        print(f"⏱️ Total Execution Time: {total_time:.2f} seconds")
        print(f"📈 Tests per second: {results['summary']['total_tests']/total_time:.2f}")
        
        # Exit with appropriate code
        if results['summary']['pass_rate'] >= 80:
            print("✅ Testing SUCCESSFUL - System ready for deployment!")
            return 0
        elif results['summary']['pass_rate'] >= 60:
            print("⚠️ Testing COMPLETED with issues - Review recommended")
            return 1
        else:
            print("❌ Testing FAILED - Critical issues detected")
            return 2
        
    except Exception as e:
        print(f"\n💥 TESTING FRAMEWORK ERROR: {str(e)}")
        print("❌ Unable to complete comprehensive testing")
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)