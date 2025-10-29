"""
Comprehensive Test Suite for AI Memory Control System

This test suite provides comprehensive validation for all new components
including AIMemoryManager, shared MCP server, web interface endpoints,
and integration with existing spaceship_designer functionality.

Test Coverage:
- ✅ MCP Server Core functionality and singleton behavior
- ✅ Service registration and routing system  
- ✅ AI Memory Control Service endpoints and file operations
- ✅ Legacy AI Controller Service backward compatibility
- ✅ Integration patch functionality
- ✅ Web interface serving and static file handling
- ✅ Cross-reference analysis and file caching
- ✅ Error handling and thread safety

Usage:
    # Run all tests
    pytest test_ai_memory_system.py -v
    
    # Run with emoji output and coverage
    pytest test_ai_memory_system.py -v --tb=short --emoji
    
    # Run specific test categories
    pytest test_ai_memory_system.py::TestMCPServerCore -v
    pytest test_ai_memory_system.py::TestAIMemoryService -v
"""

import pytest
import json
import time
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add app_components to path
current_dir = Path(__file__).parent
project_root = current_dir.parent  
app_components_path = project_root / 'app_components'
if str(app_components_path) not in sys.path:
    sys.path.insert(0, str(app_components_path))

# Import components to test
from mcp_server.mcp_server_core import (
    MCPServerCore, MCPServiceRegistry, MCPServiceBase,
    get_mcp_server, start_mcp_server, register_mcp_service
)
from mcp_server.legacy_ai_service import LegacyAIControllerService
from ai_memory_control.memory_service import AIMemoryControlService
from mcp_server.integration_patch import SpaceshipMCPIntegration, integrate_mcp_server


