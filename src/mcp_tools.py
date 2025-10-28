#!/usr/bin/env python3
"""
MCP TOOLS AND UTILITIES - ISOLATED MODULE
Model Context Protocol server management and communication tools
"""

import json
import time
import threading
import subprocess
import socket
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

class MCPCommandHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP commands with callback support"""
    
    def __init__(self, callback_registry: Dict[str, Callable], *args, **kwargs):
        self.callback_registry = callback_registry
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests with command routing"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            command_data = json.loads(post_data.decode('utf-8'))
            
            # Route command to appropriate handler
            action = command_data.get('action', 'unknown')
            if action in self.callback_registry:
                response = self.callback_registry[action](command_data)
            else:
                response = {'status': 'error', 'message': f'Unknown action: {action}'}
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Command processing error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests for status"""
        if self.path == '/status':
            response = {'status': 'running', 'timestamp': datetime.now().isoformat()}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Not found")
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class MCPSessionManager:
    """Manages persistent MCP sessions with performance tracking"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.command_history = []
        self.max_history = 100
        self.performance_metrics = {
            'commands_processed': 0,
            'session_start_time': time.time(),
            'average_response_time': 0.0,
            'total_response_time': 0.0
        }
        self.active_connections = set()
    
    def add_command(self, command_data: Dict[str, Any], processing_time: float = 0.0):
        """Add command to history with performance tracking"""
        self.command_history.append({
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'command': command_data,
            'processing_time': processing_time
        })
        
        # Maintain history size
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        # Update metrics
        self.performance_metrics['commands_processed'] += 1
        self.performance_metrics['total_response_time'] += processing_time
        if self.performance_metrics['commands_processed'] > 0:
            self.performance_metrics['average_response_time'] = (
                self.performance_metrics['total_response_time'] / 
                self.performance_metrics['commands_processed']
            )
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information"""
        uptime = time.time() - self.performance_metrics['session_start_time']
        return {
            'session_id': self.session_id,
            'uptime_seconds': uptime,
            'commands_processed': self.performance_metrics['commands_processed'],
            'average_response_time': self.performance_metrics['average_response_time'],
            'command_rate': self.performance_metrics['commands_processed'] / max(1, uptime / 60),
            'recent_commands': self.command_history[-5:] if self.command_history else [],
            'active_connections': len(self.active_connections)
        }
    
    def get_recent_commands(self, count: int = 3) -> List[str]:
        """Get recent command summaries for display"""
        recent = []
        for cmd in self.command_history[-count:]:
            action = cmd['command'].get('action', 'Unknown')
            timestamp = cmd['timestamp'].split('T')[1][:8]  # HH:MM:SS
            recent.append(f"[{timestamp}] {action}")
        return recent

