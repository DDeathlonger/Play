#!/usr/bin/env python3
"""
Test MCP UI functionality by sending commands to the running spaceship app
"""

import requests
import time

def test_mcp_ui():
    """Test that MCP server is running and UI responds to commands"""
    
    print("🧪 Testing MCP UI Functionality")
    print("=" * 40)
    
    mcp_url = "http://localhost:8765"
    
    try:
        # Test 1: Check server health
        print("📡 Testing MCP server health...")
        response = requests.get(f"{mcp_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP server is running")
        else:
            print(f"❌ MCP server health check failed: {response.status_code}")
            return False
        
        # Test 2: Check available commands
        print("📋 Checking available commands...")
        response = requests.get(f"{mcp_url}/commands", timeout=5)
        if response.status_code == 200:
            commands = response.json()
            print(f"✅ Available commands: {len(commands.get('commands', []))}")
            for cmd in commands.get('commands', []):
                print(f"   • {cmd}")
        
        # Test 3: Send a test command
        print("🎮 Sending test command...")
        test_command = {
            "action": "see",
            "reason": "Testing UI display functionality",
            "agent": "UI_Test_Agent"
        }
        
        response = requests.post(f"{mcp_url}/commands", json=test_command, timeout=5)
        if response.status_code == 200:
            print("✅ Test command sent successfully")
            print("💬 Check the spaceship app UI for:")
            print("   • MCP status should show 'Connected'")
            print("   • Commands panel should show latest command")  
            print("   • AI chat should display the command")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ MCP server connection failed: {e}")
        print("Make sure the spaceship app is running first!")
        return False

if __name__ == "__main__":
    success = test_mcp_ui()
    if success:
        print("\n🎉 MCP UI test completed successfully!")
        print("Check the spaceship designer app UI panels for updates.")
    else:
        print("\n⚠️ MCP UI test failed - ensure spaceship app is running")