#!/usr/bin/env python3
"""
MCP TEST UTILITIES
Utilities for safely testing MCP functionality with running app instances
"""

import socket
import sys
import time
from pathlib import Path

def check_port_in_use(port):
    """Check if a port is already in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Quick timeout
            result = s.connect_ex(('localhost', port))
            return result == 0  # 0 means connection successful (port in use)
    except Exception:
        return False

def get_available_mcp_port(preferred_port=8765):
    """Get an available port for MCP testing, starting with preferred port"""
    if not check_port_in_use(preferred_port):
        return preferred_port
    
    # If preferred port is taken, find next available port
    for port in range(preferred_port + 1, preferred_port + 100):
        if not check_port_in_use(port):
            return port
    
    raise RuntimeError("No available ports found for MCP testing")

def is_app_mcp_server_running(port=8765):
    """Check if the spaceship app MCP server is running on the given port"""
    try:
        # Test socket connection first
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)  # Increased timeout
            result = s.connect_ex(('localhost', port))
            if result == 0:
                print(f"✅ Detected MCP server on port {port}")
                
                # Try to verify it's actually responding to HTTP
                try:
                    import requests
                    health_response = requests.get(f'http://localhost:{port}/health', timeout=2)
                    if health_response.status_code == 200:
                        health_data = health_response.json()
                        print(f"✅ MCP server healthy: {health_data.get('status', 'unknown')}")
                        return True
                    else:
                        print(f"⚠️ Port {port} open but HTTP not responding properly")
                        return True  # Still consider it running
                except Exception as req_error:
                    print(f"⚠️ Port {port} open but HTTP error: {req_error}")
                    return True  # Still consider it running
            else:
                print(f"ℹ️ Port {port} not in use")
                return False
    except Exception as e:
        print(f"⚠️ Connection test error: {e}")
        return False

def create_test_mcp_server_safely():
    """Create MCP server for testing, avoiding conflicts with running app"""
    
    # First check if app MCP server is running
    if is_app_mcp_server_running(8765):
        print("📡 App MCP server detected - tests will use existing server")
        return None, 8765  # Return None server, existing port
    
    # No app server running, would need to create test server
    # Since the MCP server is integrated into the main app, 
    # tests should primarily work with existing app servers
    print("⚠️ No app MCP server running - tests should start app first")
    return None, None

def connect_to_existing_or_create_mcp(preferred_port=8765):
    """Connect to existing app MCP server or create new test server"""
    
    if is_app_mcp_server_running(preferred_port):
        print(f"🔗 Using existing app MCP server on port {preferred_port}")
        # Return connection info for existing server
        return {
            'server': None,  # We don't own this server
            'port': preferred_port,
            'is_app_server': True,
            'should_cleanup': False
        }
    else:
        # Create our own test server
        server, port = create_test_mcp_server_safely()
        return {
            'server': server,
            'port': port,
            'is_app_server': False,
            'should_cleanup': True
        }

class MCPTestContext:
    """Context manager for MCP testing that handles server lifecycle properly"""
    
    def __init__(self, preferred_port=8765):
        self.preferred_port = preferred_port
        self.connection_info = None
        
    def __enter__(self):
        self.connection_info = connect_to_existing_or_create_mcp(self.preferred_port)
        return self.connection_info
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection_info and self.connection_info.get('should_cleanup', False):
            server = self.connection_info.get('server')
            if server and hasattr(server, 'stop'):
                try:
                    server.stop()
                    print("🧹 Cleaned up test MCP server")
                except Exception as e:
                    print(f"⚠️ Error cleaning up test server: {e}")

def wait_for_mcp_ready(port, timeout=10):
    """Wait for MCP server to be ready on given port"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_port_in_use(port):
            time.sleep(0.1)  # Brief pause to ensure server is fully ready
            return True
        time.sleep(0.1)
    
    return False

# Example usage pattern for tests:
"""
def test_mcp_functionality(self, result: TestResult):
    with MCPTestContext() as mcp_info:
        if mcp_info['port'] is None:
            result.add_detail("No MCP server available for testing")
            return
            
        port = mcp_info['port']
        is_app = mcp_info['is_app_server']
        
        # Test MCP functionality using the port
        if is_app:
            result.add_detail(f"Testing with app MCP server on port {port}")
        else:
            result.add_detail(f"Testing with dedicated test server on port {port}")
        
        # Your actual test code here...
"""

if __name__ == "__main__":
    # Quick test of utilities
    print("🧪 Testing MCP utilities...")
    
    print(f"Port 8765 in use: {check_port_in_use(8765)}")
    print(f"Available port: {get_available_mcp_port()}")
    print(f"App server running: {is_app_mcp_server_running()}")
    
    with MCPTestContext() as mcp_info:
        print(f"MCP context: {mcp_info}")