class MCPNetworkManager:
    """Manages MCP network operations and conflict resolution"""
    
    @staticmethod
    def find_available_port(start_port: int = 8765, max_attempts: int = 10) -> int:
        """Find available port with conflict resolution"""
        for i in range(max_attempts):
            port = start_port + i
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise Exception(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")
    
    @staticmethod
    def check_existing_servers() -> List[int]:
        """Check for existing MCP servers"""
        existing_servers = []
        for port in range(8765, 8775):
            try:
                response = requests.get(f'http://localhost:{port}/status', timeout=1)
                if response.status_code == 200:
                    existing_servers.append(port)
            except:
                continue
        return existing_servers
    
    @staticmethod
    def test_server_connection(port: int) -> bool:
        """Test if server is responsive on given port"""
        try:
            response = requests.get(f'http://localhost:{port}/status', timeout=2)
            return response.status_code == 200
        except:
            return False

class MCPServer:
    """Isolated MCP server with session persistence and conflict resolution"""
    
    def __init__(self, callback_registry: Optional[Dict[str, Callable]] = None):
        self.callback_registry = callback_registry or {}
        self.session_manager = MCPSessionManager()
        self.server = None
        self.server_thread = None
        self.port = None
        self.is_running = False
        
        # Default command handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default MCP command handlers"""
        self.callback_registry.update({
            'ping': self._handle_ping,
            'get_session_info': self._handle_get_session_info,
            'get_performance': self._handle_get_performance
        })
    
    def register_handler(self, action: str, handler: Callable):
        """Register custom command handler"""
        self.callback_registry[action] = handler
    
    def _handle_ping(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping command"""
        return {'status': 'success', 'message': 'pong', 'session_id': self.session_manager.session_id}
    
    def _handle_get_session_info(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session info request"""
        return {'status': 'success', 'session_info': self.session_manager.get_session_info()}
    
    def _handle_get_performance(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance metrics request"""
        return {'status': 'success', 'performance': self.session_manager.get_session_info()}
    
    def start(self, preferred_port: int = 8765) -> bool:
        """Start MCP server with conflict resolution"""
        if self.is_running:
            return True
        
        try:
            # Check for existing servers
            existing = MCPNetworkManager.check_existing_servers()
            if existing and preferred_port in existing:
                # Try to reuse existing server
                if MCPNetworkManager.test_server_connection(preferred_port):
                    self.port = preferred_port
                    self.is_running = True
                    return True
            
            # Find available port
            self.port = MCPNetworkManager.find_available_port(preferred_port)
            
            # Create server with callback registry
            def handler_factory(*args, **kwargs):
                return MCPCommandHandler(self.callback_registry, *args, **kwargs)
            
            self.server = HTTPServer(('localhost', self.port), handler_factory)
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            return True
            
        except Exception as e:
            print(f"Failed to start MCP server: {e}")
            return False
    
    def _run_server(self):
        """Run server with error handling"""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"MCP server error: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop MCP server with cleanup"""
        if not self.is_running:
            return
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2)
            
            self.is_running = False
            
        except Exception as e:
            print(f"Error stopping MCP server: {e}")
    
    def send_command(self, action: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Send command to this server (for testing)"""
        if not self.is_running:
            return None
        
        try:
            command_data = {'action': action, **kwargs}
            response = requests.post(
                f'http://localhost:{self.port}',
                json=command_data,
                timeout=5
            )
            return response.json()
        except Exception as e:
            print(f"Command send error: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status information"""
        return {
            'running': self.is_running,
            'port': self.port,
            'session_info': self.session_manager.get_session_info() if self.is_running else None
        }

class MCPClient:
    """MCP client for external communication"""
    
    def __init__(self, server_port: int = 8765):
        self.server_port = server_port
        self.base_url = f"http://localhost:{server_port}"
    
    def send_command(self, action: str, timeout: int = 5, **kwargs) -> Optional[Dict[str, Any]]:
        """Send command to MCP server"""
        try:
            command_data = {'action': action, **kwargs}
            response = requests.post(self.base_url, json=command_data, timeout=timeout)
            return response.json()
        except Exception as e:
            print(f"MCP client error: {e}")
            return None
    
    def ping(self) -> bool:
        """Test connection to server"""
        response = self.send_command('ping')
        return response is not None and response.get('status') == 'success'
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get server session information"""
        response = self.send_command('get_session_info')
        return response.get('session_info') if response else None

# Factory functions for easy instantiation
def create_mcp_server(callback_registry: Optional[Dict[str, Callable]] = None) -> MCPServer:
    """Create MCP server instance"""
    return MCPServer(callback_registry)

def create_mcp_client(port: int = 8765) -> MCPClient:
    """Create MCP client instance"""
    return MCPClient(port)

if __name__ == "__main__":
    # Demo usage
    print("🔧 MCP TOOLS AND UTILITIES - ISOLATED MODULE TEST")
    print("=" * 50)
    
    # Test server creation and startup
    server = create_mcp_server()
    
    if server.start():
        print(f"✅ MCP server started on port {server.port}")
        
        # Test client connection
        client = create_mcp_client(server.port)
        
        if client.ping():
            print("✅ Client connection successful")
            
            # Get session info
            session_info = client.get_session_info()
            if session_info:
                print(f"✅ Session ID: {session_info['session_id'][:8]}...")
        
        server.stop()
        print("✅ Server stopped cleanly")
    else:
        print("❌ Failed to start server")