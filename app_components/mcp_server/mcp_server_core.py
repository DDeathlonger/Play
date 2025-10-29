"""
Shared MCP Server Component - Singleton Service Provider

This module provides a centralized, thread-safe MCP (Model Context Protocol) server
that can be shared across multiple components and applications. It follows the 
singleton pattern to ensure only one server instance exists while providing
services to multiple consumers.

Key Design Principles:
- Modularity: Clean separation from any specific application
- Abstraction: Service layer pattern for different endpoint types  
- Rigidity: Thread-safe operations and robust error handling
- Extensibility: Plugin-style service registration system

Architecture:
- MCPServerCore: Main singleton server with HTTP handling
- MCPServiceRegistry: Service registration and routing system
- MCPServiceBase: Abstract base class for service implementations
- Thread-safe operations with proper Qt integration where needed

Usage:
    server = MCPServerCore.get_instance()
    server.register_service('/memory', MemoryService())
    server.start(port=8765)
"""

import json
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Dict, Any, Optional, Callable, List
import traceback


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Thread-safe HTTP server with proper cleanup"""
    daemon_threads = True
    allow_reuse_address = True


class MCPServiceBase(ABC):
    """
    Abstract base class for MCP service implementations.
    
    All MCP services must inherit from this class and implement the required methods.
    This ensures consistent service interface and proper error handling.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.is_initialized = False
        
    @abstractmethod
    def handle_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET requests for this service"""
        pass
        
    @abstractmethod
    def handle_post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POST requests for this service"""  
        pass
        
    @abstractmethod
    def get_health_info(self) -> Dict[str, Any]:
        """Return service health information"""
        pass
        
    def initialize(self) -> bool:
        """Initialize service resources - called once on registration"""
        self.is_initialized = True
        return True
        
    def cleanup(self) -> None:
        """Cleanup service resources - called on server shutdown"""
        self.is_initialized = False


class MCPServiceRegistry:
    """
    Service registration and routing system for MCP endpoints.
    
    Manages registration of services and routes requests to appropriate handlers.
    Provides thread-safe access to service instances and maintains service health.
    """
    
    def __init__(self):
        self._services: Dict[str, MCPServiceBase] = {}
        self._service_lock = threading.RLock()
        self._request_counts: Dict[str, int] = {}
        
    def register_service(self, path_prefix: str, service: MCPServiceBase) -> bool:
        """
        Register a new service with the MCP server.
        
        Args:
            path_prefix: URL path prefix for this service (e.g., '/memory', '/ui')
            service: Service instance implementing MCPServiceBase
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        with self._service_lock:
            try:
                if path_prefix in self._services:
                    print(f"⚠️ Service {path_prefix} already registered, replacing...")
                    
                if service.initialize():
                    self._services[path_prefix] = service
                    self._request_counts[path_prefix] = 0
                    print(f"✅ Service registered: {path_prefix} -> {service.service_name}")
                    return True
                else:
                    print(f"❌ Service initialization failed: {path_prefix}")
                    return False
                    
            except Exception as e:
                print(f"❌ Service registration error for {path_prefix}: {e}")
                return False
                
    def unregister_service(self, path_prefix: str) -> bool:
        """Unregister a service and cleanup its resources"""
        with self._service_lock:
            try:
                if path_prefix in self._services:
                    service = self._services[path_prefix]
                    service.cleanup()
                    del self._services[path_prefix]
                    del self._request_counts[path_prefix]
                    print(f"✅ Service unregistered: {path_prefix}")
                    return True
                return False
            except Exception as e:
                print(f"❌ Service unregistration error for {path_prefix}: {e}")
                return False
                
    def route_request(self, method: str, path: str, params: Dict[str, Any] = None, 
                     data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route incoming requests to appropriate service handlers.
        
        Args:
            method: HTTP method (GET/POST)
            path: Request path
            params: Query parameters (for GET)
            data: Request body data (for POST)
            
        Returns:
            Dict containing response data or error information
        """
        with self._service_lock:
            try:
                # Find matching service by path prefix (longest match first)
                service = None
                service_path = ""
                best_match_length = -1
                
                for prefix, svc in self._services.items():
                    if path.startswith(prefix) and len(prefix) > best_match_length:
                        service = svc
                        service_path = prefix
                        best_match_length = len(prefix)
                        
                if not service:
                    return {
                        'error': 'No service found for path',
                        'path': path,
                        'available_services': list(self._services.keys())
                    }
                    
                # Update request count
                self._request_counts[service_path] += 1
                
                # Calculate relative path for the service
                relative_path = path[len(service_path):] if service_path else path
                if not relative_path.startswith('/'):
                    relative_path = '/' + relative_path
                
                # Route to appropriate handler
                if method == 'GET':
                    return service.handle_get(relative_path, params or {})
                elif method == 'POST':
                    return service.handle_post(relative_path, data or {})
                else:
                    return {'error': f'Unsupported method: {method}'}
                    
            except Exception as e:
                return {
                    'error': 'Service routing error',
                    'details': str(e),
                    'traceback': traceback.format_exc()
                }
                
    def get_registry_status(self) -> Dict[str, Any]:
        """Get status of all registered services"""
        with self._service_lock:
            status = {
                'total_services': len(self._services),
                'services': {},
                'request_counts': self._request_counts.copy()
            }
            
            for path, service in self._services.items():
                try:
                    service_health = service.get_health_info()
                    status['services'][path] = {
                        'name': service.service_name,
                        'initialized': service.is_initialized,
                        'health': service_health,
                        'requests': self._request_counts.get(path, 0)
                    }
                except Exception as e:
                    status['services'][path] = {
                        'name': service.service_name,
                        'initialized': service.is_initialized,
                        'health': {'error': str(e)},
                        'requests': self._request_counts.get(path, 0)
                    }
                    
            return status


