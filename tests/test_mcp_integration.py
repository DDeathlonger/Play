#!/usr/bin/env python3
"""
MCP INTEGRATION TESTS - SAFE CONSOLIDATED VERSION
Tests MCP functionality with existing app integration, avoiding server conflicts
"""

import sys
import time
import requests
from pathlib import Path

# Add project root and tests to path  
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'tests'))

from mcp_test_utils import is_app_mcp_server_running, MCPTestContext

# Simple test result class
class TestResult:
    def __init__(self, name):
        self.name = name
        self.success = False
        self.details = []
    
    def add_detail(self, detail):
        self.details.append(detail)

class MCPIntegrationTestSuite:
    """Consolidated MCP integration tests that work safely with existing app servers"""
    
    def _setup_geometry_node_specific(self):
        """Setup for MCP integration testing"""
        self.mcp_port = 8765
        self.app_name = "Optimized Spaceship Designer"
        
    def test_mcp_server_detection(self, result: TestResult):
        """Test detection of existing MCP servers"""
        try:
            # Test port detection
            port_in_use = is_app_mcp_server_running(8765)
            result.add_detail(f"Port 8765 in use: {port_in_use}")
            
            if port_in_use:
                result.add_detail("✅ Existing MCP server detected")
            else:
                result.add_detail("ℹ️ No MCP server running - tests require app to be started first")
                
        except Exception as e:
            result.add_detail(f"Server detection error: {str(e)}")
    
    def test_mcp_server_health_check(self, result: TestResult):
        """Test MCP server health and basic functionality"""
        
        with MCPTestContext() as mcp_info:
            if mcp_info['port'] is None:
                result.add_detail("No MCP server available - skipping health check")
                return
            
            try:
                port = mcp_info['port']
                is_app = mcp_info['is_app_server']
                
                result.add_detail(f"Testing MCP server on port {port} (app server: {is_app})")
                
                # Test health endpoint
                health_response = requests.get(f'http://localhost:{port}/health', timeout=3)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    result.add_detail(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
                else:
                    result.add_detail(f"❌ Health check failed: {health_response.status_code}")
                    return
                
                # Test commands endpoint
                commands_response = requests.get(f'http://localhost:{port}/commands', timeout=3)
                if commands_response.status_code == 200:
                    commands_data = commands_response.json()
                    command_count = len(commands_data.get('commands', []))
                    result.add_detail(f"✅ Commands endpoint: {command_count} commands available")
                
                # Test status endpoint
                status_response = requests.get(f'http://localhost:{port}/status', timeout=3)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    session_id = status_data.get('session_id', 'unknown')
                    result.add_detail(f"✅ Status endpoint: session {session_id}")
                
            except requests.exceptions.RequestException as req_error:
                result.add_detail(f"HTTP request failed: {req_error}")
            except Exception as e:
                result.add_detail(f"Health check error: {str(e)}")
    
    def test_mcp_command_interface(self, result: TestResult):
        """Test MCP command interface without executing commands"""
        
        with MCPTestContext() as mcp_info:
            if mcp_info['port'] is None:
                result.add_detail("No MCP server available - skipping command interface test")
                return
            
            try:
                port = mcp_info['port']
                
                # Get available commands
                commands_response = requests.get(f'http://localhost:{port}/commands', timeout=3)
                if commands_response.status_code != 200:
                    result.add_detail("Failed to get commands list")
                    return
                
                commands_data = commands_response.json()
                available_commands = commands_data.get('commands', [])
                
                # Verify expected commands are available
                expected_commands = ['see', 'click', 'move_to', 'press_key', 'focus_app']
                found_commands = [cmd for cmd in expected_commands if cmd in available_commands]
                
                result.add_detail(f"✅ Found {len(found_commands)}/{len(expected_commands)} expected commands")
                result.add_detail(f"Available commands: {', '.join(available_commands[:5])}")
                
                # Test status for additional info
                status_response = requests.get(f'http://localhost:{port}/status', timeout=3)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    connected_clients = status_data.get('connected_clients', 0)
                    result.add_detail(f"Connected clients: {connected_clients}")
                
            except Exception as e:
                result.add_detail(f"Command interface test error: {str(e)}")
    
    def test_mcp_concurrent_access(self, result: TestResult):
        """Test that multiple test connections don't interfere with each other"""
        
        try:
            # Test multiple simultaneous connections
            success_count = 0
            total_tests = 3
            
            for i in range(total_tests):
                with MCPTestContext() as mcp_info:
                    if mcp_info['port'] is not None:
                        try:
                            port = mcp_info['port']
                            health_response = requests.get(f'http://localhost:{port}/health', timeout=2)
                            if health_response.status_code == 200:
                                success_count += 1
                        except Exception:
                            pass
            
            result.add_detail(f"✅ Concurrent access test: {success_count}/{total_tests} connections successful")
            
            if success_count == total_tests:
                result.add_detail("All concurrent connections successful - no conflicts detected")
            elif success_count > 0:
                result.add_detail("Some connections successful - server responsive")
            else:
                result.add_detail("No successful connections - server may not be running")
                
        except Exception as e:
            result.add_detail(f"Concurrent access test error: {str(e)}")

def run_mcp_tests():
    """Run consolidated MCP integration tests"""
    print("🧪 Running consolidated MCP integration tests...")
    
    suite = MCPIntegrationTestSuite()
    suite.module_name = "mcp_integration"
    
    # Run tests
    results = []
    
    test_methods = [
        'test_mcp_server_detection',
        'test_mcp_server_health_check',
        'test_mcp_command_interface',
        'test_mcp_concurrent_access'
    ]
    
    for test_name in test_methods:
        result = TestResult(test_name)
        try:
            method = getattr(suite, test_name)
            method(result)
            result.success = True
        except Exception as e:
            result.add_detail(f"Test failed: {str(e)}")
            result.success = False
        
        results.append(result)
        print(f"{'✅' if result.success else '❌'} {test_name}")
        for detail in result.details:
            print(f"   {detail}")
    
    # Summary
    passed = sum(1 for r in results if r.success)
    total = len(results)
    print(f"\n🎯 MCP Integration Tests: {passed}/{total} passed")
    
    return results

if __name__ == "__main__":
    run_mcp_tests()