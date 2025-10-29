#!/usr/bin/env python3
"""
Simple MCP Client - Direct Connection Test
Connects to running MCP server, maintains connection, sends commands, analyzes UI
"""

import requests
import time
import json
from datetime import datetime

class SimpleMCPClient:
    def __init__(self, server_url="http://localhost:8765"):
        self.server_url = server_url
        self.session_id = datetime.now().strftime("%H%M%S")
        self.connected = False
        
    def connect(self):
        """Connect to MCP server and verify it's responding"""
        try:
            print(f"🔗 Connecting to MCP server at {self.server_url}")
            
            # Test health endpoint
            health_response = requests.get(f"{self.server_url}/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ MCP Server Health: {health_data.get('status', 'unknown')}")
                
                # Test commands endpoint  
                commands_response = requests.get(f"{self.server_url}/commands", timeout=5)
                if commands_response.status_code == 200:
                    commands_data = commands_response.json()
                    available_commands = commands_data.get('commands', [])
                    print(f"📋 Available Commands: {len(available_commands)}")
                    print(f"    {', '.join(available_commands[:5])}")
                    
                    self.connected = True
                    return True
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
    def send_command(self, command, reason="test", agent="SimpleMCPClient"):
        """Send command to MCP server"""
        if not self.connected:
            print("❌ Not connected to MCP server")
            return None
            
        try:
            command_data = {
                "command": command,
                "reason": reason,
                "agent": agent,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"📤 Sending command: {command} - {reason}")
            
            response = requests.post(
                f"{self.server_url}/status",  # Using status endpoint for command sending
                json=command_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Command sent successfully: {result.get('status', 'unknown')}")
                return result
            else:
                print(f"⚠️ Command response: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Command send failed: {e}")
            return None
            
    def get_status(self):
        """Get current MCP server status"""
        if not self.connected:
            return None
            
        try:
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ Status check failed: {e}")
            
        return None
        
    def run_ui_test_sequence(self):
        """Run sequence to test UI updates"""
        print("\n🎯 Starting UI Test Sequence")
        print("=" * 40)
        
        # 1. Send screenshot command
        print("\n📸 Step 1: Requesting screenshot")
        screenshot_result = self.send_command(
            "see",
            "capture_current_ui_state_for_analysis",
            "UITestClient"
        )
        
        if screenshot_result:
            print(f"    Screenshot result: {screenshot_result.get('message', 'No message')}")
        
        # Wait and check status
        time.sleep(1)
        status = self.get_status()
        if status:
            print(f"📊 Server Status: {status.get('session_id', 'unknown')}")
            connected_clients = status.get('connected_clients', 0)
            print(f"    Connected clients: {connected_clients}")
            
        # 2. Send UI interaction command  
        print("\n🖱️ Step 2: Requesting UI interaction")
        click_result = self.send_command(
            "click", 
            "test_generate_button_for_ui_update_validation",
            "UITestClient"
        )
        
        if click_result:
            print(f"    Click result: {click_result.get('message', 'No message')}")
            
        # 3. Send analysis command
        print("\n🧠 Step 3: Requesting UI analysis")  
        analysis_result = self.send_command(
            "screenshot_analysis",
            "analyze_mcp_ui_elements_and_command_display",
            "UITestClient"  
        )
        
        if analysis_result:
            print(f"    Analysis result: {analysis_result.get('message', 'No message')}")
            
        # Final status check
        time.sleep(1)
        final_status = self.get_status()
        if final_status:
            print(f"\n📈 Final Status Check:")
            print(f"    Session: {final_status.get('session_id', 'unknown')}")
            print(f"    Connected clients: {final_status.get('connected_clients', 0)}")
            command_history = final_status.get('command_history', [])
            if command_history:
                print(f"    Recent commands: {len(command_history)}")
                for cmd in command_history[-3:]:  # Show last 3
                    cmd_name = cmd.get('command', 'unknown')  
                    cmd_time = cmd.get('timestamp', '')[-8:] if cmd.get('timestamp') else ''
                    print(f"      • {cmd_name} at {cmd_time}")
                    
    def maintain_connection(self, duration=30):
        """Maintain connection and periodically check status"""
        print(f"\n⏰ Maintaining connection for {duration} seconds")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Check status every 5 seconds
                if int(time.time() - start_time) % 5 == 0:
                    status = self.get_status()
                    if status:
                        clients = status.get('connected_clients', 0)
                        print(f"🔄 Connection alive - {clients} clients connected")
                    else:
                        print("⚠️ Status check failed - connection may be lost")
                        break
                        
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n⏹️ Connection interrupted by user")
                break
                
        print("✅ Connection maintenance completed")

def main():
    print("🚀 Simple MCP Client - UI Validation Test")
    print("=" * 50)
    
    client = SimpleMCPClient()
    
    # Connect to server
    if not client.connect():
        print("❌ Failed to connect to MCP server")
        print("💡 Make sure the spaceship app is running with MCP server on port 8765")
        return
        
    print("✅ Connected successfully!")
    
    # Run UI test sequence
    client.run_ui_test_sequence()
    
    # Maintain connection briefly to observe any updates
    client.maintain_connection(15)
    
    print("\n🎉 MCP Client test completed successfully!")
    print("The app's UI should now show updated MCP status and command history")

if __name__ == "__main__":
    main()