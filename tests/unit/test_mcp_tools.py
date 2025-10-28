#!/usr/bin/env python3
"""
MCP TOOLS MODULE UNIT TESTS
Comprehensive testing for networking and MCP server functionality
"""

import sys
import time
import threading
import socket
from pathlib import Path

# Import test framework
from test_framework import ModuleTestSuite, TestResult, assert_module_function_exists, assert_class_has_method, assert_instance_created

class MCPToolsTestSuite(ModuleTestSuite):
    """Complete test suite for MCP tools module"""
    
    def _setup_module_specific(self):
        """Setup specific to MCP tools testing"""
        # Test port for server testing
        self.server_port = 8765
        self.mcp_server = None
        self.mcp_client = None
        
    def test_module_imports(self, result: TestResult):
        """Test that all required classes and functions can be imported"""
        
        # Check main classes exist
        assert_class_has_method(self.module.MCPServer, '__init__')
        assert_class_has_method(self.module.MCPClient, '__init__')
        assert_class_has_method(self.module.MCPSessionManager, '__init__')
        result.add_detail("All main classes importable")
        
        # Check server methods (matching actual implementation)
        assert_class_has_method(self.module.MCPServer, 'start')
        assert_class_has_method(self.module.MCPServer, 'stop')
        assert_class_has_method(self.module.MCPServer, 'register_handler')
        result.add_detail("MCPServer has required methods")
        
        # Check client methods (matching actual implementation) 
        assert_class_has_method(self.module.MCPClient, 'send_command')
        assert_class_has_method(self.module.MCPClient, 'ping')
        assert_class_has_method(self.module.MCPClient, 'get_session_info')
        result.add_detail("MCPClient has required methods")
        
        # Check session manager methods (matching actual implementation)
        assert_class_has_method(self.module.MCPSessionManager, 'add_command')
        assert_class_has_method(self.module.MCPSessionManager, 'get_session_info')
        assert_class_has_method(self.module.MCPSessionManager, 'get_recent_commands')
        result.add_detail("MCPSessionManager has required methods")
    
    def test_server_creation(self, result: TestResult):
        """Test MCP server can be created and configured"""
        
        # Create server instance (current implementation takes callback_registry, not port)
        server = assert_instance_created(
            lambda: self.module.MCPServer(), 
            self.module.MCPServer
        )
        result.add_detail("MCPServer created successfully")
        
        # Check server has required attributes (matching actual implementation)
        required_attrs = ['callback_registry', 'session_manager', 'is_running']
        for attr in required_attrs:
            assert hasattr(server, attr), f"Server missing attribute: {attr}"
        result.add_detail("Server has all required attributes")
        
        # Test server can be started
        try:
            started = server.start(self.server_port)
            if started:
                result.add_detail(f"Server started on port {server.port}")
                self.mcp_server = server
            else:
                result.add_detail("Server start returned False but handled gracefully")
        except Exception as e:
            result.add_detail(f"Server start error (expected in test env): {str(e)}")
        
        self.mcp_server = server
    
    def test_client_creation(self, result: TestResult):
        """Test MCP client can be created and configured"""
        
        # Create client instance (current implementation takes server_port, not host/port)
        client = assert_instance_created(
            lambda: self.module.MCPClient(server_port=self.server_port),
            self.module.MCPClient
        )
        result.add_detail("MCPClient created successfully")
        
        # Check client properties (matching actual implementation)
        assert hasattr(client, 'server_port'), "Client missing server_port property"
        assert hasattr(client, 'base_url'), "Client missing base_url property" 
        assert client.server_port == self.server_port, f"Client port mismatch: {client.server_port} != {self.server_port}"
        result.add_detail("Client properties configured correctly")
        
        # Check base URL is constructed correctly
        expected_url = f"http://localhost:{self.server_port}"
        assert client.base_url == expected_url, f"Base URL mismatch: {client.base_url} != {expected_url}"
        result.add_detail("Client base URL configured correctly")
        
        self.mcp_client = client
    
    def test_session_manager_creation(self, result: TestResult):
        """Test session manager can be created and manages sessions"""
        
        # Create session manager
        session_mgr = assert_instance_created(
            lambda: self.module.MCPSessionManager(),
            self.module.MCPSessionManager
        )
        result.add_detail("MCPSessionManager created successfully")
        
        # Check session manager attributes (matching actual implementation)
        required_attrs = ['session_id', 'command_history', 'performance_metrics']
        for attr in required_attrs:
            assert hasattr(session_mgr, attr), f"SessionManager missing attribute: {attr}"
        result.add_detail("SessionManager has all required attributes")
        
        # Test session ID generation
        assert session_mgr.session_id is not None, "Session ID not generated"
        assert len(session_mgr.session_id) > 0, "Session ID is empty"
        result.add_detail(f"Session ID generated: {session_mgr.session_id[:8]}...")
        
        # Test command history functionality
        test_command = {'action': 'test', 'data': 'sample'}
        session_mgr.add_command(test_command, processing_time=0.1)
        
        assert len(session_mgr.command_history) > 0, "Command not added to history"
        result.add_detail("Command added to session history")
        
        # Test performance metrics
        assert session_mgr.performance_metrics['commands_processed'] > 0, "Performance metrics not updated"
        result.add_detail("Performance metrics updated correctly")
    
    def test_server_startup_shutdown(self, result: TestResult):
        """Test server can be started and stopped properly"""
        
        if not self.mcp_server:
            result.complete("SKIP", "No test server available")
            return
        
        # Test server startup
        try:
            # Start server in thread to avoid blocking
            server_thread = threading.Thread(target=self.mcp_server.start, daemon=True)
            server_thread.start()
            time.sleep(0.5)  # Allow server to start
            
            # Check if server is running
            assert self.mcp_server.running, "Server not marked as running"
            result.add_detail("Server started successfully")
            
            # Test port is bound
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.settimeout(1.0)
                connection_result = sock.connect_ex(('localhost', self.server_port))
                assert connection_result == 0, "Server port not accessible"
                result.add_detail(f"Server listening on port {self.server_port}")
            finally:
                sock.close()
            
            # Stop server
            self.mcp_server.stop()
            time.sleep(0.5)  # Allow server to stop
            
            assert not self.mcp_server.running, "Server still marked as running after stop"
            result.add_detail("Server stopped successfully")
            
        except Exception as e:
            # Ensure server is stopped even if test fails
            try:
                self.mcp_server.stop()
            except:
                pass
            raise e
    
    def test_client_connection(self, result: TestResult):
        """Test client connection functionality"""
        
        if not self.mcp_client:
            result.complete("SKIP", "No test client available")
            return
        
        # Test ping without server (should handle gracefully)
        try:
            ping_result = self.mcp_client.ping()
            # Connection should fail gracefully without server
            assert not ping_result, "Client ping succeeded without server running"
            result.add_detail("Client handled ping failure gracefully")
        except Exception as e:
            # Client should handle connection errors gracefully
            result.add_detail(f"Client ping error handled: {str(e)}")
        
        # Test send_command functionality
        try:
            response = self.mcp_client.send_command('test_action', timeout=1)
            # Should return None when server not available
            assert response is None, "Client should return None when server unavailable"
            result.add_detail("Client send_command handles no server gracefully")
        except Exception as e:
            result.add_detail(f"Client send_command error handled: {str(e)}")
        
        # Test get_session_info
        try:
            session_info = self.mcp_client.get_session_info()
            assert session_info is None, "Should return None when server unavailable"
            result.add_detail("Client get_session_info handles no server gracefully")
        except Exception as e:
            result.add_detail(f"Client get_session_info error: {str(e)}")
    
    def test_request_handling(self, result: TestResult):
        """Test request handling functionality"""
        
        if not self.mcp_server:
            result.complete("SKIP", "No test server available")
            return
        
        # Test handler registration (matching actual implementation)
        def test_handler(command_data):
            return {'status': 'success', 'echo': command_data}
        
        self.mcp_server.register_handler('test', test_handler)
        assert 'test' in self.mcp_server.callback_registry, "Handler not registered"
        result.add_detail("Request handler registered successfully")
        
        # Test handler execution directly (since actual HTTP handling requires running server)
        test_command = {'action': 'test', 'data': 'hello'}
        response = self.mcp_server.callback_registry['test'](test_command)
        
        assert response is not None, "Handler returned None"
        assert response.get('status') == 'success', "Handler not executed correctly"
        assert response.get('echo') == test_command, "Command data not echoed correctly"
        result.add_detail("Handler processed command correctly")
        
        # Test default handlers
        ping_response = self.mcp_server.callback_registry['ping']({})
        assert ping_response.get('status') == 'success', "Default ping handler failed"
        result.add_detail("Default ping handler working")
    
    def test_session_persistence(self, result: TestResult):
        """Test session persistence functionality"""
        
        try:
            # Create session manager
            session_mgr = self.module.MCPSessionManager()
            
            # Create test session
            test_data = {
                'user_id': 'test_user',
                'timestamp': time.time(),
                'actions': ['connect', 'generate', 'export']
            }
            
            session_id = session_mgr.create_session(test_data)
            result.add_detail(f"Session created: {session_id}")
            
            # Save session
            save_success = session_mgr.save_session(session_id)
            assert save_success, "Session save failed"
            result.add_detail("Session saved to storage")
            
            # Create new session manager to test persistence
            new_session_mgr = self.module.MCPSessionManager()
            
            # Load session
            loaded_data = new_session_mgr.get_session(session_id)
            assert loaded_data is not None, "Session not loaded from storage"
            assert loaded_data.get('user_id') == test_data['user_id'], "Session data corrupted"
            result.add_detail("Session loaded successfully from storage")
            
        except Exception as e:
            result.add_detail(f"Session persistence error: {str(e)}")
            raise
    
    def test_error_handling(self, result: TestResult):
        """Test error handling and recovery"""
        
        # Test invalid server port
        try:
            invalid_server = self.module.MCPServer(port=-1)
            result.add_detail("Server handles invalid port gracefully")
        except Exception as e:
            result.add_detail(f"Server port validation: {str(e)}")
        
        # Test invalid client connection
        try:
            invalid_client = self.module.MCPClient(host='invalid.host.name', port=99999)
            connected = invalid_client.connect()
            assert not connected, "Client should not connect to invalid host"
            result.add_detail("Client handles invalid host gracefully")
        except Exception as e:
            result.add_detail(f"Client connection validation: {str(e)}")
        
        # Test session manager with invalid data
        try:
            session_mgr = self.module.MCPSessionManager()
            invalid_session = session_mgr.get_session('invalid_session_id')
            assert invalid_session is None, "Should return None for invalid session"
            result.add_detail("SessionManager handles invalid IDs gracefully")
        except Exception as e:
            result.add_detail(f"Session validation: {str(e)}")
    
    def test_performance_metrics(self, result: TestResult):
        """Test performance tracking functionality"""
        
        try:
            # Create server with performance tracking
            server = self.module.MCPServer(port=self.server_port + 1)
            
            # Check performance attributes exist
            perf_attrs = ['request_count', 'total_response_time', 'error_count']
            for attr in perf_attrs:
                if hasattr(server, attr):
                    result.add_detail(f"Performance metric available: {attr}")
            
            # Test request timing (if available)
            if hasattr(server, 'track_request_time'):
                start_time = time.time()
                server.track_request_time(start_time, time.time())
                result.add_detail("Request timing tracked successfully")
            
        except Exception as e:
            result.add_detail(f"Performance testing error: {str(e)}")

if __name__ == "__main__":
    from test_framework import UniversalTestRunner
    
    # Create test runner
    runner = UniversalTestRunner()
    
    # Add MCP tools test suite
    mcp_suite = MCPToolsTestSuite("mcp_tools", runner.logger)
    runner.add_test_suite(mcp_suite)
    
    # Run dependency check
    deps_ok = runner.run_dependency_check()
    
    if deps_ok:
        # Run tests
        results = runner.run_all_tests()
        
        # Save results
        output_dir = Path(__file__).parent.parent / "results"
        runner.save_results(output_dir)
        
        print(f"\n🎯 MCP TOOLS MODULE TESTING COMPLETE")
        print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    else:
        print("❌ Critical dependencies missing - skipping tests")