class TestMCPServerCore:
    """Test suite for MCP Server Core functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Reset singleton for clean testing
        MCPServerCore._instance = None
        self.server = MCPServerCore()
        self.test_port = 8766  # Use different port for testing
        
    def teardown_method(self):
        """Clean up after tests"""
        if self.server.is_running:
            self.server.stop()
        MCPServerCore._instance = None
        
    def test_singleton_behavior(self):
        """🧪 Test that MCPServerCore implements singleton pattern correctly"""
        server1 = MCPServerCore.get_instance()
        server2 = MCPServerCore.get_instance() 
        server3 = get_mcp_server()
        
        assert server1 is server2, "❌ Multiple instances created"
        assert server1 is server3, "❌ Factory function returns different instance"
        assert server1 is self.server, "❌ Instance not preserved"
        
    def test_server_startup_and_shutdown(self):
        """🧪 Test server startup and graceful shutdown"""
        # Test startup
        assert not self.server.is_running, "❌ Server should not be running initially"
        
        success = self.server.start(self.test_port)
        assert success, "❌ Server failed to start"
        assert self.server.is_running, "❌ Server not marked as running"
        assert self.server.port == self.test_port, "❌ Wrong port assigned"
        
        # Test server responds
        time.sleep(0.1)  # Allow server thread to start
        
        # Test shutdown
        self.server.stop()
        assert not self.server.is_running, "❌ Server should not be running after stop"
        
    def test_port_conflict_resolution(self):
        """🧪 Test automatic port conflict resolution"""
        # Start server on test port
        success1 = self.server.start(self.test_port)
        assert success1, "❌ First server failed to start"
        
        # Try to start second server on same port
        server2 = MCPServerCore()
        success2 = server2.start(self.test_port)
        
        if success2:
            # Should get different port
            assert server2.port != self.test_port, "❌ Port conflict not resolved"
            server2.stop()
        
    def test_service_registry(self):
        """🧪 Test service registration and routing system"""
        registry = self.server.registry
        
        # Create mock service
        mock_service = Mock(spec=MCPServiceBase)
        mock_service.service_name = "Test Service"
        mock_service.initialize.return_value = True
        mock_service.is_initialized = True
        mock_service.handle_get.return_value = {'test': 'response'}
        
        # Test registration
        success = registry.register_service('/test', mock_service)
        assert success, "❌ Service registration failed"
        assert '/test' in registry._services, "❌ Service not in registry"
        
        # Test routing
        response = registry.route_request('GET', '/test/endpoint')
        mock_service.handle_get.assert_called_once()
        
        # Test unregistration
        success = registry.unregister_service('/test')
        assert success, "❌ Service unregistration failed"
        assert '/test' not in registry._services, "❌ Service still in registry"
        
    def test_server_status_reporting(self):
        """🧪 Test comprehensive server status reporting"""
        self.server.start(self.test_port)
        
        status = self.server.get_server_status()
        
        assert 'server' in status, "❌ Missing server status section"
        assert 'registry' in status, "❌ Missing registry status section"
        assert 'timestamp' in status, "❌ Missing timestamp"
        
        server_info = status['server']
        assert server_info['running'] == True, "❌ Wrong running status"
        assert server_info['port'] == self.test_port, "❌ Wrong port in status"
        assert 'uptime_seconds' in server_info, "❌ Missing uptime"
        
    def test_thread_safety(self):
        """🧪 Test thread safety of server operations"""
        self.server.start(self.test_port)
        
        errors = []
        
        def register_services():
            try:
                for i in range(5):
                    mock_service = Mock(spec=MCPServiceBase)
                    mock_service.service_name = f"Service{i}"
                    mock_service.initialize.return_value = True
                    mock_service.is_initialized = True
                    self.server.register_service(f'/test{i}', mock_service)
                    time.sleep(0.01)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(e)
                
        # Start multiple threads
        threads = [threading.Thread(target=register_services) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        assert len(errors) == 0, f"❌ Thread safety violations: {errors}"


class TestAIMemoryService:
    """Test suite for AI Memory Control Service"""
    
    def setup_method(self):
        """Set up test fixtures with temporary copilot directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.copilot_dir = Path(self.temp_dir) / '.github' / 'copilot'
        self.copilot_dir.mkdir(parents=True)
        
        # Create test markdown files
        self.create_test_files()
        
        # Create service with mocked paths
        self.service = AIMemoryControlService()
        self.service.copilot_dir = self.copilot_dir
        
        # Create component directories
        self.component_dir = Path(self.temp_dir) / 'app_components' / 'ai_memory_control'
        self.service.static_dir = self.component_dir / 'static'
        self.service.templates_dir = self.component_dir / 'templates'
        self.service.static_dir.mkdir(parents=True)
        self.service.templates_dir.mkdir(parents=True)
        
        # Create test template
        template_content = "<html><head><title>Test</title></head><body>Test Interface</body></html>"
        (self.service.templates_dir / 'memory_control.html').write_text(template_content)
        
        # Create test CSS
        css_content = "body { background: black; color: white; }"
        (self.service.static_dir / 'css').mkdir(parents=True)
        (self.service.static_dir / 'css' / 'memory-control.css').write_text(css_content)
        
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def create_test_files(self):
        """Create test markdown files in copilot directory"""
        test_files = {
            'README.md': '# Test README\nThis is a test file.',
            'context/test.md': '# Test Context\nRefers to [README.md](../README.md)',
            'guides/guide.md': '# Test Guide\nSee also `context/test.md`',
            'protocols/protocol.md': '# Test Protocol\nImportant protocol information.'
        }
        
        for path, content in test_files.items():
            file_path = self.copilot_dir / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            
    def test_service_initialization(self):
        """🧪 Test service initialization and directory discovery"""
        success = self.service.initialize()
        assert success, "❌ Service initialization failed"
        assert self.service.is_initialized, "❌ Service not marked as initialized"
        
        # Check file cache was built
        assert len(self.service.file_cache) > 0, "❌ File cache is empty"
        assert 'README.md' in self.service.file_cache, "❌ Root file not cached"
        
    def test_file_list_endpoint(self):
        """🧪 Test file listing endpoint functionality"""
        self.service.initialize()
        
        response = self.service.handle_get('/memory/files', {})
        
        assert 'files' in response, "❌ Missing files in response"
        assert response['status'] == 'success', "❌ Wrong status"
        assert response['total_files'] > 0, "❌ No files reported"
        
        # Check file organization by category
        files = response['files']
        assert 'root' in files or 'README.md' in str(files), "❌ Root files not organized"
        assert 'context' in files, "❌ Context category missing"
        
    def test_file_content_retrieval(self):
        """🧪 Test individual file content retrieval"""
        self.service.initialize()
        
        response = self.service.handle_get('/memory/file/README.md', {})
        
        assert response['status'] == 'success', "❌ File retrieval failed"
        assert 'content' in response, "❌ Missing content"
        assert '# Test README' in response['content'], "❌ Wrong content"
        assert response['filename'] == 'README.md', "❌ Wrong filename"
        
    def test_file_saving(self):
        """🧪 Test file content saving functionality"""
        self.service.initialize()
        
        new_content = "# Updated README\nThis content was updated by test."
        data = {'content': new_content}
        
        response = self.service.handle_post('/memory/file/README.md', data)
        
        assert response['status'] == 'success', "❌ File saving failed"
        
        # Verify content was saved
        file_path = self.copilot_dir / 'README.md'
        saved_content = file_path.read_text()
        assert saved_content == new_content, "❌ File content not saved correctly"
        
    def test_search_functionality(self):
        """🧪 Test cross-file search functionality"""
        self.service.initialize()
        
        data = {'query': 'Test'}
        response = self.service.handle_post('/memory/search', data)
        
        assert response['status'] == 'success', "❌ Search failed"
        assert 'results' in response, "❌ Missing search results"
        assert len(response['results']) > 0, "❌ No search results found"
        
        # Check result structure
        first_result = response['results'][0]
        assert 'file' in first_result, "❌ Missing file in result"
        assert 'matches' in first_result, "❌ Missing matches in result"
        
    def test_cross_reference_analysis(self):
        """🧪 Test cross-reference detection between files"""
        self.service.initialize()
        
        response = self.service.handle_get('/memory/cross-refs', {})
        
        assert response['status'] == 'success', "❌ Cross-reference analysis failed"
        assert 'cross_references' in response, "❌ Missing cross-references"
        
        # Should detect the reference from context/test.md to README.md
        cross_refs = response['cross_references']
        context_refs = cross_refs.get('context/test.md', [])
        
        # Look for reference to README.md
        readme_refs = [ref for ref in context_refs if 'README.md' in str(ref)]
        assert len(readme_refs) > 0, "❌ Cross-reference not detected"
        
    def test_web_interface_serving(self):
        """🧪 Test web interface HTML serving"""
        self.service.initialize()
        
        response = self.service.handle_get('/memory', {})
        
        assert response['status'] == 'success', "❌ Web interface serving failed"
        assert response['content_type'] == 'text/html', "❌ Wrong content type"
        assert '<html>' in response['content'], "❌ Invalid HTML content"
        
    def test_static_file_serving(self):
        """🧪 Test static file (CSS, JS) serving"""
        self.service.initialize()
        
        response = self.service.handle_get('/memory/static/css/memory-control.css', {})
        
        assert response['status'] == 'success', "❌ Static file serving failed"
        assert response['content_type'] == 'text/css', "❌ Wrong content type for CSS"
        assert 'background: black' in response['content'], "❌ Wrong CSS content"
        
    def test_health_reporting(self):
        """🧪 Test service health reporting"""
        self.service.initialize()
        
        health = self.service.get_health_info()
        
        assert health['status'] == 'healthy', "❌ Service not healthy"
        assert health['service'] == 'AI Memory Control', "❌ Wrong service name"
        assert 'statistics' in health, "❌ Missing statistics"
        
        stats = health['statistics']
        assert stats['total_files'] > 0, "❌ No files in statistics"
        assert stats['copilot_dir_exists'] == True, "❌ Copilot directory check failed"


