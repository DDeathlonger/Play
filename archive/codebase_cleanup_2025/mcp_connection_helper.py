#!/usr/bin/env python3
"""
MCP Server Connection Helper
Reliable connection to running spaceship app MCP server
"""

import requests
import time
import json
from datetime import datetime

class MCPConnection:
    """Helper class for connecting to MCP server"""
    
    def __init__(self, base_url="http://localhost:8765"):
        self.base_url = base_url
        self.connected = False
        self.last_status = None
        
    def wait_for_server(self, timeout=30, check_interval=1):
        """Wait for MCP server to become available"""
        print(f"🔄 Waiting for MCP server at {self.base_url}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    self.connected = True
                    print("✅ MCP server is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(f"⏳ Waiting... ({int(time.time() - start_time)}s)")
            time.sleep(check_interval)
        
        print(f"❌ Timeout waiting for MCP server ({timeout}s)")
        return False
    
    def get_health(self):
        """Get server health status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Health check error: {e}")
        return None
    
    def get_commands(self):
        """Get available commands"""
        try:
            response = requests.get(f"{self.base_url}/commands", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Commands error: {e}")
        return None
    
    def get_status(self):
        """Get server status"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.last_status = data
                return data
        except Exception as e:
            print(f"Status error: {e}")
        return None
    
    def send_command(self, command_data):
        """Send command to MCP server"""
        try:
            response = requests.post(
                f"{self.base_url}/commands", 
                json=command_data, 
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Command failed: {response.status_code}")
        except Exception as e:
            print(f"Command error: {e}")
        return None
    
    def test_full_connection(self):
        """Test all MCP server endpoints"""
        print("🧪 Testing Full MCP Connection")
        print("=" * 40)
        
        # Test health
        health = self.get_health()
        if health:
            print(f"✅ Health: {health.get('status', 'Unknown')}")
            print(f"   Uptime: {health.get('uptime', 'Unknown')}")
        else:
            print("❌ Health check failed")
            return False
        
        # Test commands
        commands = self.get_commands()
        if commands:
            cmd_list = commands.get('commands', [])
            print(f"✅ Commands: {len(cmd_list)} available")
            for cmd in cmd_list[:3]:
                print(f"   • {cmd}")
        else:
            print("❌ Commands check failed")
        
        # Test status  
        status = self.get_status()
        if status:
            print(f"✅ Status: Session {status.get('session_id', 'Unknown')}")
            print(f"   Clients: {len(status.get('connected_clients', {}))}")
            
            latest = status.get('latest_command')
            if latest:
                print(f"   Latest: {latest.get('command', 'None')}")
            else:
                print("   Latest: No commands yet")
        else:
            print("❌ Status check failed")
        
        # Test sending a command
        print("\n🎮 Testing command sending...")
        test_cmd = {
            "action": "see",
            "reason": "Testing MCP connection functionality",
            "agent": "Connection_Test_Agent",
            "timestamp": datetime.now().isoformat()
        }
        
        result = self.send_command(test_cmd)
        if result:
            print("✅ Command sent successfully!")
            print(f"   Response: {result}")
        else:
            print("❌ Command sending failed")
        
        print("\n🎉 Full MCP connection test complete!")
        return True

def main():
    """Main connection test"""
    conn = MCPConnection()
    
    # Wait for server to be ready
    if conn.wait_for_server(timeout=60):
        # Run full connection test
        conn.test_full_connection()
    else:
        print("❌ Could not connect to MCP server")
        print("Make sure spaceship app is running with MCP integration")

if __name__ == "__main__":
    main()