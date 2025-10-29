#!/usr/bin/env python3
"""
Pytest plugin to add emoji flair to test output
Enhances visual feedback while maintaining pytest functionality
"""

import pytest
import time
from datetime import datetime

class EmojiTestReporter:
    """Custom pytest plugin for enhanced visual output with emojis"""
    
    def __init__(self):
        self.session_start_time = None
        self.test_results = []
        
    def pytest_configure(self, config):
        """Configure the emoji reporter"""
        # Only add our reporter if not already configured
        if not hasattr(config, '_emoji_reporter_configured'):
            config._emoji_reporter_configured = True
            
    def pytest_sessionstart(self, session):
        """Called after the Session object has been created"""
        self.session_start_time = time.time()
        print("\n🚀 SPACESHIP DESIGNER TEST SESSION STARTING")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐍 Python: {session.config.getoption('--tb')}")
        print("=" * 60)
        
    def pytest_runtest_logstart(self, nodeid, location):
        """Called at the start of running the runtest protocol for a single item"""
        test_name = nodeid.split("::")[-1]
        print(f"\n🧪 Running: {test_name}")
        
    def pytest_runtest_logreport(self, report):
        """Process test reports for enhanced output"""
        if report.when == "call":
            test_name = report.nodeid.split("::")[-1]
            
            if report.outcome == "passed":
                duration = f"{report.duration:.3f}s"
                print(f"   ✅ PASSED ({duration})")
                self.test_results.append(('✅', test_name, 'PASSED', duration))
                
            elif report.outcome == "failed":
                duration = f"{report.duration:.3f}s"
                print(f"   ❌ FAILED ({duration})")
                self.test_results.append(('❌', test_name, 'FAILED', duration))
                
            elif report.outcome == "skipped":
                print(f"   ⏭️  SKIPPED")
                self.test_results.append(('⏭️', test_name, 'SKIPPED', '0s'))
                
    def pytest_sessionfinish(self, session, exitstatus):
        """Called after whole test run finished"""
        duration = time.time() - self.session_start_time if self.session_start_time else 0
        
        print("\n" + "=" * 60)
        print("🏁 TEST SESSION COMPLETE")
        print("=" * 60)
        
        # Count results
        passed = len([r for r in self.test_results if r[2] == 'PASSED'])
        failed = len([r for r in self.test_results if r[2] == 'FAILED'])
        skipped = len([r for r in self.test_results if r[2] == 'SKIPPED'])
        total = len(self.test_results)
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   🎯 Total Tests: {total}")
        if passed > 0:
            print(f"   ✅ Passed: {passed}")
        if failed > 0:
            print(f"   ❌ Failed: {failed}")
        if skipped > 0:
            print(f"   ⏭️  Skipped: {skipped}")
            
        print(f"⏱️  Total Time: {duration:.2f}s")
        
        # Status emoji
        if failed == 0 and total > 0:
            print("🎉 ALL TESTS PASSED!")
        elif failed > 0:
            print("💥 SOME TESTS FAILED!")
        else:
            print("⚠️  NO TESTS RAN")
            
        print("=" * 60)

# Global reporter instance
_emoji_reporter = EmojiTestReporter()

# Pytest hooks
def pytest_configure(config):
    _emoji_reporter.pytest_configure(config)

def pytest_sessionstart(session):
    _emoji_reporter.pytest_sessionstart(session)
    
def pytest_runtest_logstart(nodeid, location):
    _emoji_reporter.pytest_runtest_logstart(nodeid, location)
    
def pytest_runtest_logreport(report):
    _emoji_reporter.pytest_runtest_logreport(report)
    
def pytest_sessionfinish(session, exitstatus):
    _emoji_reporter.pytest_sessionfinish(session, exitstatus)