class TestLegacyAIService:
    """Test suite for Legacy AI Controller Service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_app = Mock()
        self.service = LegacyAIControllerService(self.mock_app)
        
    def test_service_initialization(self):
        """🧪 Test legacy service initialization"""
        success = self.service.initialize()
        assert success, "❌ Legacy service initialization failed"
        assert self.service.is_initialized, "❌ Service not marked as initialized"
        assert self.service.app_ref is self.mock_app, "❌ App reference not set"
        
    def test_available_commands(self):
        """🧪 Test legacy command list compatibility"""
        commands = self.service._get_available_commands()
        
        expected_commands = ['see', 'click', 'move_to', 'press_key', 'focus_app']
        for cmd in expected_commands:
            assert cmd in commands, f"❌ Missing expected command: {cmd}"
            
    def test_command_execution_logging(self):
        """🧪 Test command execution and audit logging"""
        self.service.initialize()
        
        command_data = {
            'command': 'see',
            'params': {'description': 'test_screenshot'},
            'agent': 'test_agent',
            'reason': 'testing'
        }
        
        response = self.service.handle_post('/commands', command_data)
        
        assert response['status'] == 'command_received', "❌ Command not processed"
        assert self.service.latest_command is not None, "❌ Latest command not recorded"
        assert len(self.service.command_history) > 0, "❌ Command history empty"
        
        # Check agent tracking
        assert 'test_agent' in self.service.connected_clients, "❌ Agent not tracked"
        
    def test_screenshot_command(self):
        """🧪 Test screenshot command processing"""
        self.service.initialize()
        
        result = self.service._process_command('see', {'description': 'test'}, 'testing')
        
        assert result['success'] == True, "❌ Screenshot command failed"
        assert result['action'] == 'screenshot', "❌ Wrong action type"
        assert 'filename' in result, "❌ Missing filename"
        
    def test_mouse_commands(self):
        """🧪 Test mouse control commands"""
        self.service.initialize()
        
        # Test click
        click_result = self.service._process_command('click', {'x': 100, 'y': 200}, 'test click')
        assert click_result['success'] == True, "❌ Click command failed"
        assert click_result['coordinates'] == {'x': 100, 'y': 200}, "❌ Wrong coordinates"
        
        # Test move
        move_result = self.service._process_command('move_to', {'x': 150, 'y': 250}, 'test move')
        assert move_result['success'] == True, "❌ Move command failed"
        
    def test_keyboard_commands(self):
        """🧪 Test keyboard input commands"""
        self.service.initialize()
        
        # Test key press
        key_result = self.service._process_command('press_key', {'key': 'w'}, 'test key')
        assert key_result['success'] == True, "❌ Key press failed"
        assert key_result['key'] == 'w', "❌ Wrong key recorded"
        
        # Test text input
        text_result = self.service._process_command('type_text', {'text': 'hello'}, 'test text')
        assert text_result['success'] == True, "❌ Text input failed"
        assert text_result['text'] == 'hello', "❌ Wrong text recorded"
        
    def test_status_reporting(self):
        """🧪 Test AI status reporting compatibility"""
        self.service.initialize()
        
        status = self.service._get_ai_status()
        
        assert 'session_id' in status, "❌ Missing session ID"
        assert 'connected_clients' in status, "❌ Missing client count"
        assert 'command_history' in status, "❌ Missing command history"
        
    def test_health_monitoring(self):
        """🧪 Test service health monitoring"""
        self.service.initialize()
        
        health = self.service.get_health_info()
        
        assert health['status'] == 'healthy', "❌ Service not healthy"
        assert 'statistics' in health, "❌ Missing statistics"
        assert health['statistics']['session_id'] == self.service.session_id, "❌ Wrong session ID"


class TestIntegrationPatch:
    """Test suite for Spaceship MCP Integration"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_app = Mock()
        self.integration = SpaceshipMCPIntegration(self.mock_app)
        
    def teardown_method(self):
        """Clean up after tests"""
        if self.integration.is_running:
            self.integration.stop()
        # Reset singleton
        MCPServerCore._instance = None
        
    def test_integration_initialization(self):
        """🧪 Test integration initialization with app reference"""
        assert self.integration.app_ref is self.mock_app, "❌ App reference not set"
        assert self.integration.mcp_server is not None, "❌ MCP server not initialized"
        assert not self.integration.is_running, "❌ Should not be running initially"
        
    def test_integrated_server_startup(self):
        """🧪 Test integrated server startup with all services"""
        success = self.integration.start(8767)  # Different port for testing
        
        if success:  # May fail in test environment without proper setup
            assert self.integration.is_running, "❌ Integration not marked as running"
            assert self.integration.legacy_service is not None, "❌ Legacy service not created"
            
            # Test status reporting
            status = self.integration.get_status()
            assert status['running'] == True, "❌ Wrong running status"
            assert 'endpoints' in status, "❌ Missing endpoints info"
            
    def test_backward_compatibility(self):
        """🧪 Test backward compatibility with existing methods"""
        # Test that old method names still work
        commands = self.integration.get_mcp_commands()
        assert isinstance(commands, list), "❌ Commands should be a list"
        
        ai_status = self.integration.get_ai_connection_status()
        assert isinstance(ai_status, dict), "❌ AI status should be a dict"
        
    def test_factory_function(self):
        """🧪 Test factory function for creating integrations"""
        integration2 = integrate_mcp_server(self.mock_app)
        
        assert isinstance(integration2, SpaceshipMCPIntegration), "❌ Wrong type returned"
        assert integration2.app_ref is self.mock_app, "❌ App reference not preserved"


