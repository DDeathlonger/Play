#!/usr/bin/env python3
"""
ASYNC MCP TOOLS - ENHANCED VERSION
Model Context Protocol with async startup, network readiness, and proper status monitoring
"""

import asyncio
import json
import time
import threading
import socket
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
from pathlib import Path
import uuid

class NetworkStatusMonitor:
    """Monitor network readiness and connection status"""
    
    def __init__(self):
        self.connection_history = []
        self.last_check_time = None
        self.is_monitoring = False
    
    async def wait_for_network_ready(self, timeout: float = 30.0) -> bool:
        """Wait for network to be ready with timeout"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            if await self.check_network_connectivity():
                return True
            await asyncio.sleep(0.5)
        
        return False
    
    async def check_network_connectivity(self) -> bool:
        """Check if network is available"""
        try:
            # Quick connectivity check
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 80))  # Local connectivity
            sock.close()
            
            self.last_check_time = time.time()
            success = result == 0 or result == 10061  # Connection refused is OK for localhost
            
            self.connection_history.append({
                'timestamp': self.last_check_time,
                'success': success,
                'result_code': result
            })
            
            # Keep only recent history
            if len(self.connection_history) > 50:
                self.connection_history = self.connection_history[-25:]
            
            return success
            
        except Exception as e:
            print(f"Network connectivity check failed: {e}")
            return False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get network connection statistics"""
        if not self.connection_history:
            return {'status': 'no_data', 'success_rate': 0.0}
        
        recent_checks = self.connection_history[-10:] if len(self.connection_history) >= 10 else self.connection_history
        successful = sum(1 for check in recent_checks if check['success'])
        success_rate = successful / len(recent_checks)
        
        return {
            'status': 'healthy' if success_rate > 0.8 else 'degraded' if success_rate > 0.3 else 'poor',
            'success_rate': success_rate,
            'total_checks': len(self.connection_history),
            'recent_successful': successful,
            'last_check': self.last_check_time
        }