class MCPServerCore:
    """
    Singleton MCP Server Core with thread-safe HTTP handling.
    
    Provides centralized MCP server functionality that can serve multiple
    applications and components. Maintains singleton pattern to ensure
    only one server instance exists across the entire application.
    
    Features:
    - Singleton pattern for shared server instance
    - Thread-safe service registration and request handling
    - Automatic port conflict resolution
    - Graceful shutdown and cleanup
    - Health monitoring and status reporting
    - Integration with existing Qt applications
    """
    
    _instance = None
    _instance_lock = threading.Lock()
    
    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
            
    def __init__(self):
        if self._initialized:
            return
            
        self.port = 8765
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.start_time = None
        
        # Service registry for routing requests
        self.registry = MCPServiceRegistry()
        
        # Server statistics
        self.total_requests = 0
        self.server_lock = threading.RLock()
        
        self._initialized = True
        
    @classmethod 
    def get_instance(cls) -> 'MCPServerCore':
        """Get singleton instance of MCP server"""
        return cls()
        
    def start(self, port: int = 8765, host: str = '127.0.0.1') -> bool:
        """
        Start the MCP server with service registry support.
        
        Args:
            port: Port number to bind to (default 8765)
            host: Host address to bind to (default all interfaces)
            
        Returns:
            bool: True if server started successfully
        """
        with self.server_lock:
            if self.is_running:
                print(f"⚠️ MCP Server already running on port {self.port}")
                return True
                
            try:
                self.port = self._find_available_port(port)
                if not self.port:
                    print(f"❌ No available ports found starting from {port}")
                    return False
                    
                # Create HTTP server with custom handler
                class MCPRequestHandler(BaseHTTPRequestHandler):
                    def __init__(self, server_core, *args, **kwargs):
                        self.server_core = server_core
                        super().__init__(*args, **kwargs)
                        
                    def log_message(self, format, *args):
                        """Suppress default HTTP server logging"""
                        pass
                        
                    def do_GET(self):
                        self.server_core._handle_request('GET', self)
                        
                    def do_POST(self):
                        self.server_core._handle_request('POST', self)
                        
                    def do_OPTIONS(self):
                        """Handle CORS preflight requests"""
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                        self.end_headers()
                
                # Create server with bound handler
                def handler(*args, **kwargs):
                    return MCPRequestHandler(self, *args, **kwargs)
                
                print(f"🔧 Creating server on {host}:{self.port}")
                self.server = ThreadedHTTPServer((host, self.port), handler)
                self.server.allow_reuse_address = True
                print(f"🔧 Server created, starting thread...")
                
                # Start server in background thread
                def server_runner():
                    try:
                        print(f"🔧 Server thread starting on {host}:{self.port}")
                        self.server.serve_forever()
                    except Exception as e:
                        print(f"❌ Server thread error: {e}")
                        import traceback
                        traceback.print_exc()
                        
                self.server_thread = threading.Thread(
                    target=server_runner,
                    daemon=True,
                    name=f"MCPServer-{self.port}"
                )
                
                self.server_thread.start()
                
                # Wait a moment for thread to start and verify socket
                time.sleep(0.2)
                
                # Test socket connectivity
                try:
                    import socket
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.settimeout(1)
                    result = test_socket.connect_ex((host, self.port))
                    test_socket.close()
                    if result == 0:
                        print(f"✅ Socket verification: Port {self.port} is accessible")
                    else:
                        print(f"⚠️ Socket verification: Port {self.port} connection failed (code {result})")
                except Exception as e:
                    print(f"⚠️ Socket verification error: {e}")
                
                self.is_running = True
                self.start_time = time.time()
                
                print(f"🚀 Shared MCP Server started on http://{host}:{self.port}")
                print(f"📡 Service registry ready for endpoint registration")
                print(f"🔧 Server thread active: {self.server_thread.is_alive()}")
                
                return True
                
            except Exception as e:
                print(f"❌ Failed to start MCP server: {e}")
                traceback.print_exc()
                return False
                
    def stop(self) -> None:
        """Stop the MCP server and cleanup all services"""
        with self.server_lock:
            if not self.is_running:
                return
                
            try:
                print("🛑 Stopping shared MCP server...")
                
                # Cleanup all registered services
                for path in list(self.registry._services.keys()):
                    self.registry.unregister_service(path)
                
                # Stop HTTP server
                if self.server:
                    self.server.shutdown()
                    self.server.server_close()
                    
                # Wait for server thread
                if self.server_thread and self.server_thread.is_alive():
                    self.server_thread.join(timeout=3)
                    
                self.is_running = False
                self.server = None
                self.server_thread = None
                
                print("✅ Shared MCP server stopped successfully")
                
            except Exception as e:
                print(f"⚠️ MCP server shutdown error: {e}")
                
    def register_service(self, path_prefix: str, service: MCPServiceBase) -> bool:
        """Register a service with the MCP server"""
        return self.registry.register_service(path_prefix, service)
        
    def unregister_service(self, path_prefix: str) -> bool:
        """Unregister a service from the MCP server"""
        return self.registry.unregister_service(path_prefix)
        
    def get_server_status(self) -> Dict[str, Any]:
        """Get comprehensive server status including all services"""
        with self.server_lock:
            uptime = time.time() - self.start_time if self.start_time else 0
            
            return {
                'server': {
                    'running': self.is_running,
                    'port': self.port,
                    'uptime_seconds': uptime,
                    'total_requests': self.total_requests,
                    'thread_name': self.server_thread.name if self.server_thread else None
                },
                'registry': self.registry.get_registry_status(),
                'timestamp': datetime.now().isoformat()
            }
            
    def _handle_request(self, method: str, handler: BaseHTTPRequestHandler) -> None:
        """Handle incoming HTTP requests and route to services"""
        try:
            self.total_requests += 1
            
            # Parse request
            path = handler.path
            params = {}
            data = {}
            
            # Handle POST data
            if method == 'POST':
                try:
                    content_length = int(handler.headers.get('Content-Length', 0))
                    if content_length > 0:
                        post_data = handler.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                except Exception as e:
                    print(f"⚠️ POST data parsing error: {e}")
            
            # Built-in endpoints
            if path == '/health':
                response = {'status': 'healthy', 'timestamp': time.time()}
            elif path == '/status':
                response = self.get_server_status()
            elif path == '/services':
                response = self.registry.get_registry_status()
            else:
                # Route to registered services
                response = self.registry.route_request(method, path, params, data)
            
            # Send response
            handler.send_response(200)
            handler.send_header('Content-Type', 'application/json')
            handler.send_header('Access-Control-Allow-Origin', '*')
            handler.end_headers()
            
            response_json = json.dumps(response, indent=2)
            handler.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Request handling error: {e}")
            try:
                handler.send_response(500)
                handler.send_header('Content-Type', 'application/json')
                handler.send_header('Access-Control-Allow-Origin', '*')
                handler.end_headers()
                
                error_response = {
                    'error': 'Internal server error',
                    'details': str(e),
                    'timestamp': time.time()
                }
                handler.wfile.write(json.dumps(error_response).encode('utf-8'))
            except:
                pass  # Can't send error response
                
    def _find_available_port(self, start_port: int) -> Optional[int]:
        """Find an available port starting from start_port"""
        import socket
        
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        return None


# Convenience functions for easy service management
def get_mcp_server() -> MCPServerCore:
    """Get the singleton MCP server instance"""
    return MCPServerCore.get_instance()

def start_mcp_server(port: int = 8765) -> bool:
    """Start the shared MCP server on specified port"""
    return get_mcp_server().start(port)

def register_mcp_service(path: str, service: MCPServiceBase) -> bool:
    """Register a service with the shared MCP server"""
    return get_mcp_server().register_service(path, service)

def stop_mcp_server() -> None:
    """Stop the shared MCP server and cleanup all services"""
    get_mcp_server().stop()