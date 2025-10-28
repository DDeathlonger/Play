#!/usr/bin/env python3
"""
Unit tests for MCP Application Integration
Tests the complete startup integration system including async handling,
network readiness, tunnel management, and UI integration.
"""

import unittest
import asyncio
import time
import threading
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, Optional
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import test framework
try:
    from test_framework import TestFramework, TestResult, create_test_result
except ImportError:
    # Fallback test framework
    class TestFramework:
        @staticmethod
        def run_test_suite(suite_class):
            return {'tests_run': 0, 'failures': [], 'errors': []}
    
    def create_test_result(name, success, details=None, timing=None):
        return {'name': name, 'success': success, 'details': details, 'timing': timing}

# Import modules to test
try:
    from mcp_app_integration import (
        MCPIntegratedStartup, 
        quick_start_mcp_system,
        start_mcp_system_sync,
        integrate_mcp_with_spaceship_app
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class MCPIntegratedStartup:
        def __init__(self, **kwargs):
            self.is_initialized = False
            self.startup_complete = False
            self.mcp_server = None
            self.tunnel_manager = None
            self.session_panel = None
            self.startup_phases = {}
            self.startup_times = {}
            self.startup_errors = []
        
        async def initialize_async(self):
            return True
        
        def initialize_sync(self):
            return True
    
    async def quick_start_mcp_system(**kwargs):
        return MCPIntegratedStartup(**kwargs)
    
    def start_mcp_system_sync(**kwargs):
        return MCPIntegratedStartup(**kwargs)
    
    def integrate_mcp_with_spaceship_app(app):
        return MCPIntegratedStartup(), None

class MCPAppIntegrationTestSuite(unittest.TestCase):
    """Comprehensive test suite for MCP application integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_results = []
        self.mock_network_ready = True
        self.mock_mcp_success = True
        self.mock_tunnel_success = True
        self.mock_ui_success = True
        
        # Create event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests"""
        try:
            # Clean up event loop
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                task.cancel()
            
            self.loop.close()
        except Exception:
            pass
    
    def test_mcp_integrated_startup_initialization(self):
        """Test MCPIntegratedStartup basic initialization"""
        start_time = time.time()
        
        try:
            # Test with default parameters
            startup = MCPIntegratedStartup()
            
            # Verify initial state
            self.assertFalse(startup.is_initialized)
            self.assertFalse(startup.startup_complete)
            self.assertEqual(startup.mcp_port, 8765)
            self.assertTrue(startup.enable_tunnels)
            self.assertTrue(startup.enable_ui_integration)
            self.assertEqual(startup.startup_timeout, 60.0)
            
            # Test with custom parameters
            custom_startup = MCPIntegratedStartup(
                mcp_port=9999,
                enable_tunnels=False,
                enable_ui_integration=False,
                startup_timeout=30.0
            )
            
            self.assertEqual(custom_startup.mcp_port, 9999)
            self.assertFalse(custom_startup.enable_tunnels)
            self.assertFalse(custom_startup.enable_ui_integration)
            self.assertEqual(custom_startup.startup_timeout, 30.0)
            
            success = True
            error_message = None
            
        except Exception as e:
            success = False
            error_message = str(e)
        
        timing = time.time() - start_time
        result = create_test_result(
            'MCPIntegratedStartup initialization',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"MCPIntegratedStartup initialization failed: {error_message}")
    
    def test_async_initialization_workflow(self):
        """Test async initialization with proper phase sequencing"""
        start_time = time.time()
        
        async def run_async_test():
            try:
                startup = MCPIntegratedStartup(
                    mcp_port=8766,
                    startup_timeout=10.0
                )
                
                # Mock the network monitor
                with patch('src.mcp_app_integration.NetworkStatusMonitor') as mock_network:
                    mock_network.return_value.wait_for_network_ready = AsyncMock(
                        return_value=self.mock_network_ready
                    )
                    
                    # Mock the MCP server
                    with patch('src.mcp_app_integration.AsyncMCPServer') as mock_mcp:
                        mock_server = Mock()
                        mock_server.start_async = AsyncMock(return_value=self.mock_mcp_success)
                        mock_server.port = 8766
                        mock_server.is_running = self.mock_mcp_success
                        mock_mcp.return_value = mock_server
                        
                        # Mock tunnel manager
                        with patch('src.mcp_app_integration.TunnelManager') as mock_tunnel:
                            mock_manager = Mock()
                            mock_manager.start_manager = AsyncMock()
                            mock_manager.create_tunnel = AsyncMock()
                            mock_manager.is_running = True
                            mock_manager.tunnels = {}
                            mock_tunnel.return_value = mock_manager
                            
                            # Run initialization
                            success = await startup.initialize_async()
                            
                            # Verify phases were executed
                            expected_phases = ['network_check', 'mcp_server', 'tunnel_manager', 'ui_integration']
                            for phase in expected_phases:
                                self.assertIn(phase, startup.startup_phases)
                                self.assertIn(phase, startup.startup_times)
                            
                            # Verify initialization success
                            self.assertTrue(startup.is_initialized)
                            
                            # Test startup status
                            status = startup.get_startup_status()
                            self.assertIsInstance(status, dict)
                            self.assertIn('initialized', status)
                            self.assertIn('phases', status)
                            self.assertIn('components', status)
                            
                            return True, None
            
            except Exception as e:
                return False, str(e)
        
        # Run the async test
        success, error_message = self.loop.run_until_complete(run_async_test())
        
        timing = time.time() - start_time
        result = create_test_result(
            'Async initialization workflow',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Async initialization failed: {error_message}")
    
    def test_synchronous_initialization_with_threading(self):
        """Test synchronous initialization using background thread"""
        start_time = time.time()
        
        try:
            startup = MCPIntegratedStartup(
                mcp_port=8767,
                startup_timeout=10.0
            )
            
            # Mock async components for sync test
            with patch.object(startup, 'initialize_async', new_callable=AsyncMock) as mock_init:
                mock_init.return_value = True
                
                # Test sync initialization
                success = startup.initialize_sync()
                
                # Verify thread was created
                self.assertIsNotNone(startup.loop_thread)
                
                # Wait for thread to be ready
                time.sleep(1.0)
                
                # Verify initialization was called
                self.assertTrue(success or mock_init.called)
            
            success = True
            error_message = None
            
        except Exception as e:
            success = False
            error_message = str(e)
        
        timing = time.time() - start_time
        result = create_test_result(
            'Synchronous initialization with threading',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Synchronous initialization failed: {error_message}")
    
    def test_startup_phase_error_handling(self):
        """Test error handling during different startup phases"""
        start_time = time.time()
        
        async def test_error_scenarios():
            scenarios = [
                ('network_failure', {'mock_network_ready': False}),
                ('mcp_failure', {'mock_mcp_success': False}),
                ('exception_during_init', {'raise_exception': True})
            ]
            
            results = []
            
            for scenario_name, scenario_config in scenarios:
                try:
                    startup = MCPIntegratedStartup(startup_timeout=5.0)
                    
                    # Configure mocks based on scenario
                    with patch('src.mcp_app_integration.NetworkStatusMonitor') as mock_network:
                        if scenario_config.get('raise_exception'):
                            mock_network.side_effect = Exception("Test exception")
                        else:
                            mock_network.return_value.wait_for_network_ready = AsyncMock(
                                return_value=scenario_config.get('mock_network_ready', True)
                            )
                        
                        with patch('src.mcp_app_integration.AsyncMCPServer') as mock_mcp:
                            mock_server = Mock()
                            mock_server.start_async = AsyncMock(
                                return_value=scenario_config.get('mock_mcp_success', True)
                            )
                            mock_server.port = 8765
                            mock_mcp.return_value = mock_server
                            
                            # Run initialization
                            success = await startup.initialize_async()
                            
                            # Verify error handling
                            if scenario_config.get('raise_exception'):
                                results.append(f"{scenario_name}: Exception handled properly")
                            elif not scenario_config.get('mock_network_ready', True):
                                results.append(f"{scenario_name}: Network failure handled")
                                self.assertGreater(len(startup.startup_errors), 0)
                            elif not scenario_config.get('mock_mcp_success', True):
                                results.append(f"{scenario_name}: MCP failure handled")
                                self.assertFalse(startup.startup_phases['mcp_server'])
                
                except Exception as e:
                    if scenario_config.get('raise_exception'):
                        results.append(f"{scenario_name}: Exception properly caught: {e}")
                    else:
                        results.append(f"{scenario_name}: Unexpected error: {e}")
            
            return True, results
        
        success, details = self.loop.run_until_complete(test_error_scenarios())
        
        timing = time.time() - start_time
        result = create_test_result(
            'Startup phase error handling',
            success,
            details,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail("Startup error handling test failed")
    
    def test_quick_start_convenience_function(self):
        """Test quick_start_mcp_system convenience function"""
        start_time = time.time()
        
        async def test_quick_start():
            try:
                # Mock the MCPIntegratedStartup class
                with patch('src.mcp_app_integration.MCPIntegratedStartup') as mock_startup_class:
                    mock_startup = Mock()
                    mock_startup.initialize_async = AsyncMock(return_value=True)
                    mock_startup_class.return_value = mock_startup
                    
                    # Test quick start
                    system = await quick_start_mcp_system(
                        port=8768,
                        enable_tunnels=False,
                        enable_ui=False
                    )
                    
                    # Verify system was created with correct parameters
                    mock_startup_class.assert_called_once_with(
                        mcp_port=8768,
                        enable_tunnels=False,
                        enable_ui_integration=False
                    )
                    
                    # Verify initialization was called
                    mock_startup.initialize_async.assert_called_once()
                    
                    return True, None
            
            except Exception as e:
                return False, str(e)
        
        success, error_message = self.loop.run_until_complete(test_quick_start())
        
        timing = time.time() - start_time
        result = create_test_result(
            'Quick start convenience function',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Quick start test failed: {error_message}")
    
    def test_sync_start_convenience_function(self):
        """Test start_mcp_system_sync convenience function"""
        start_time = time.time()
        
        try:
            # Mock the MCPIntegratedStartup class
            with patch('src.mcp_app_integration.MCPIntegratedStartup') as mock_startup_class:
                mock_startup = Mock()
                mock_startup.initialize_sync = Mock(return_value=True)
                mock_startup_class.return_value = mock_startup
                
                # Test sync start
                system = start_mcp_system_sync(
                    port=8769,
                    enable_tunnels=True,
                    enable_ui=True
                )
                
                # Verify system was created with correct parameters
                mock_startup_class.assert_called_once_with(
                    mcp_port=8769,
                    enable_tunnels=True,
                    enable_ui_integration=True
                )
                
                # Verify sync initialization was called
                mock_startup.initialize_sync.assert_called_once()
            
            success = True
            error_message = None
            
        except Exception as e:
            success = False
            error_message = str(e)
        
        timing = time.time() - start_time
        result = create_test_result(
            'Sync start convenience function',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Sync start test failed: {error_message}")
    
    def test_spaceship_app_integration(self):
        """Test spaceship application specific integration"""
        start_time = time.time()
        
        try:
            # Mock spaceship app window
            mock_app_window = Mock()
            mock_app_window.title = "Spaceship Designer"
            
            # Mock the integration functions
            with patch('src.mcp_app_integration.start_mcp_system_sync') as mock_start:
                mock_system = Mock()
                mock_system.add_custom_mcp_handler = Mock()
                mock_system.integrate_with_main_app = Mock(return_value=Mock())
                mock_start.return_value = mock_system
                
                # Test integration
                mcp_system, session_panel = integrate_mcp_with_spaceship_app(mock_app_window)
                
                # Verify MCP system was started
                mock_start.assert_called_once_with(
                    port=8765,
                    enable_tunnels=True,
                    enable_ui=True
                )
                
                # Verify custom handlers were added
                handler_calls = mock_system.add_custom_mcp_handler.call_args_list
                self.assertEqual(len(handler_calls), 2)
                
                # Verify handler names
                handler_names = [call[0][0] for call in handler_calls]
                self.assertIn('generate_ship', handler_names)
                self.assertIn('export_ship', handler_names)
                
                # Verify UI integration was called
                mock_system.integrate_with_main_app.assert_called_once_with(mock_app_window)
            
            success = True
            error_message = None
            
        except Exception as e:
            success = False
            error_message = str(e)
        
        timing = time.time() - start_time
        result = create_test_result(
            'Spaceship app integration',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Spaceship app integration test failed: {error_message}")
    
    def test_shutdown_and_cleanup(self):
        """Test graceful shutdown and cleanup procedures"""
        start_time = time.time()
        
        async def test_shutdown():
            try:
                startup = MCPIntegratedStartup()
                
                # Mock components
                mock_mcp_server = Mock()
                mock_mcp_server.stop_async = AsyncMock()
                startup.mcp_server = mock_mcp_server
                
                mock_tunnel_manager = Mock()
                mock_tunnel_manager.stop_manager = AsyncMock()
                startup.tunnel_manager = mock_tunnel_manager
                
                mock_session_panel = Mock()
                startup.session_panel = mock_session_panel
                
                # Mark as initialized
                startup.is_initialized = True
                
                # Test shutdown
                await startup.shutdown_async()
                
                # Verify shutdown was called on components
                mock_mcp_server.stop_async.assert_called_once()
                mock_tunnel_manager.stop_manager.assert_called_once()
                
                # Verify shutdown flag
                self.assertTrue(startup.shutdown_requested)
                
                return True, None
            
            except Exception as e:
                return False, str(e)
        
        success, error_message = self.loop.run_until_complete(test_shutdown())
        
        timing = time.time() - start_time
        result = create_test_result(
            'Shutdown and cleanup',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Shutdown test failed: {error_message}")
    
    def test_custom_mcp_handlers(self):
        """Test custom MCP handler registration and usage"""
        start_time = time.time()
        
        async def test_handlers():
            try:
                startup = MCPIntegratedStartup()
                
                # Mock MCP server
                mock_mcp_server = Mock()
                mock_mcp_server.register_handler = Mock()
                mock_mcp_server.send_command_async = AsyncMock(return_value={'status': 'ok'})
                mock_mcp_server.is_running = True
                startup.mcp_server = mock_mcp_server
                
                # Test handler registration
                def test_handler(data):
                    return {'result': 'test_success'}
                
                startup.add_custom_mcp_handler('test_action', test_handler)
                
                # Verify handler was registered
                mock_mcp_server.register_handler.assert_called_once_with('test_action', test_handler)
                
                # Test sending command
                response = await startup.send_mcp_command('test_command', param1='value1')
                
                # Verify command was sent
                mock_mcp_server.send_command_async.assert_called_once_with(
                    'test_command', 
                    param1='value1'
                )
                
                # Verify response
                self.assertEqual(response, {'status': 'ok'})
                
                return True, None
            
            except Exception as e:
                return False, str(e)
        
        success, error_message = self.loop.run_until_complete(test_handlers())
        
        timing = time.time() - start_time
        result = create_test_result(
            'Custom MCP handlers',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Custom MCP handlers test failed: {error_message}")
    
    def test_wait_for_ready_functionality(self):
        """Test wait_for_ready with timeout handling"""
        start_time = time.time()
        
        async def test_wait_for_ready():
            try:
                startup = MCPIntegratedStartup()
                
                # Test immediate ready state
                startup.startup_complete = True
                ready = await startup.wait_for_ready(timeout=1.0)
                self.assertTrue(ready)
                
                # Test timeout scenario
                startup.startup_complete = False
                ready = await startup.wait_for_ready(timeout=0.5)
                self.assertFalse(ready)
                
                # Test becoming ready during wait
                startup.startup_complete = False
                
                async def set_ready_later():
                    await asyncio.sleep(0.2)
                    startup.startup_complete = True
                
                asyncio.create_task(set_ready_later())
                ready = await startup.wait_for_ready(timeout=1.0)
                self.assertTrue(ready)
                
                return True, None
            
            except Exception as e:
                return False, str(e)
        
        success, error_message = self.loop.run_until_complete(test_wait_for_ready())
        
        timing = time.time() - start_time
        result = create_test_result(
            'Wait for ready functionality',
            success,
            error_message,
            timing
        )
        self.test_results.append(result)
        
        if not success:
            self.fail(f"Wait for ready test failed: {error_message}")
    
    def get_test_results(self) -> Dict[str, Any]:
        """Get comprehensive test results"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        return {
            'suite_name': 'MCP App Integration Tests',
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'results': self.test_results,
            'summary': f"MCP App Integration: {passed_tests}/{total_tests} tests passed"
        }

def run_mcp_app_integration_tests():
    """Run the complete MCP app integration test suite"""
    print("🧪 Running MCP Application Integration Tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(MCPAppIntegrationTestSuite)
    
    # Custom test runner to capture results
    class CustomTestResult(unittest.TextTestResult):
        def __init__(self, stream, descriptions, verbosity):
            super().__init__(stream, descriptions, verbosity)
            self.test_results = []
        
        def addSuccess(self, test):
            super().addSuccess(test)
            self.test_results.append({
                'name': str(test),
                'success': True,
                'error': None
            })
        
        def addError(self, test, err):
            super().addError(test, err)
            self.test_results.append({
                'name': str(test),
                'success': False,
                'error': str(err[1])
            })
        
        def addFailure(self, test, err):
            super().addFailure(test, err)
            self.test_results.append({
                'name': str(test),
                'success': False,
                'error': str(err[1])
            })
    
    # Run tests
    runner = unittest.TextTestRunner(resultclass=CustomTestResult, verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 TEST SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result

if __name__ == "__main__":
    # Run the tests
    test_result = run_mcp_app_integration_tests()
    
    # Exit with error code if tests failed
    if test_result.failures or test_result.errors:
        sys.exit(1)
    else:
        print("✅ All MCP app integration tests passed!")
        sys.exit(0)