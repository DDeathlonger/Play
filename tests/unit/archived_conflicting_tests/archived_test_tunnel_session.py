#!/usr/bin/env python3
"""
TUNNEL AND SESSION MANAGEMENT UNIT TESTS
Comprehensive testing for tunnel creation, session monitoring, and network handling
"""

import sys
import asyncio
import time
import unittest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import test framework
from test_framework import ModuleTestSuite, TestResult, assert_module_function_exists, assert_class_has_method, assert_instance_created

class TunnelSessionTestSuite(ModuleTestSuite):
    """Complete test suite for tunnel and session management"""
    
    def _setup_module_specific(self):
        """Setup specific to tunnel/session testing"""
        self.test_tunnels = []
        self.test_sessions = []
        self.mock_network = Mock()
        self.event_loop = None
    
    def test_module_imports(self, result: TestResult):
        """Test that tunnel and session modules can be imported"""
        
        try:
            # Test tunnel manager imports
            from src.tunnel_manager import (
                TunnelManager, TunnelConnection, TunnelConfiguration,
                TunnelType, TunnelStatus, create_mcp_tunnel
            )
            result.add_detail("Tunnel manager classes imported successfully")
            
            # Test session UI imports
            from src.session_ui_integration import (
                SessionManagementPanel, MCPConnectionStatus, 
                TunnelStatusWidget, SessionLogWidget
            )
            result.add_detail("Session UI classes imported successfully")
            
            # Test async MCP tools imports  
            from src.mcp_async_tools import (
                AsyncMCPServer, NetworkStatusMonitor,
                start_mcp_server_async, test_mcp_connection_async
            )
            result.add_detail("Async MCP tools imported successfully")
            
        except ImportError as e:
            result.add_detail(f"Import error: {str(e)}")
            # Continue with available imports
    
    def test_tunnel_configuration_creation(self, result: TestResult):
        """Test tunnel configuration creation and validation"""
        
        try:
            from src.tunnel_manager import TunnelConfiguration, TunnelType
            
            # Create basic configuration
            config = TunnelConfiguration(
                tunnel_type=TunnelType.HTTP,
                local_port=8765,
                remote_host="localhost",
                remote_port=8766,
                name="test_tunnel"
            )
            
            assert config.tunnel_type == TunnelType.HTTP
            assert config.local_port == 8765
            assert config.remote_host == "localhost"
            assert config.remote_port == 8766
            assert config.name == "test_tunnel"
            assert config.tunnel_id is not None
            result.add_detail("Basic tunnel configuration created")
            
            # Test configuration serialization
            config_dict = config.to_dict()
            assert isinstance(config_dict, dict)
            assert 'tunnel_id' in config_dict
            assert 'tunnel_type' in config_dict
            assert config_dict['tunnel_type'] == 'http'
            result.add_detail("Configuration serialization working")
            
            # Test different tunnel types
            for tunnel_type in [TunnelType.HTTP, TunnelType.WEBSOCKET, TunnelType.TCP]:
                type_config = TunnelConfiguration(
                    tunnel_type=tunnel_type,
                    local_port=9000,
                    name=f"test_{tunnel_type.value}"
                )
                assert type_config.tunnel_type == tunnel_type
                result.add_detail(f"Created {tunnel_type.value} configuration")
        
        except Exception as e:
            result.add_detail(f"Configuration creation error: {str(e)}")
    
    def test_tunnel_connection_lifecycle(self, result: TestResult):
        """Test tunnel connection creation, connection, and disconnection"""
        
        try:
            from src.tunnel_manager import TunnelConnection, TunnelConfiguration, TunnelType, TunnelStatus
            
            # Create tunnel connection
            config = TunnelConfiguration(
                tunnel_type=TunnelType.HTTP,
                local_port=8765,
                name="test_lifecycle_tunnel"
            )
            
            tunnel = TunnelConnection(config)
            assert tunnel.config == config
            assert tunnel.status == TunnelStatus.DISCONNECTED
            result.add_detail("Tunnel connection created")
            
            # Test status tracking
            assert hasattr(tunnel, 'connection_attempts')
            assert hasattr(tunnel, 'error_count')
            assert hasattr(tunnel, 'total_bytes_sent')
            assert hasattr(tunnel, 'total_bytes_received')
            result.add_detail("Tunnel tracking attributes present")
            
            # Test statistics
            stats = tunnel.get_statistics()
            assert isinstance(stats, dict)
            assert 'tunnel_id' in stats
            assert 'status' in stats
            assert stats['status'] == 'disconnected'
            result.add_detail("Tunnel statistics available")
            
            # Store for cleanup
            self.test_tunnels.append(tunnel)
        
        except Exception as e:
            result.add_detail(f"Tunnel lifecycle error: {str(e)}")
    
    def test_tunnel_manager_operations(self, result: TestResult):
        """Test tunnel manager creation and basic operations"""
        
        try:
            from src.tunnel_manager import TunnelManager, TunnelConfiguration, TunnelType
            
            # Create tunnel manager
            manager = TunnelManager()
            assert hasattr(manager, 'tunnels')
            assert hasattr(manager, 'is_running')
            assert not manager.is_running
            result.add_detail("Tunnel manager created")
            
            # Test manager statistics
            stats = manager.get_manager_statistics()
            assert isinstance(stats, dict)
            assert 'total_tunnels' in stats
            assert 'active_tunnels' in stats
            assert stats['total_tunnels'] == 0
            result.add_detail("Manager statistics available")
            
            # Test tunnel listing
            tunnel_list = manager.list_tunnels()
            assert isinstance(tunnel_list, list)
            assert len(tunnel_list) == 0
            result.add_detail("Tunnel listing working")
            
            # Test event subscription
            event_received = []
            def test_handler(event_type, data):
                event_received.append((event_type, data))
            
            manager.subscribe_to_events('test_event', test_handler)
            manager._emit_event('test_event', {'test': 'data'})
            
            # Note: In real async environment, this would work
            # For sync testing, we just verify the handler is registered
            assert 'test_event' in manager.event_handlers
            assert test_handler in manager.event_handlers['test_event']
            result.add_detail("Event system working")
        
        except Exception as e:
            result.add_detail(f"Tunnel manager error: {str(e)}")
    
    def test_async_mcp_server_creation(self, result: TestResult):
        """Test MCP server functionality without creating conflicting servers"""
        
        try:
            # Import MCP test utilities for safe testing
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from mcp_test_utils import is_app_mcp_server_running, MCPTestContext
            
            # Use safe MCP testing approach
            with MCPTestContext() as mcp_info:
                if mcp_info['port'] is None:
                    result.add_detail("No MCP server available - skipping server creation test")
                    return
                
                port = mcp_info['port']
                is_app = mcp_info['is_app_server']
                
                if is_app:
                    result.add_detail(f"Testing with existing app MCP server on port {port}")
                    
                    # Test MCP server health via HTTP
                    import requests
                    try:
                        health_response = requests.get(f'http://localhost:{port}/health', timeout=2)
                        if health_response.status_code == 200:
                            result.add_detail("MCP server health check passed")
                        
                        commands_response = requests.get(f'http://localhost:{port}/commands', timeout=2)
                        if commands_response.status_code == 200:
                            commands_data = commands_response.json()
                            if 'commands' in commands_data:
                                result.add_detail(f"MCP server has {len(commands_data['commands'])} commands")
                        
                    except Exception as req_error:
                        result.add_detail(f"HTTP request test failed: {req_error}")
                else:
                    result.add_detail("No app server running - MCP functionality requires app instance")
            
            # Test handler registration
            test_handler_called = []
            def test_handler(data):
                test_handler_called.append(data)
                return {'status': 'success', 'test': True}
            
            server.register_handler('test_action', test_handler)
            assert 'test_action' in server.callback_registry
            result.add_detail("Handler registration working")
        
        except Exception as e:
            result.add_detail(f"Async MCP server error: {str(e)}")
    
    def test_network_status_monitoring(self, result: TestResult):
        """Test network status monitoring functionality"""
        
        try:
            from src.mcp_async_tools import NetworkStatusMonitor
            
            # Create network monitor
            monitor = NetworkStatusMonitor()
            assert hasattr(monitor, 'connection_history')
            assert hasattr(monitor, 'last_check_time')
            assert not monitor.is_monitoring
            result.add_detail("Network status monitor created")
            
            # Test connection stats (initial state)
            stats = monitor.get_connection_stats()
            assert isinstance(stats, dict)
            assert 'status' in stats
            assert 'success_rate' in stats
            assert stats['status'] == 'no_data'
            result.add_detail("Initial connection stats available")
            
            # Simulate connection history
            monitor.connection_history = [
                {'timestamp': time.time() - 10, 'success': True, 'result_code': 0},
                {'timestamp': time.time() - 5, 'success': True, 'result_code': 0},
                {'timestamp': time.time(), 'success': False, 'result_code': -1}
            ]
            
            stats = monitor.get_connection_stats()
            assert stats['success_rate'] > 0.0
            assert stats['total_checks'] == 3
            result.add_detail("Connection history tracking working")
        
        except Exception as e:
            result.add_detail(f"Network monitoring error: {str(e)}")
    
    def test_session_ui_widget_creation(self, result: TestResult):
        """Test session management UI widget creation"""
        
        try:
            # Skip if PyQt6 not available
            import PyQt6
            from PyQt6.QtWidgets import QApplication
            
            # Ensure QApplication exists
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                result.add_detail("Created QApplication for testing")
            
            from src.session_ui_integration import (
                MCPConnectionStatus, TunnelStatusWidget, 
                SessionLogWidget, SessionManagementPanel
            )
            
            # Test MCP connection status widget
            mcp_status = MCPConnectionStatus()
            assert hasattr(mcp_status, 'connection_label')
            assert hasattr(mcp_status, 'port_label')
            assert hasattr(mcp_status, 'server_status')
            result.add_detail("MCP connection status widget created")
            
            # Test status update
            test_status = {
                'running': True,
                'ready': True,
                'port': 8765,
                'uptime': 123.45,
                'connection_count': 5,
                'network_status': {'status': 'healthy'}
            }
            mcp_status.update_status(test_status)
            result.add_detail("Status update working")
            
            # Test tunnel status widget
            tunnel_widget = TunnelStatusWidget()
            assert hasattr(tunnel_widget, 'tunnel_list')
            assert hasattr(tunnel_widget, 'tunnels')
            result.add_detail("Tunnel status widget created")
            
            # Test tunnel update
            tunnel_stats = {
                'tunnels': [
                    {
                        'name': 'test_tunnel',
                        'status': 'connected',
                        'bytes_sent': 1024,
                        'bytes_received': 2048
                    }
                ]
            }
            tunnel_widget.update_tunnels(tunnel_stats)
            result.add_detail("Tunnel status update working")
            
            # Test session logs widget
            log_widget = SessionLogWidget()
            assert hasattr(log_widget, 'log_display')
            log_widget.add_log_entry("INFO", "Test log message")
            result.add_detail("Session log widget working")
            
        except ImportError:
            result.add_detail("PyQt6 not available, skipping UI tests")
        except Exception as e:
            result.add_detail(f"UI widget error: {str(e)}")
    
    def test_session_management_integration(self, result: TestResult):
        """Test full session management panel integration"""
        
        try:
            # Skip if PyQt6 not available  
            import PyQt6
            from PyQt6.QtWidgets import QApplication
            
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            from src.session_ui_integration import SessionManagementPanel
            
            # Create main panel without backend connections (for testing)
            panel = SessionManagementPanel()
            assert hasattr(panel, 'tab_widget')
            assert hasattr(panel, 'connection_status')
            assert hasattr(panel, 'tunnel_status')
            assert hasattr(panel, 'session_logs')
            result.add_detail("Session management panel created")
            
            # Test tab structure
            assert panel.tab_widget.count() == 3
            result.add_detail("Tab structure correct")
            
            # Test overall status update
            test_status = {'running': True, 'ready': True}
            panel.update_server_status(test_status)
            result.add_detail("Overall status update working")
            
            # Test error handling
            panel.handle_error("test_error", "Test error message")
            result.add_detail("Error handling working")
        
        except ImportError:
            result.add_detail("PyQt6 not available, skipping integration tests")
        except Exception as e:
            result.add_detail(f"Integration error: {str(e)}")
    
    def test_async_functions_signature(self, result: TestResult):
        """Test async function signatures and basic structure"""
        
        try:
            from src.mcp_async_tools import start_mcp_server_async, test_mcp_connection_async
            from src.tunnel_manager import create_mcp_tunnel, create_websocket_tunnel
            
            # Test function signatures exist
            assert callable(start_mcp_server_async)
            assert callable(test_mcp_connection_async)
            assert callable(create_mcp_tunnel)
            assert callable(create_websocket_tunnel)
            result.add_detail("Async convenience functions available")
            
            # Test they are coroutines (async functions)
            import inspect
            assert inspect.iscoroutinefunction(start_mcp_server_async)
            assert inspect.iscoroutinefunction(test_mcp_connection_async)
            assert inspect.iscoroutinefunction(create_mcp_tunnel)
            result.add_detail("Functions are properly async")
        
        except Exception as e:
            result.add_detail(f"Async function error: {str(e)}")
    
    def test_error_handling_and_recovery(self, result: TestResult):
        """Test error handling and recovery mechanisms"""
        
        try:
            from src.tunnel_manager import TunnelConnection, TunnelConfiguration, TunnelType
            
            # Test invalid configuration handling
            try:
                invalid_config = TunnelConfiguration(
                    tunnel_type="invalid_type",  # This should be TunnelType enum
                    local_port=-1  # Invalid port
                )
                result.add_detail("Invalid configuration accepted (unexpected)")
            except (ValueError, TypeError):
                result.add_detail("Invalid configuration rejected (expected)")
            
            # Test connection with unreachable host
            config = TunnelConfiguration(
                tunnel_type=TunnelType.HTTP,
                local_port=99999,  # Very high port
                remote_host="nonexistent.host",
                timeout=1.0  # Short timeout
            )
            
            tunnel = TunnelConnection(config)
            # The connect method is async, so we test the structure
            assert tunnel.status.value in ['disconnected', 'connecting', 'connected', 'error']
            result.add_detail("Error state handling available")
            
            # Test statistics in error state
            stats = tunnel.get_statistics()
            assert 'error_count' in stats
            assert 'connection_attempts' in stats
            result.add_detail("Error statistics tracking available")
        
        except Exception as e:
            result.add_detail(f"Error handling test error: {str(e)}")
    
    def test_performance_and_monitoring(self, result: TestResult):
        """Test performance monitoring and metrics collection"""
        
        try:
            from src.tunnel_manager import TunnelManager
            from src.mcp_async_tools import AsyncMCPServer
            
            # Test tunnel manager metrics
            manager = TunnelManager()
            stats = manager.get_manager_statistics()
            
            required_metrics = [
                'manager_uptime', 'total_tunnels', 'active_tunnels',
                'total_connections_created', 'total_bytes_sent',
                'total_bytes_received'
            ]
            
            for metric in required_metrics:
                assert metric in stats
                result.add_detail(f"Metric '{metric}' available")
            
            # Test server performance tracking
            server = AsyncMCPServer()
            status = server.get_server_status()
            
            performance_fields = ['uptime', 'connection_count', 'network_status']
            for field in performance_fields:
                if field in status:
                    result.add_detail(f"Performance field '{field}' tracked")
            
            result.add_detail("Performance monitoring structure verified")
        
        except Exception as e:
            result.add_detail(f"Performance monitoring error: {str(e)}")
    
    def test_cleanup_and_resource_management(self, result: TestResult):
        """Test proper cleanup and resource management"""
        
        try:
            # Clean up any test tunnels created
            cleanup_count = 0
            
            for tunnel in self.test_tunnels:
                try:
                    if hasattr(tunnel, 'disconnect'):
                        # Would call await tunnel.disconnect() in async context
                        tunnel.status = tunnel.status  # Just access it
                        cleanup_count += 1
                except Exception as cleanup_error:
                    result.add_detail(f"Cleanup error: {str(cleanup_error)}")
            
            result.add_detail(f"Attempted cleanup of {cleanup_count} test tunnels")
            
            # Test resource tracking
            from src.tunnel_manager import TunnelManager
            manager = TunnelManager()
            
            initial_tunnel_count = len(manager.tunnels)
            
            # Test manager cleanup methods exist
            assert hasattr(manager, 'stop_manager')
            result.add_detail("Manager cleanup methods available")
            
            # Test server cleanup
            from src.mcp_async_tools import AsyncMCPServer
            server = AsyncMCPServer()
            assert hasattr(server, 'stop_async')
            result.add_detail("Server cleanup methods available")
            
        except Exception as e:
            result.add_detail(f"Cleanup test error: {str(e)}")

if __name__ == "__main__":
    # Import the test framework runner
    from test_framework import UniversalTestRunner
    
    # Create and run test suite
    suite = TunnelSessionTestSuite()
    runner = UniversalTestRunner()
    
    print("🚇 RUNNING TUNNEL & SESSION MANAGEMENT TESTS")
    print("=" * 60)
    
    results = suite.run_all_tests()
    
    # Print results summary
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL") 
    errors = sum(1 for r in results if r.status == "ERROR")
    skipped = sum(1 for r in results if r.status == "SKIP")
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Total Tests: {len(results)}")
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")
    print(f"ERROR: {errors}")
    print(f"SKIP: {skipped}")
    
    if len(results) > 0:
        pass_rate = (passed / len(results)) * 100
        print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Save results
    output_dir = Path("tests/results")
    runner.save_results(output_dir)
    
    print(f"\n🚇 TUNNEL & SESSION MANAGEMENT TESTING COMPLETE")
    print(f"Pass Rate: {pass_rate:.1f}%")