class AsyncMCPServer:
    """Enhanced MCP Server with async startup and network readiness"""
    
    def __init__(self, callback_registry: Optional[Dict[str, Callable]] = None):
        self.callback_registry = callback_registry or {}
        self.session_manager = MCPSessionManager()
        self.network_monitor = NetworkStatusMonitor()
        self.server = None
        self.server_thread = None
        self.port = None
        self.is_running = False
        self.startup_complete = asyncio.Event()
        self.shutdown_event = asyncio.Event()
        
        # Enhanced status tracking
        self.startup_time = None
        self.connection_count = 0
        self.last_activity = None
        
        # Register default handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register enhanced default command handlers"""
        self.callback_registry.update({
            'ping': self._handle_ping,
            'get_session_info': self._handle_get_session_info,
            'get_performance': self._handle_get_performance,
            'get_network_status': self._handle_get_network_status,
            'health_check': self._handle_health_check
        })
    
    def _handle_ping(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced ping with network status"""
        self.last_activity = time.time()
        network_stats = self.network_monitor.get_connection_stats()
        
        return {
            'status': 'success',
            'message': 'pong',
            'session_id': self.session_manager.session_id,
            'server_uptime': time.time() - self.startup_time if self.startup_time else 0,
            'network_status': network_stats['status']
        }
    
    def _handle_get_session_info(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced session info with performance metrics"""
        return {
            'status': 'success',
            'session_info': self.session_manager.get_session_info(),
            'server_stats': {
                'uptime': time.time() - self.startup_time if self.startup_time else 0,
                'connection_count': self.connection_count,
                'last_activity': self.last_activity
            }
        }
    
    def _handle_get_performance(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Performance metrics with network status"""
        return {
            'status': 'success',
            'performance': self.session_manager.get_session_info(),
            'network_performance': self.network_monitor.get_connection_stats()
        }
    
    def _handle_get_network_status(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detailed network status information"""
        return {
            'status': 'success',
            'network_status': self.network_monitor.get_connection_stats(),
            'server_ready': self.is_running and self.startup_complete.is_set()
        }
    
    def _handle_health_check(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive health check"""
        network_stats = self.network_monitor.get_connection_stats()
        
        health_status = 'healthy'
        if not self.is_running:
            health_status = 'down'
        elif network_stats['success_rate'] < 0.5:
            health_status = 'degraded'
        elif not self.startup_complete.is_set():
            health_status = 'starting'
        
        return {
            'status': 'success',
            'health': health_status,
            'uptime': time.time() - self.startup_time if self.startup_time else 0,
            'network': network_stats,
            'ready': self.startup_complete.is_set()
        }
    
    async def start_async(self, preferred_port: int = 8765, wait_timeout: float = 30.0) -> bool:
        """Start server with async network readiness checking"""
        if self.is_running:
            return True
        
        try:
            print(f"🚀 Starting async MCP server on port {preferred_port}...")
            
            # Wait for network readiness
            print("🔍 Checking network connectivity...")
            network_ready = await self.network_monitor.wait_for_network_ready(timeout=10.0)
            if not network_ready:
                print("⚠️ Network not fully ready, but continuing...")
            
            # Find available port
            self.port = await self._find_available_port_async(preferred_port)
            print(f"📡 Using port {self.port}")
            
            # Start server
            success = await self._start_server_async()
            
            if success:
                # Wait for server to be fully ready
                await self._wait_for_server_ready(timeout=wait_timeout)
                self.startup_time = time.time()
                self.startup_complete.set()
                print(f"✅ MCP server ready on http://localhost:{self.port}")
                return True
            else:
                print("❌ Failed to start MCP server")
                return False
        
        except Exception as e:
            print(f"❌ MCP server startup error: {e}")
            return False
    
    async def _find_available_port_async(self, preferred_port: int) -> int:
        """Find available port asynchronously"""
        for port in range(preferred_port, preferred_port + 100):
            if await self._is_port_available_async(port):
                return port
        
        raise RuntimeError(f"No available ports found starting from {preferred_port}")
    
    async def _is_port_available_async(self, port: int) -> bool:
        """Check if port is available asynchronously"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # Port is available if connection fails
        except Exception:
            return True
    
    async def _start_server_async(self) -> bool:
        """Start the HTTP server in a thread"""
        try:
            # Create server
            def handler_factory(*args, **kwargs):
                return EnhancedMCPCommandHandler(self.callback_registry, self, *args, **kwargs)
            
            self.server = HTTPServer(('localhost', self.port), handler_factory)
            
            # Start in thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            return True
        
        except Exception as e:
            print(f"Server startup error: {e}")
            return False
    
    async def _wait_for_server_ready(self, timeout: float = 30.0) -> bool:
        """Wait for server to be fully ready to accept connections"""
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                # Test connection to our own server
                response = requests.get(f'http://localhost:{self.port}', timeout=1)
                if response.status_code in [200, 404, 405]:  # Server is responding
                    return True
            except requests.exceptions.RequestException:
                pass
            
            await asyncio.sleep(0.2)
        
        return False
    
    def _run_server(self):
        """Run server with enhanced error handling"""
        try:
            print(f"🌐 HTTP server listening on http://localhost:{self.port}")
            self.server.serve_forever()
        except Exception as e:
            print(f"❌ MCP server error: {e}")
            self.is_running = False
            self.startup_complete.clear()
    
    async def stop_async(self):
        """Stop server asynchronously with proper cleanup"""
        if not self.is_running:
            return
        
        print("🛑 Stopping MCP server...")
        
        try:
            # Signal shutdown
            self.shutdown_event.set()
            
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.server_thread and self.server_thread.is_alive():
                # Wait for thread to finish
                await asyncio.to_thread(self.server_thread.join, timeout=3)
            
            self.is_running = False
            self.startup_complete.clear()
            print("✅ MCP server stopped successfully")
        
        except Exception as e:
            print(f"⚠️ Error stopping MCP server: {e}")
    
    def register_handler(self, action: str, handler: Callable):
        """Register custom command handler"""
        self.callback_registry[action] = handler
    
    async def send_command_async(self, action: str, timeout: float = 5.0, **kwargs) -> Optional[Dict[str, Any]]:
        """Send command to server asynchronously"""
        if not self.is_running or not self.startup_complete.is_set():
            return None
        
        try:
            command_data = {'action': action, **kwargs}
            
            # Use asyncio for the HTTP request
            response = await asyncio.to_thread(
                requests.post,
                f'http://localhost:{self.port}',
                json=command_data,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        
        except Exception as e:
            print(f"Command send error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get comprehensive server status"""
        return {
            'running': self.is_running,
            'ready': self.startup_complete.is_set(),
            'port': self.port,
            'uptime': time.time() - self.startup_time if self.startup_time else 0,
            'connection_count': self.connection_count,
            'last_activity': self.last_activity,
            'network_status': self.network_monitor.get_connection_stats()
        }

class EnhancedMCPCommandHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler with better logging and connection tracking"""
    
    def __init__(self, callback_registry: Dict[str, Callable], server_instance: AsyncMCPServer, *args, **kwargs):
        self.callback_registry = callback_registry
        self.server_instance = server_instance
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests with enhanced tracking"""
        self.server_instance.connection_count += 1
        self.server_instance.last_activity = time.time()
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            command_data = json.loads(post_data.decode('utf-8'))
            
            # Route command to handler
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
        self.server_instance.connection_count += 1
        
        status = self.server_instance.get_server_status()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging (we have our own)"""
        pass

# Import required dependencies from original mcp_tools
from .mcp_tools import MCPSessionManager, MCPClient, MCPNetworkManager

# Async convenience functions
async def start_mcp_server_async(port: int = 8765, timeout: float = 30.0) -> AsyncMCPServer:
    """Start MCP server and wait for readiness"""
    server = AsyncMCPServer()
    success = await server.start_async(port, timeout)
    
    if not success:
        raise RuntimeError(f"Failed to start MCP server on port {port}")
    
    return server

async def test_mcp_connection_async(port: int = 8765, timeout: float = 5.0) -> bool:
    """Test if MCP server is responding"""
    try:
        response = await asyncio.to_thread(
            requests.get,
            f'http://localhost:{port}',
            timeout=timeout
        )
        return response.status_code == 200
    except Exception:
        return False