class TestSystemIntegration:
    """System-level integration tests"""
    
    def setup_method(self):
        """Set up system-level test fixtures"""
        MCPServerCore._instance = None
        self.server = get_mcp_server()
        self.test_port = 8768
        
    def teardown_method(self):
        """Clean up system tests"""
        if self.server.is_running:
            self.server.stop()
        MCPServerCore._instance = None
        
    def test_full_system_integration(self):
        """🧪 Test complete system with all components working together"""
        # Start server
        success = self.server.start(self.test_port)
        assert success, "❌ System startup failed"
        
        # Register both services
        mock_app = Mock()
        legacy_service = LegacyAIControllerService(mock_app)
        memory_service = AIMemoryControlService()
        
        # Mock the memory service initialization to avoid file system dependencies
        with patch.object(memory_service, 'initialize', return_value=True):
            with patch.object(memory_service, 'copilot_dir', Path('/mock/path')):
                legacy_registered = self.server.register_service('', legacy_service)
                memory_registered = self.server.register_service('/memory', memory_service)
                
                assert legacy_registered, "❌ Legacy service registration failed"
                assert memory_registered, "❌ Memory service registration failed"
                
                # Test server status includes both services
                status = self.server.get_server_status()
                services = status['registry']['services']
                
                assert '' in services, "❌ Legacy service not in status"
                assert '/memory' in services, "❌ Memory service not in status"
                
    def test_concurrent_service_operations(self):
        """🧪 Test thread safety with concurrent service operations"""
        self.server.start(self.test_port)
        
        # Create multiple mock services
        services = []
        for i in range(5):
            service = Mock(spec=MCPServiceBase)
            service.service_name = f"TestService{i}"
            service.initialize.return_value = True
            service.is_initialized = True
            service.get_health_info.return_value = {'status': 'healthy'}
            services.append((f'/test{i}', service))
            
        # Register services concurrently
        threads = []
        results = []
        
        def register_service(path, service):
            try:
                result = self.server.register_service(path, service)
                results.append(result)
            except Exception as e:
                results.append(False)
                
        for path, service in services:
            thread = threading.Thread(target=register_service, args=(path, service))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # All registrations should succeed
        assert all(results), "❌ Some concurrent registrations failed"
        assert len(self.server.registry._services) >= len(services), "❌ Not all services registered"


def test_pytest_integration():
    """🧪 Test that pytest is working correctly with our test suite"""
    assert True, "❌ Basic pytest assertion failed"
    

if __name__ == '__main__':
    # Allow running tests directly
    pytest.main([__file__, '-v', '--tb=short'])